import asyncio
from argparse import ArgumentParser
from asyncio import create_task, StreamReader, StreamWriter, Task
from tempfile import TemporaryDirectory
from typing import Iterable

import zmq
import zmq.asyncio

from .connection import guacd_route_connection
from .constants import GuacClientLogLevel, GUACD_DEFAULT_BIND_HOST, GUACD_DEFAULT_BIND_PORT
from .log import guacd_log
from .proc import GuacdProcMap
from .utils.ipc_addr import new_ipc_addr
from .utils.zmq_monitor import check_zmq_monitor_events


DATA_CHUNK_SIZE = 2 ** 10  # 1kB data chunk


async def handle_tcp_to_zmq(tcp_reader: StreamReader, zmq_socket: zmq.asyncio.Socket):
    """Read data chunk from tcp socket and write to ZeroMQ socket

    :param tcp_reader:
        TCP connection read stream provided by asyncio.start_server()
    :param zmq_socket:
        ZeroMQ socket that will be routed in guacd_route_connection()
    """

    while True:
        data = await tcp_reader.read(DATA_CHUNK_SIZE)
        if len(data) == 0:
            break

        await zmq_socket.send(data)


async def handle_zmq_to_tcp(zmq_socket: zmq.asyncio.Socket, tcp_writer: StreamWriter):
    """Read from ZeroMQ socket and write to TCP socket

    :param zmq_socket:
        ZeroMQ socket that will be routed in guacd_route_connection()
    :param tcp_writer:
        TCP connection write stream provided by asyncio.start_server()
    """

    while True:
        data = await zmq_socket.recv()
        if len(data) == 0:
            break

        tcp_writer.write(data)
        await tcp_writer.drain()


async def monitor_zmq_socket(zmq_monitor_socket: zmq.asyncio.Socket, connection_tasks: Iterable[Task]):
    """Wait for ZeroMQ socket to finish before canceling read and write handlers

    :param zmq_monitor_socket:
        ZeroMQ socket provided by get_monitor_socket method of another ZeroMQ Socket object
    :param connection_tasks:
        Iterable of connection tasks to cancel after ZeroMQ socket disconnect.
        The connection tasks are the read and write handlers.
    """

    # These are the events that occur on successful connect and disconnect
    # Note that two event sequences with connect and disconnect occur on the same ZeroMQ socket as described below
    zmq_events = [zmq.Event.ACCEPTED, zmq.Event.HANDSHAKE_SUCCEEDED, zmq.Event.DISCONNECTED]

    # Wait for connect and disconnect from libguac guac_parser_expect for parsing identifier
    if (error_msg := await check_zmq_monitor_events(zmq_monitor_socket, zmq_events)) is None:

        # Wait for connect and disconnect by libguac guac_user_handle_connection for handling remainder of connection
        if (error_msg := await check_zmq_monitor_events(zmq_monitor_socket, zmq_events)) is not None:
            guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, 'Exiting prematurely during handling of connection')

    else:
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, 'Exiting prematurely during parsing of identifier')

    # Cancel connection handles to prevent waiting to read forever on closed socket
    for conn_task in connection_tasks:
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
            zmq_user_socket = ctx.socket(zmq.PAIR)
            zmq_user_addr = new_ipc_addr(tmp_dir)
            zmq_user_socket.bind(zmq_user_addr)

            # Create monitor socket for the above user socket
            zmq_user_monitor = zmq_user_socket.get_monitor_socket()

            # Tasks used to proxy TCP connection to ZeroMQ socket
            connection_tasks = [
                create_task(handle_zmq_to_tcp(zmq_user_socket, tcp_writer)),
                create_task(handle_tcp_to_zmq(tcp_reader, zmq_user_socket)),
            ]

            # Wait for ZeroMQ socket disconnect and guacd_route_connection to finish
            await asyncio.wait([
                create_task(monitor_zmq_socket(zmq_user_monitor, connection_tasks)),
                create_task(guacd_route_connection(self.proc_map, zmq_user_addr, zmq_user_addr, tmp_dir)),
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
