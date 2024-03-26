import asyncio
import queue
from argparse import ArgumentParser
from asyncio import create_task, StreamReader, StreamWriter
from dataclasses import dataclass, field
from queue import SimpleQueue
from tempfile import TemporaryDirectory

import zmq
import zmq.asyncio

from .connection import guacd_route_connection
from .constants import (
    GuacClientLogLevel, GUACD_DEFAULT_BIND_HOST, GUACD_DEFAULT_BIND_PORT,
    GUACD_ARG_TO_LOG_LEVEL, GUACD_DEFAULT_LOG_LEVEL
)
from .log import guacd_log
from .proc import GuacClientLog, GuacdProcMap
from .utils.ipc_addr import new_ipc_addr


DATA_CHUNK_SIZE = 2 ** 13  # 8kB data chunk


@dataclass
class ZmqSocketToTCP:
    """ZeroMQ socket with handler to write out to TCP stream"""
    ctx: zmq.Context
    tcp_writer: StreamWriter
    tmp_dir: str
    zmq_type: zmq.SocketType

    address: str = None
    socket: zmq.Socket = None
    task: asyncio.Task = None

    def __post_init__(self):
        self.address = new_ipc_addr(self.tmp_dir)
        self.socket = self.ctx.socket(self.zmq_type)
        self.socket.bind(self.address)
        # self.task = create_task(asyncio.to_thread(self.zmq_read_handler))
        self.task = create_task(self.tcp_write_handler())

    async def tcp_write_handler(self):
        while True:
            try:
                data = self.socket.recv(zmq.NOBLOCK)
            except zmq.ZMQError:
                data = await asyncio.to_thread(self.socket.recv)
            self.tcp_writer.write(data)
            await self.tcp_writer.drain()


@dataclass
class UserConnection:
    # External TCP connection reader and writer
    tcp_reader: StreamReader
    tcp_writer: StreamWriter
    ctx: zmq.Context
    tmp_dir: str

    # thread-safe queues
    tcp_write_queue: SimpleQueue = field(default_factory=SimpleQueue)

    # Socket pointer and event for switching TCP read handler to new ZeroMQ socket
    active_zmq_socket: zmq.Socket = None

    # Internal ZeroMQ socket data used for parsing connection id / protocol when the connection starts
    zmq_parse_id: ZmqSocketToTCP = None

    # Internal ZeroMQ socket data used for handling the user connection
    zmq_user_handler: ZmqSocketToTCP = None

    # Asyncio task for transferring data from external tcp socket to active ZeroMQ socket
    tcp_read_task: asyncio.Task = None

    def __post_init__(self):
        # Start parse id socket immediately for parsing connection id / protocol
        self.zmq_parse_id = ZmqSocketToTCP(self.ctx, self.tcp_writer, self.tmp_dir, zmq.CHANNEL)
        self.zmq_user_handler = ZmqSocketToTCP(self.ctx, self.tcp_writer, self.tmp_dir, zmq.CHANNEL)
        self.active_zmq_socket = self.zmq_parse_id.socket
        self.tcp_read_task = create_task(self.tcp_read_handler())
        # self.tcp_write_task = create_task(self.tcp_write_handler())

    def activate_user_handler(self):
        self.active_zmq_socket = self.zmq_user_handler.socket

    def close(self):
        tasks = [self.tcp_read_task, self.zmq_parse_id.task, self.zmq_user_handler.task]
        for task in tasks:
            if task and not task.done():
                task.cancel()

    async def tcp_read_handler(self):
        """Read data chunk from tcp socket and write to ZeroMQ socket

        :param debug:
            Keep last messages
        """

        while True:
            data = await self.tcp_reader.read(DATA_CHUNK_SIZE)
            try:
                self.active_zmq_socket.send(data, flags=zmq.NOBLOCK)
            except zmq.ZMQError:
                await asyncio.to_thread(self.active_zmq_socket.send, data)

    async def tcp_write_handler(self):
        while True:
            try:
                data = self.tcp_write_queue.get_nowait()
            except queue.Empty:
                data = await asyncio.to_thread(self.tcp_write_queue.get)
            self.tcp_writer.write(data)
            await self.tcp_writer.drain()


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
        with zmq.Context() as ctx, TemporaryDirectory(dir=self.server_tmp_dir) as tmp_dir:
            user_connection = UserConnection(tcp_reader, tcp_writer, ctx, tmp_dir)
            if await guacd_route_connection(self.proc_map, user_connection) == 0:
                print('User connection completed successfully')
            else:
                print('User connection was unsuccessful')

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
    parser.add_argument(
        '-L', '--log-level', default=GUACD_DEFAULT_LOG_LEVEL.name.split('_')[-1].lower(),
        choices=GUACD_ARG_TO_LOG_LEVEL
    )
    ns = parser.parse_args()
    GuacClientLog.max_log_level = GUACD_ARG_TO_LOG_LEVEL[ns.log_level]

    # Run asyncio TCP server
    try:
        asyncio.run(run_server(ns.bind_host, ns.bind_port))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
