import aiomonitor
import asyncio
import click
import os
from aiomonitor.termui.commands import auto_async_command_done
from argparse import ArgumentParser
from asyncio import create_task, StreamReader, StreamWriter, Task
from dataclasses import dataclass, field
from tempfile import TemporaryDirectory
from time import clock_gettime, clock_gettime_ns, CLOCK_MONOTONIC
from typing import Dict, Iterable, List, Optional

import zmq
import zmq.asyncio
from prompt_toolkit import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.shortcuts import ProgressBar, ProgressBarCounter

from .connection import guacd_route_connection
from .constants import DEBUG_READ_TIMESTAMP, GuacClientLogLevel, GUACD_DEFAULT_BIND_HOST, GUACD_DEFAULT_BIND_PORT
from .log import guacd_log
from .proc import GuacdProcMap
from .utils.ipc_addr import new_ipc_addr
from .utils.zmq_monitor import check_zmq_monitor_events


DATA_CHUNK_SIZE = 2 ** 15  # 32kB data chunk
NSEC_PER_SEC = 10 ** 9


@dataclass
class ZmqSocketToTCP:
    """ZeroMQ socket with handler to write out to TCP stream"""
    ctx: zmq.asyncio.Context
    tcp_write_queue: asyncio.Queue
    tcp_read_timer_queue: asyncio.Queue
    tmp_dir: str

    address: str = None
    monitor: zmq.asyncio.Socket = None
    socket: zmq.asyncio.Socket = None
    start_MBs_usec: int = 0
    task: asyncio.Task = None
    total_size: int = 0

    def __post_init__(self):
        self.address = new_ipc_addr(self.tmp_dir)
        self.socket = self.ctx.socket(zmq.PAIR)
        self.socket.bind(self.address)
        self.monitor = self.socket.get_monitor_socket()
        self.task = create_task(self.zmq_read_handler())

    async def monitor_connection(self):
        # These are the events that occur on successful connect and disconnect
        zmq_events = [zmq.Event.ACCEPTED, zmq.Event.HANDSHAKE_SUCCEEDED, zmq.Event.DISCONNECTED]

        # Wait for connect and disconnect
        if (error_msg := await check_zmq_monitor_events(self.monitor, zmq_events)) is not None:
            guacd_log(
                GuacClientLogLevel.GUAC_LOG_ERROR, f'Exiting prematurely during handling of connection: {error_msg}'
            )

    async def zmq_read_handler(self):
        while True:
            new_transfer = False
            try:
                tv_sec, tv_nsec, *data_parts = await self.socket.recv_multipart(zmq.NOBLOCK)
            except zmq.ZMQError:
                new_transfer = True
                tv_sec, tv_nsec, *data_parts = await self.socket.recv_multipart()

            if len(data_parts) > 1:
               # print(f'Got data parts {data_parts}')
               # breakpoint()
               tv_after_sec, tv_after_nsec, _, read_size = data_parts
               tcp_read_usec, tcp_read_size = await self.tcp_read_timer_queue.get()
               zmq_before_read_usec = int.from_bytes(tv_sec, signed=True) * 1000000 + int.from_bytes(tv_nsec, signed=True) // 1000
               zmq_after_read_usec = int.from_bytes(tv_after_sec, signed=True) * 1000000 + int.from_bytes(tv_after_nsec, signed=True) // 1000
               libguac_read_us = f'{zmq_after_read_usec - zmq_before_read_usec} usec'
               total_read_us = f'{zmq_after_read_usec - tcp_read_usec} usec'
               zmq_read_size = int.from_bytes(read_size)
               mismatched = f'Mismatched {zmq_read_size}/' if tcp_read_size == zmq_read_size else 'Matched'
               print(f'{mismatched} {tcp_read_size} bytes of data read by libguac in {libguac_read_us}, total {total_read_us}')

            else:
                zmq_usec = int(clock_gettime_ns(CLOCK_MONOTONIC)) // 1000
                send_usec = int.from_bytes(tv_sec, signed=True) * 1000000 + int.from_bytes(tv_nsec, signed=True) // 1000
                data = data_parts[0]
                if new_transfer:
                    self.total_size = len(data)
                    self.start_MBs_usec = send_usec
                else:
                    self.total_size += len(data)

                #     start_MBs_usec = None
                # else:
                #     start_MBs_usec = self.start_MBs_usec

                await self.tcp_write_queue.put((self.start_MBs_usec, self.total_size, send_usec, zmq_usec, data))


@dataclass
class UserConnection:
    # External TCP connection reader and writer
    tcp_reader: StreamReader
    tcp_writer: StreamWriter
    ctx: zmq.asyncio.Context
    tmp_dir: str

    tcp_read_queue: asyncio.Queue = None
    tcp_read_timer_queue: asyncio.Queue = None
    tcp_write_queue: asyncio.Queue = None
    test_queue: asyncio.Queue = None

    # Socket pointer and event for switching TCP read handler to new ZeroMQ socket
    active_zmq_socket: Optional[zmq.asyncio.Socket] = None

    # Internal ZeroMQ socket data used for parsing connection id / protocol when the connection starts
    zmq_parse_id: ZmqSocketToTCP = None

    # Internal ZeroMQ socket data used for handling the user connection
    zmq_user_handler: ZmqSocketToTCP = None

    # Asyncio task for transferring data from external tcp socket to active ZeroMQ socket
    tcp_to_zmq_task: Optional[asyncio.Task] = None

    # Asyncio task for monitoring the ZeroMQ user handler socket
    monitor_user_handler: Optional[asyncio.Task] = None

    def __post_init__(self):
        # Init queues
        self.tcp_read_queue = asyncio.Queue(8)
        self.tcp_read_timer_queue = asyncio.Queue(8)
        self.tcp_write_queue = asyncio.Queue(8)
        self.test_queue = asyncio.Queue(8)

        # Start parse id socket immediately for parsing connection id / protocol
        self.zmq_parse_id = ZmqSocketToTCP(self.ctx, self.tcp_write_queue, self.tcp_read_timer_queue, self.tmp_dir)
        self.zmq_user_handler = ZmqSocketToTCP(self.ctx, self.tcp_write_queue, self.tcp_read_timer_queue, self.tmp_dir)
        self.tcp_write_task = create_task(self.tcp_write_handler())
        self.active_zmq_socket = self.zmq_parse_id.socket
        self.zmq_write_task = create_task(self.zmq_write_handler())
        self.tcp_read_task = create_task(self.tcp_read_handler())
        self.monitor_user_handler = create_task(self.zmq_user_handler.monitor_connection())

    def activate_user_handler(self):
        self.active_zmq_socket = self.zmq_user_handler.socket

    def close(self):
        tasks = [
            self.tcp_read_task, self.zmq_write_task,
            self.zmq_parse_id.task, self.monitor_user_handler,
            self.zmq_user_handler.task, self.tcp_write_task
        ]
        for task in tasks:
            if task and not task.done():
                task.cancel()

    def start_socket(self, socket):
        socket = self.ctx.socket(zmq.PAIR)

    async def tcp_write_handler(self):
        while True:
            start_MBs_usec, total_size, send_usec, zmq_usec, data = await self.tcp_write_queue.get()
            self.tcp_writer.write(data)
            await self.tcp_writer.drain()
            self.tcp_write_queue.task_done()
            tcp_write_usec = int(clock_gettime_ns(CLOCK_MONOTONIC)) // 1000
            zmq_out = f'ZMQ ({zmq_usec - send_usec} usec)'
            tcp_out = f'TCP ({tcp_write_usec - zmq_usec} usec)'
            total = f'total ({tcp_write_usec - send_usec} usec)'
            size_out = f'{total_size} bytes in {tcp_write_usec - start_MBs_usec} usec'

            if start_MBs_usec:
                throughput = total_size * 1000 / (tcp_write_usec - start_MBs_usec)
                throughput_out = f'; Output throughput: {throughput} KB/s'
            else:
                throughput_out = ''

            if total_size < 50:
                print(f'TCP output: "{str(data)}", {size_out}')
            else:
                print(f'Output latency: {zmq_out}, {tcp_out}, {total}; {size_out}{throughput_out}')

    async def tcp_read_handler(self):
        while True:
            data = await self.tcp_reader.read(DATA_CHUNK_SIZE)
            tcp_read_usec = int(clock_gettime_ns(CLOCK_MONOTONIC)) // 1000
            await self.tcp_read_queue.put(
                (tcp_read_usec, data)
            )
            await self.tcp_read_timer_queue.put(
                (tcp_read_usec, len(data))
            )

    async def zmq_write_handler(self):
        """Read data chunk from tcp socket and write to ZeroMQ socket

        :param debug:
            Keep last messages
        """

        while True:
            tcp_read_usec, data = await self.tcp_read_queue.get()
            queue_get_usec = int(clock_gettime_ns(CLOCK_MONOTONIC)) // 1000
            await self.active_zmq_socket.send(data)
            zmq_send_usec = int(clock_gettime_ns(CLOCK_MONOTONIC)) // 1000
            self.tcp_read_queue.task_done()
            print(f'tcp to queue: {queue_get_usec - tcp_read_usec}, queue to zmq: {zmq_send_usec - queue_get_usec} in: {data}')
            # if data.startswith(b'3.key,'):
            #     print(f'keypress: {data}')


class TcpHandler:
    """Class to keep state between TCP connections

    Primarily the data to keep between TCP connections is proc_map.

    In addition, there is a temp directory for secure storage of ZeroMQ socket file.
    Within this directory each connection has another nested temp directory for ZeroMQ socket files.
    There is a cleanup method for removing the top level temp directory and all contents.
    """

    def __init__(self):
        # Initialize temp directory for all TCP connections
        self._temporary_directory = TemporaryDirectory()
        self.server_tmp_dir = self._temporary_directory.name

        # The map of existing guacd client processes
        self.proc_map: GuacdProcMap = GuacdProcMap()
        self.user_connections: Dict[str, List[UserConnection]] = dict()

    def cleanup(self):
        # Cleanup temp directory and contents for all TCP connections
        self._temporary_directory.cleanup()

    async def handle(self, tcp_reader: StreamReader, tcp_writer: StreamWriter):
        """Callback for aysncio.start_server()

        This handles a TCP connection from connect to disconnect
        """

        # Two context manager variables:
        # - ZeroMQ context
        # - Temp directory for this connection within top level temp directory for server
        with zmq.asyncio.Context() as ctx, TemporaryDirectory(dir=self.server_tmp_dir) as tmp_dir:
            ctx.setsockopt(zmq.SNDBUF, 32768)
            ctx.setsockopt(zmq.SNDHWM, 2000)
            ctx.setsockopt(zmq.RCVBUF, 32768)
            ctx.setsockopt(zmq.RCVHWM, 2000)
            user_connection = UserConnection(tcp_reader, tcp_writer, ctx, tmp_dir)
            connection_id = await guacd_route_connection(self.proc_map, user_connection)
            if connection_id is not None:
                if connection_id not in self.user_connections:
                    self.user_connections[connection_id] = []
                conn_id_users = self.user_connections[connection_id]
                conn_id_users.append(user_connection)

                await user_connection.monitor_user_handler

                conn_id_users.remove(user_connection)
                if len(conn_id_users) == 0:
                    self.user_connections.pop(connection_id)

            # Clean up tasks
            user_connection.close()


@aiomonitor.monitor_cli.command(name="hello-async")
def do_async_hello(ctx: click.Context) -> None:
    """
    Command extension example (async)
    """

    @auto_async_command_done
    async def _do_async_hello(ctx: click.Context):
        tcp_handler = ctx.obj.console_locals['tcp_handler']
        connections = list(tcp_handler.user_connections.values())
        if len(connections) == 0:
            click.echo('There are no connections')
            return

        conn = connections[0][0]

        # Create custom key bindings first.
        kb = KeyBindings()
        cancel = [False]
        i = [0]

        @kb.add("a")
        def _(event):
            if conn.test_queue.full():
                print('Queue full.')
            else:
                i[0] += 1
                conn.test_queue.put_nowait(f'Item{i[0]}')
                print(f'Added "Item{i[0]}" to queue.')

        @kb.add("g")
        def _(event):
            if conn.test_queue.empty():
                print(f'Queue empty.')
            else:
                item = conn.test_queue.get_nowait()
                print(f'Got "{item}" from queue.')
                conn.test_queue.task_done()

        @kb.add("f")
        def _(event):
            print("You pressed `f`.")

        @kb.add("q")
        def _(event):
            "Quit by setting cancel flag."
            cancel[0] = True

        @kb.add("x")
        def _(event):
            "Quit by sending SIGINT to the main thread."
            os.kill(os.getpid(), signal.SIGINT)

        bottom_toolbar = HTML(
            ' <b>[f]</b> Print "f" <b>[q]</b> Abort  <b>[x]</b> Send Control-C.'
        )

        with ProgressBar(key_bindings=kb, bottom_toolbar=bottom_toolbar) as pb:
            read_counter = ProgressBarCounter(pb, label='TCP Read Queue', total=8)
            pb.counters.append(read_counter)
            write_counter = ProgressBarCounter(pb, label='TCP Write Queue', total=8)
            pb.counters.append(write_counter)
            sec_counter = ProgressBarCounter(pb, label='Seconds', total=60)
            pb.counters.append(sec_counter)
            test_counter = ProgressBarCounter(pb, label='Test Queue', total=8)
            pb.counters.append(test_counter)

            ms = 0
            while True:
                if cancel[0]:
                    break
                if ms == 0:
                    sec_counter.items_completed = (sec_counter.items_completed + 1) % 60
                read_counter.items_completed = conn.tcp_read_queue.qsize()
                write_counter.items_completed = conn.tcp_write_queue.qsize()
                test_counter.items_completed = conn.test_queue.qsize()
                pb.invalidate()

                await asyncio.sleep(.1)
                ms = (ms + 100) % 1000

    asyncio.create_task(_do_async_hello(ctx))


async def run_server(bind_host: str, bind_port: int):
    """Launch asyncio TCP server on given host and port

    :param bind_host: host used to bind
    :param bind_port: port used to bind
    """

    tcp_handler = TcpHandler()


    with aiomonitor.start_monitor(loop=asyncio.get_running_loop(), locals=locals()) as monitor:
        # monitor.console_locals["tcp_handler"] = tcp_handler

        server = await asyncio.start_server(tcp_handler.handle, bind_host, bind_port)

        if len(server.sockets) == 1:
            host, port = server.sockets[0].getsockname()
            print(f'Listening on host {host}, port {port}')
        else:
            addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
            print(f'Serving on {addrs}')

        async with server:
            try:
                await server.serve_forever()
            except asyncio.exceptions.CancelledError:
                print('Server closed')

    # Cleanup temp directory
    tcp_handler.cleanup()


def main():
    """Parse command line and other setup before launching asyncio TCP server"""

    # Parse args
    parser = ArgumentParser()
    parser.add_argument('-b', '--bind-host', default=GUACD_DEFAULT_BIND_HOST)
    parser.add_argument('-l', '--bind-port', type=int, default=GUACD_DEFAULT_BIND_PORT)
    ns = parser.parse_args()

    # Run asyncio TCP server
    asyncio.run(run_server(ns.bind_host, ns.bind_port))


if __name__ == '__main__':
    main()
