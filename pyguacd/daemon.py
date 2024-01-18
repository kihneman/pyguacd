import asyncio
from asyncio import create_task, StreamReader, StreamWriter, Task
from itertools import count

import zmq
import zmq.asyncio

from .connection import guacd_route_connection
from .constants import GUACD_USER_SOCKET_PATH
from .utils.zmq import new_ipc_addr, check_zmq_monitor_events


DATA_CHUNK_SIZE = 1000


async def handle_tcp_to_zmq(tcp_reader: StreamReader, zmq_socket: zmq.asyncio.Socket):
    while True:
        data = await tcp_reader.read(DATA_CHUNK_SIZE)
        if len(data) == 0:
            print('tcp to zmq handler closing')
            break

        await zmq_socket.send(data)


async def handle_zmq_to_tcp(zmq_socket: zmq.asyncio.Socket, tcp_writer: StreamWriter):
    while True:
        data = await zmq_socket.recv()
        if len(data) == 0:
            print('zmq to tcp handler closing')
            break

        tcp_writer.write(data)
        await tcp_writer.drain()


async def monitor_zmq_socket(zmq_monitor_socket: zmq.asyncio.Socket, zmq_to_tcp_task: Task):
    zmq_events = [zmq.Event.LISTENING, zmq.Event.ACCEPTED, zmq.Event.HANDSHAKE_SUCCEEDED, zmq.Event.DISCONNECTED]
    if await check_zmq_monitor_events(zmq_monitor_socket, zmq_events):
        print('Parsed connection identifier')

        if await check_zmq_monitor_events(zmq_monitor_socket, zmq_events[1:]):
            print('User disconnected')
        else:
            print('Connection terminated unexpectedly')
    else:
        print('Connection parsing terminated unexpectedly')

    # Prevent handle_zmq_to_tcp function from waiting forever to read on a closed socket
    zmq_to_tcp_task.cancel()
    await zmq_to_tcp_task


async def handle_connection(
        zmq_socket: zmq.asyncio.Socket, zmq_monitor: zmq.asyncio.Socket,
        tcp_reader: StreamReader, tcp_writer: StreamWriter
):
    done, pending = await asyncio.wait([
    ], return_when=asyncio.FIRST_COMPLETED)

    for task in pending:
        task.cancel()


class TcpConnectionServer:
    _counter = count(1)
    current_connections = 0
    total_connections = 0
    proc_map = dict()

    def __init__(self):
        self.current_connection = self.total_connections = next(self._counter)
        self.current_connections += 1
        self.zmq_context = zmq.asyncio.Context()

    async def handle(self, tcp_reader: StreamReader, tcp_writer: StreamWriter):
        zmq_user_socket = self.zmq_context.socket(zmq.PAIR)
        zmq_user_monitor = zmq_user_socket.get_monitor_socket()
        zmq_user_addr = new_ipc_addr(GUACD_USER_SOCKET_PATH)
        zmq_user_socket.bind(zmq_user_addr)
        print(
            f'Starting connection #{self.current_connection}. Current connections running: {self.current_connections}'
        )
        await asyncio.wait([
            create_task(
                monitor_zmq_socket(zmq_user_monitor, create_task(handle_zmq_to_tcp(zmq_user_socket, tcp_writer)))
            ),
            create_task(handle_tcp_to_zmq(tcp_reader, zmq_user_socket)),
            create_task(guacd_route_connection(self.proc_map, zmq_user_addr, self.zmq_context)),
        ])
        print(
            f'Finished connection #{self.current_connection}. Current connections running: {self.current_connections}'
        )

    @classmethod
    async def start(cls):
        return await asyncio.start_server(cls().handle, '0.0.0.0', 8888)


async def run_server():
    server = await TcpConnectionServer.start()

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        try:
            await server.serve_forever()
        except asyncio.exceptions.CancelledError:
            print('Server closed')


if __name__ == '__main__':
    asyncio.run(run_server())
