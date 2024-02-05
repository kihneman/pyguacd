import asyncio
import os
import sys
from asyncio import create_task, StreamReader, StreamWriter, Task
from dataclasses import dataclass, field
from typing import Dict, Iterable

import zmq
import zmq.asyncio

from .connection import guacd_route_connection
from .constants import GUACD_DEFAULT_BIND_HOST, GUACD_DEFAULT_BIND_PORT, GUACD_SOCKET_DIR
from .proc import GuacdProc
from .utils.ipc_addr import new_ipc_addr, remove_ipc_addr_file
from .utils.zmq_monitor import check_zmq_monitor_events


DATA_CHUNK_SIZE = 2 ** 10  # ~1kB data chunk


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
        Iterable of connection tasks to cancel after ZeroMQ socket disconnect
    """
    # These are the events that occur on successful connect and disconnect
    zmq_events = [zmq.Event.ACCEPTED, zmq.Event.HANDSHAKE_SUCCEEDED, zmq.Event.DISCONNECTED]

    # Wait for connect and disconnect by libguac guac_parser_expect
    if error_msg := await check_zmq_monitor_events(zmq_monitor_socket, zmq_events) is not None:
        raise ConnectionError(error_msg)

    # Wait for connect and disconnect by libguac guac_user_handle_connection
    if error_msg := await check_zmq_monitor_events(zmq_monitor_socket, zmq_events) is not None:
        raise ConnectionError(error_msg)

    # Cancel connection handles to prevent waiting to read forever on closed socket
    for conn_task in connection_tasks:
        if not conn_task.done():
            conn_task.cancel()
            await conn_task


@dataclass
class TcpHandler:
    """Dataclass to keep state between TCP connections

    The only data to keep between TCP connections is proc_map.
    The Python dict is asyncio safe since no await is needed to read or update the dict.
    """
    # The map of existing guacd client processes
    proc_map: Dict[str, GuacdProc] = field(default_factory=dict)

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
                create_task(guacd_route_connection(self.proc_map, zmq_user_addr, ctx)),
            ])

        # Clean up
        remove_ipc_addr_file(zmq_user_addr)


async def run_server():
    handler = TcpHandler()
    server = await asyncio.start_server(handler.handle, GUACD_DEFAULT_BIND_HOST, GUACD_DEFAULT_BIND_PORT)
    if not sys.platform.startswith('win'):
        import signal
        loop = server.get_loop()
        loop.add_signal_handler(signal.SIGINT, server.close)
        loop.add_signal_handler(signal.SIGTERM, server.close)

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
    os.makedirs(GUACD_SOCKET_DIR, exist_ok=True)
    asyncio.run(run_server())


if __name__ == '__main__':
    main()
