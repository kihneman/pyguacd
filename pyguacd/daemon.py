import asyncio
import os
from argparse import ArgumentParser
from asyncio import create_task, StreamReader, StreamWriter, Task
from typing import Iterable

import zmq
import zmq.asyncio

from .connection import guacd_route_connection
from .constants import GUACD_DEFAULT_BIND_HOST, GUACD_DEFAULT_BIND_PORT, GUACD_SOCKET_DIR
from .proc import GuacdProcMap
from .utils.ipc_addr import new_ipc_addr, remove_ipc_addr_file
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
    """Wait for ZeroMQ socket to disconnect before canceling read and write handlers

    :param zmq_monitor_socket:
        ZeroMQ socket provided by get_monitor_socket method of another ZeroMQ Socket object
    :param connection_tasks:
        Iterable of connection tasks to cancel after ZeroMQ socket disconnect.
        The connection tasks are the read and write handlers.
    """

    # These are the events that occur on successful connect and disconnect
    zmq_events = [zmq.Event.ACCEPTED, zmq.Event.HANDSHAKE_SUCCEEDED, zmq.Event.DISCONNECTED]

    # Wait for connect and disconnect by libguac guac_parser_expect
    if (error_msg := await check_zmq_monitor_events(zmq_monitor_socket, zmq_events)) is not None:
        raise ConnectionError(error_msg)

    # Wait for connect and disconnect by libguac guac_user_handle_connection
    if (error_msg := await check_zmq_monitor_events(zmq_monitor_socket, zmq_events)) is not None:
        raise ConnectionError(error_msg)

    # Cancel connection handles to prevent waiting to read forever on closed socket
    for conn_task in connection_tasks:
        if not conn_task.done():
            conn_task.cancel()
            await conn_task


class TcpHandler:
    """Class to keep state between TCP connections

    The only data to keep between TCP connections is proc_map.
    """

    def __init__(self):
        # The map of existing guacd client processes
        self.proc_map: GuacdProcMap = GuacdProcMap()

    async def handle(self, tcp_reader: StreamReader, tcp_writer: StreamWriter):
        """Callback for aysncio.start_server()

        This handles a TCP connection from connect to disconnect
        """

        with zmq.asyncio.Context() as ctx:
            # Create and bind Zero MQ socket to libguac functions guac_parser_expect and guac_user_handle_connection
            zmq_user_socket = ctx.socket(zmq.PAIR)
            zmq_user_addr = new_ipc_addr()
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
                create_task(guacd_route_connection(self.proc_map, zmq_user_addr)),
            ])

        # Clean up
        remove_ipc_addr_file(zmq_user_addr)


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


def main():
    """Parse command line and other setup before launching asyncio TCP server"""

    # Parse args
    parser = ArgumentParser()
    parser.add_argument('-b', '--bind-host', default=GUACD_DEFAULT_BIND_HOST)
    parser.add_argument('-l', '--bind-port', type=int, default=GUACD_DEFAULT_BIND_PORT)
    ns = parser.parse_args()

    # Make directory for ZeroMQ IPC address files
    os.makedirs(GUACD_SOCKET_DIR, exist_ok=True)

    # Run asyncio TCP server
    asyncio.run(run_server(ns.bind_host, ns.bind_port))


if __name__ == '__main__':
    main()
