import asyncio
from asyncio import create_task, gather
from asyncio.streams import StreamReader, StreamWriter
from dataclasses import dataclass
from typing import Optional

import zmq
import zmq.asyncio

from .constants import GUACD_DEFAULT_BIND_PORT


@dataclass
class TcpServer:
    server: Optional[asyncio.Server] = None
    conn_reader: Optional[StreamReader] = None
    conn_writer: Optional[StreamWriter] = None
    srv_reader: Optional[StreamReader] = None
    srv_writer: Optional[StreamWriter] = None
    zmq_context: Optional[zmq.asyncio.Context] = None
    zmq_connect: Optional[zmq.asyncio.Socket] = None
    zmq_monitor: Optional[zmq.asyncio.Socket] = None
    zmq_ready: Optional[zmq.asyncio.Socket] = None
    use_zmq: bool = False

    def __post_init__(self):
        self.zmq_context = zmq.asyncio.Context()
        self.zmq_monitor = self.zmq_context.socket(zmq.PAIR)
        self.zmq_monitor.bind('tcp://0.0.0.0:8890')

    async def close(self):
        await self.zmq_monitor.send(b'Close the connection')
        self.zmq_monitor.close()
        self.srv_writer.close()
        if self.use_zmq:
            self.zmq_connect.close()
            self.zmq_ready.close()
            await self.srv_writer.wait_closed()
        else:
            self.conn_writer.close()
            await gather(create_task(self.srv_writer.wait_closed()), create_task(self.conn_writer.wait_closed()))

    async def handle(self, reader: StreamReader, writer: StreamWriter):
        self.srv_reader, self.srv_writer = reader, writer
        if self.use_zmq:
            self.zmq_connect = self.zmq_context.socket(zmq.PAIR)
            self.zmq_connect.bind('tcp://0.0.0.0:8892')
            self.zmq_ready = self.zmq_context.socket(zmq.PAIR)
            self.zmq_ready.connect('tcp://127.0.0.1:8891')
        else:
            self.conn_reader, self.conn_writer = await asyncio.open_connection('127.0.0.1', int(GUACD_DEFAULT_BIND_PORT))

        await asyncio.wait(
            (create_task(self.handle_conn_read()), create_task(self.handle_srv_read())),
            return_when=asyncio.ALL_COMPLETED
        )

    async def handle_conn_read(self):
        from_addr = 'zmq' if self.use_zmq else self.conn_writer.get_extra_info('peername')
        to_addr = self.srv_writer.get_extra_info('peername')

        while True:
            if self.use_zmq:
                data = await self.zmq_connect.recv()
            else:
                data = await self.conn_reader.read(1000)
            message = data.decode()

            await self.zmq_monitor.send(f'Received from {from_addr}: {message}'.encode())
            await self.zmq_monitor.send(f'Sending to {to_addr}...'.encode())

            self.srv_writer.write(data)
            await self.srv_writer.drain()

            if len(data) == 0:
                await self.close()
                break
        self.server.close()

    async def handle_srv_read(self):
        from_addr = self.srv_writer.get_extra_info('peername')
        to_addr = 'zmq' if self.use_zmq else self.conn_writer.get_extra_info('peername')

        while True:
            data = await self.srv_reader.read(1000)
            message = data.decode()

            await self.zmq_monitor.send(f'Received from {from_addr}: {message}'.encode())
            await self.zmq_monitor.send(f'Sending to {to_addr}...'.encode())

            if self.use_zmq:
                await self.zmq_connect.send(data)
            else:
                self.conn_writer.write(data)
                await self.conn_writer.drain()

            if len(data) == 0:
                await self.close()
                break
        self.server.close()


async def run_server(**kwargs):
    tcp_server = TcpServer(**kwargs)
    tcp_server.server = await asyncio.start_server(tcp_server.handle, '0.0.0.0', 8888)
    server = tcp_server.server

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        try:
            await server.serve_forever()
        except asyncio.exceptions.CancelledError:
            print('Server closed')


def main(**kwargs):
    asyncio.run(run_server(**kwargs))
