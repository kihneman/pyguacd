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
    zmq_output: Optional[zmq.asyncio.Socket] = None

    def __post_init__(self):
        ctx = zmq.asyncio.Context()
        self.zmq_output = ctx.socket(zmq.PAIR)
        self.zmq_output.bind('tcp:0.0.0.0:8890')

    async def close(self):
        await self.zmq_output.send(b'Close the connection')
        self.zmq_output.close()
        self.srv_writer.close()
        self.conn_writer.close()
        await gather(create_task(self.srv_writer.wait_closed()), create_task(self.conn_writer.wait_closed()))

    async def handle(self, reader: StreamReader, writer: StreamWriter):
        self.srv_reader, self.srv_writer = reader, writer
        self.conn_reader, self.conn_writer = await asyncio.open_connection('127.0.0.1', int(GUACD_DEFAULT_BIND_PORT))
        await asyncio.wait(
            (create_task(self.handle_conn_read()), create_task(self.handle_srv_read())),
            return_when=asyncio.ALL_COMPLETED
        )

    async def handle_conn_read(self):
        from_addr = self.conn_writer.get_extra_info('peername')
        to_addr = self.srv_writer.get_extra_info('peername')
        while True:
            data = await self.conn_reader.read(1000)
            message = data.decode()

            # print(f"Received from {from_addr!r}: {message!r}")
            await self.zmq_output.send(f'Received from {from_addr}: {message}'.encode())

            # print(f"Send to {to_addr!r}: {message!r}")
            await self.zmq_output.send(f'Send to {to_addr}: {message}'.encode())
            self.srv_writer.write(data)
            await self.srv_writer.drain()

            if len(data) == 0:
                await self.close()
                break
        self.server.close()

    async def handle_srv_read(self):
        from_addr = self.srv_writer.get_extra_info('peername')
        to_addr = self.conn_writer.get_extra_info('peername')
        while True:
            data = await self.srv_reader.read(1000)
            message = data.decode()

            # print(f"Received from {from_addr!r}: {message!r}")
            await self.zmq_output.send(f'Received from {from_addr}: {message}'.encode())

            # print(f"Send to {to_addr!r}: {message!r}")
            await self.zmq_output.send(f'Send to {to_addr}: {message}'.encode())
            self.conn_writer.write(data)
            await self.conn_writer.drain()

            # if data == b'q' or len(data) == 0:
            if len(data) == 0:
                await self.close()
                break
        self.server.close()


async def run_server():
    tcp_server = TcpServer()
    tcp_server.server = await asyncio.start_server(tcp_server.handle, '0.0.0.0', 8888)
    server = tcp_server.server

    addrs = ', '.join(str(sock.getsockname()) for sock in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        try:
            await server.serve_forever()
        except asyncio.exceptions.CancelledError:
            print('Server closed')

def main():
    asyncio.run(run_server())
