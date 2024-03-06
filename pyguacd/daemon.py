import asyncio
from argparse import ArgumentParser
from asyncio import create_task, StreamReader, StreamWriter, Task
from dataclasses import dataclass, field
from tempfile import TemporaryDirectory
from typing import Iterable, List, Optional

import zmq
import zmq.asyncio

from .connection import guacd_route_connection
from .constants import GuacClientLogLevel, GUACD_DEFAULT_BIND_HOST, GUACD_DEFAULT_BIND_PORT
from .log import guacd_log
from .proc import GuacdProcMap
from .utils.ipc_addr import new_ipc_addr
from .utils.zmq_monitor import check_zmq_monitor_events


DATA_CHUNK_SIZE = 2 ** 10  # 1kB data chunk


@dataclass
class UserConnection:
    # External TCP connection reader and writer
    tcp_reader: StreamReader
    tcp_writer: StreamWriter
    ctx: zmq.asyncio.Context
    tmp_dir: str

    # Internal ZeroMQ socket data used for parsing connection id / protocol when the connection starts
    parse_id_addr: Optional[str] = None
    parse_id_socket: Optional[zmq.asyncio.Socket] = None
    parse_id_monitor: Optional[zmq.asyncio.Socket] = None
    parse_id_input: List = field(default_factory=list)
    parse_id_output: List = field(default_factory=list)

    # Internal ZeroMQ socket data used for handling the user connection
    handler_addr: Optional[str] = None
    handler_socket: Optional[zmq.asyncio.Socket] = None
    handler_monitor: Optional[zmq.asyncio.Socket] = None

    # Asyncio tasks for transferring data between external tcp socket and internal ZeroMQ sockets
    tcp_to_zmq_task: Optional[asyncio.Task] = None
    zmq_to_tcp_task: Optional[asyncio.Task] = None

    def __post_init__(self):
        # Start parse id socket immediately for parsing connection id / protocol
        self.parse_id_socket = self.ctx.socket(zmq.PAIR)
        self.parse_id_addr = new_ipc_addr(self.tmp_dir)
        self.parse_id_socket.bind(self.parse_id_addr)
        self.parse_id_monitor = self.parse_id_socket.get_monitor_socket()

        # Start handlers for parse id socket
        self.tcp_to_zmq_task = create_task(
            handle_tcp_to_zmq(self.tcp_reader, self.parse_id_socket, self.parse_id_input)
        )
        self.zmq_to_tcp_task = create_task(
            handle_zmq_to_tcp(self.parse_id_socket, self.tcp_writer, self.parse_id_output)
        )

    def start_handler_socket(self):
        self.handler_socket = self.ctx.socket(zmq.PAIR)
        self.handler_addr = new_ipc_addr(self.tmp_dir)
        self.handler_socket.bind(self.handler_addr)
        self.handler_monitor = self.handler_socket.get_monitor_socket()

        # Start handlers for parse id socket
        self.tcp_to_zmq_task = create_task(
            handle_tcp_to_zmq(self.tcp_reader, self.handler_socket)
        )
        self.zmq_to_tcp_task = create_task(
            handle_zmq_to_tcp(self.handler_socket, self.tcp_writer)
        )


async def handle_tcp_to_zmq(tcp_reader: StreamReader, zmq_socket: zmq.asyncio.Socket, keep_last: Optional[List] = None):
    """Read data chunk from tcp socket and write to ZeroMQ socket

    :param tcp_reader:
        TCP connection read stream provided by asyncio.start_server()
    :param zmq_socket:
        ZeroMQ socket that will be routed in guacd_route_connection()
    :param keep_last:
        Keep last messages
    """

    keep = isinstance(keep_last, list)
    while True:
        data = await tcp_reader.read(DATA_CHUNK_SIZE)
        if keep:
            keep_last.append(data)

        if len(data) == 0:
            break

        await zmq_socket.send(data)


async def handle_zmq_to_tcp(zmq_socket: zmq.asyncio.Socket, tcp_writer: StreamWriter, keep_last: Optional[List] = None):
    """Read from ZeroMQ socket and write to TCP socket

    :param zmq_socket:
        ZeroMQ socket that will be routed in guacd_route_connection()
    :param tcp_writer:
        TCP connection write stream provided by asyncio.start_server()
    :param keep_last:
        Keep last messages
    """

    keep = isinstance(keep_last, list)
    while True:
        data = await zmq_socket.recv()
        if keep:
            keep_last.append(data)

        if len(data) == 0:
            break

        tcp_writer.write(data)
        await tcp_writer.drain()


async def monitor_zmq_socket(conn: UserConnection):
    """Wait for ZeroMQ socket to finish before canceling read and write handlers

    :param conn:
        Class with connection data and sockets
    """

    # These are the events that occur on successful connect and disconnect
    # Note that two event sequences with connect and disconnect occur on the same ZeroMQ socket as described below
    zmq_events = [zmq.Event.ACCEPTED, zmq.Event.HANDSHAKE_SUCCEEDED, zmq.Event.DISCONNECTED]

    # Wait for connect and disconnect from libguac guac_parser_expect for parsing identifier
    if (error_msg := await check_zmq_monitor_events(conn.parse_id_monitor, zmq_events)) is None:
        for conn_task in [conn.zmq_to_tcp_task, conn.tcp_to_zmq_task]:
            if not conn_task.done():
                conn_task.cancel()

        print(f'Finished parsing id')
        conn.start_handler_socket()

        # Wait for connect and disconnect by libguac guac_user_handle_connection for handling remainder of connection
        if (error_msg := await check_zmq_monitor_events(conn.handler_monitor, zmq_events)) is not None:
            guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, 'Exiting prematurely during handling of connection')
    else:
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, 'Exiting prematurely during parsing of identifier')

    # Cancel connection handles to prevent waiting to read forever on closed socket
    for conn_task in [conn.zmq_to_tcp_task, conn.tcp_to_zmq_task]:
        if not conn_task.done():
            conn_task.cancel()
            await conn_task

    if error_msg is not None:
        raise ConnectionError(error_msg)


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
            # Create and bind Zero MQ socket. Two connections are made to this socket from libguac by:
            # - guac_parser_expect in connection.py for parsing identifier
            # - guac_user_handle_connection in proc.py for handling connection
            conn = UserConnection(tcp_reader, tcp_writer, ctx, tmp_dir)

            # Wait for ZeroMQ socket disconnect and guacd_route_connection to finish
            await asyncio.wait([
                create_task(monitor_zmq_socket(conn)),
                create_task(
                    guacd_route_connection(self.proc_map, conn.parse_id_addr, conn.handler_addr, conn.tmp_dir)
                ),
            ])


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
