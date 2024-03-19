import asyncio
from argparse import ArgumentParser
from asyncio import create_task, StreamReader, StreamWriter, Task
from dataclasses import dataclass, field
from tempfile import TemporaryDirectory
from time import clock_gettime_ns, CLOCK_MONOTONIC
from typing import Iterable, List, Optional

import zmq
import zmq.asyncio

from .connection import guacd_route_connection
from .constants import GuacClientLogLevel, GUACD_DEFAULT_BIND_HOST, GUACD_DEFAULT_BIND_PORT
from .log import guacd_log
from .proc import GuacdProcMap
from .utils.ipc_addr import new_ipc_addr
from .utils.zmq_monitor import check_zmq_monitor_events


DATA_CHUNK_SIZE = 2 ** 13  # 8kB data chunk


@dataclass
class ZmqSocketToTCP:
    """ZeroMQ socket with handler to write out to TCP stream"""
    ctx: zmq.asyncio.Context
    tcp_writer: StreamWriter
    tmp_dir: str
    zmq_recv_time: asyncio.Queue
    zmq_libguac_send_time: asyncio.Queue

    address: str = None
    guac_mon_address: str = None
    guac_mon_socket: zmq.asyncio.Socket = None
    monitor: zmq.asyncio.Socket = None
    socket: zmq.asyncio.Socket = None
    task: asyncio.Task = None
    zmq_guac_monitor_task: asyncio.Task = None

    def __post_init__(self):
        self.address = new_ipc_addr(self.tmp_dir)
        self.socket = self.ctx.socket(zmq.PAIR)
        self.socket.bind(self.address)
        self.monitor = self.socket.get_monitor_socket()
        self.guac_mon_address = f'{self.address}-monitor'
        self.guac_mon_socket = self.ctx.socket(zmq.PAIR)
        self.guac_mon_socket.bind(self.guac_mon_address)
        self.task = create_task(self.tcp_write_handler())
        self.zmq_guac_monitor_task = create_task(self.zmq_guac_monitor_handler())

    async def monitor_connection(self):
        # These are the events that occur on successful connect and disconnect
        zmq_events = [zmq.Event.ACCEPTED, zmq.Event.HANDSHAKE_SUCCEEDED, zmq.Event.DISCONNECTED]

        # Wait for connect and disconnect
        if (error_msg := await check_zmq_monitor_events(self.monitor, zmq_events)) is not None:
            guacd_log(
                GuacClientLogLevel.GUAC_LOG_ERROR, f'Exiting prematurely during handling of connection: {error_msg}'
            )

    async def tcp_write_handler(self):
        while True:
            msg_id_bytes, data = await self.socket.recv_multipart()
            recv_usec = clock_gettime_ns(CLOCK_MONOTONIC) // 1000
            msg_id = int.from_bytes(msg_id_bytes)
            if len(data) == 0:
                break

            self.tcp_writer.write(data)
            await self.zmq_recv_time.put((msg_id, recv_usec, len(data)))
            # print(f'**** Received msg id "{msg_id}"')
            await self.tcp_writer.drain()

    async def zmq_guac_monitor_handler(self):
        while True:
            (
                msg_id_bytes, sec_bytes, nsec_bytes, data_size_bytes, pthread_id_bytes, send_recv
            ) = await self.guac_mon_socket.recv_multipart()
            msg_id = int.from_bytes(msg_id_bytes)
            usec = int.from_bytes(sec_bytes) * 1000000 + int.from_bytes(nsec_bytes) // 1000
            data_size = int.from_bytes(data_size_bytes)
            pthread_id = int.from_bytes(pthread_id_bytes, signed=False)
            if send_recv == b'SEND':
                await self.zmq_libguac_send_time.put((msg_id, usec, data_size, pthread_id))
                if (qsize := self.zmq_libguac_send_time.qsize()) > 1:
                    print(f'**** Waiting for {qsize} messages from libguac')
            elif send_recv == b'RECV':
                print(f'**** Received {data_size} bytes of msg id {msg_id} sent at {usec} usec')
            else:
                print(f'Received "{send_recv.decode()}" instead of "SEND" or "RECV" on ZeroMQ libguac monitor socket')


@dataclass
class UserConnection:
    # External TCP connection reader and writer
    tcp_reader: StreamReader
    tcp_writer: StreamWriter

    ctx: zmq.asyncio.Context
    tmp_dir: str

    # write_zmq_msg_id: int = 0

    # Socket pointer and event for switching TCP read handler to new ZeroMQ socket
    active_zmq_socket: Optional[zmq.asyncio.Socket] = None

    # Internal ZeroMQ socket data used for parsing connection id / protocol when the connection starts
    zmq_parse_id: ZmqSocketToTCP = None

    zmq_recv_time: asyncio.Queue = None
    zmq_libguac_send_time: asyncio.Queue = None

    # Internal ZeroMQ socket data used for handling the user connection
    zmq_user_handler: ZmqSocketToTCP = None

    # Asyncio task for transferring data from external tcp socket to active ZeroMQ socket
    tcp_to_zmq_task: Optional[asyncio.Task] = None

    # Asyncio task for monitoring the ZeroMQ user handler socket
    monitor_user_handler: Optional[asyncio.Task] = None

    def __post_init__(self):
        # Init queues
        self.zmq_recv_time = asyncio.Queue(1000)
        self.zmq_libguac_send_time = asyncio.Queue(1000)

        # Start parse id socket immediately for parsing connection id / protocol
        self.zmq_parse_id = ZmqSocketToTCP(
            self.ctx, self.tcp_writer, self.tmp_dir, self.zmq_recv_time, self.zmq_libguac_send_time
        )
        self.zmq_user_handler = ZmqSocketToTCP(
            self.ctx, self.tcp_writer, self.tmp_dir, self.zmq_recv_time, self.zmq_libguac_send_time
        )
        self.active_zmq_socket = self.zmq_parse_id.socket
        self.tcp_to_zmq_task = create_task(self.handle_tcp_to_zmq())
        self.monitor_user_handler = create_task(self.zmq_user_handler.monitor_connection())
        self.monitor_recv_task = create_task(self.monitor_zmq_recv_time())

    def activate_user_handler(self):
        self.active_zmq_socket = self.zmq_user_handler.socket

    def close(self):
        tasks = [self.tcp_to_zmq_task, self.zmq_parse_id.task, self.monitor_user_handler, self.zmq_user_handler.task]
        for task in tasks:
            if task and not task.done():
                task.cancel()

    def start_socket(self, socket):
        socket = self.ctx.socket(zmq.PAIR)

    async def monitor_zmq_recv_time(self):
        while True:
            send_msg_id, send_usec, send_data_size, pthread_id = await self.zmq_libguac_send_time.get()
            recv_msg_id, recv_usec, recv_data_size = await self.zmq_recv_time.get()
            if send_msg_id != recv_msg_id:
                print(f'**** Received ZeroMQ messages out of order. Sent {send_msg_id} and received {recv_msg_id}')
            elif send_data_size != recv_data_size:
                print(f'**** Mismatch of sent and received data size. Sent {send_data_size} bytes and received {recv_data_size}')
            else:
                print(f'Received msg {send_msg_id}, {send_data_size} bytes in {recv_usec - send_usec} usec on thread {pthread_id}')

    async def handle_tcp_to_zmq(self):
        """Read data chunk from tcp socket and write to ZeroMQ socket

        :param debug:
            Keep last messages
        """

        while True:
            data = await self.tcp_reader.read(DATA_CHUNK_SIZE)
            if len(data) == 0:
                break

            await self.active_zmq_socket.send(data)
            # self.write_zmq_msg_id += 1
            # await self.active_zmq_socket.send_multipart(
            #     self.write_zmq_msg_id.to_bytes(4), data
            # )


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
            user_connection = UserConnection(tcp_reader, tcp_writer, ctx, tmp_dir)
            if await guacd_route_connection(self.proc_map, user_connection) == 0:
                await user_connection.monitor_user_handler

            # Clean up tasks
            user_connection.close()


async def run_server(bind_host: str, bind_port: int):
    """Launch asyncio TCP server on given host and port

    :param bind_host: host used to bind
    :param bind_port: port used to bind
    """

    handler = TcpHandler()
    server = await asyncio.start_server(handler.handle, bind_host, bind_port)

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
    handler.cleanup()


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
