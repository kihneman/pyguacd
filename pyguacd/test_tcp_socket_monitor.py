import asyncio
from asyncio import create_task, gather
from asyncio.streams import StreamReader, StreamWriter
from dataclasses import dataclass
from typing import Optional


@dataclass
class TcpServer:
    server: Optional[asyncio.Server] = None
    conn_reader: Optional[StreamReader] = None
    conn_writer: Optional[StreamWriter] = None
    srv_reader: Optional[StreamReader] = None
    srv_writer: Optional[StreamWriter] = None

    async def close(self):
        print("Close the connection")
        self.srv_writer.close()
        self.conn_writer.close()
        await gather(create_task(self.srv_writer.wait_closed()), create_task(self.conn_writer.wait_closed()))

    async def handle(self, reader: StreamReader, writer: StreamWriter):
        self.srv_reader, self.srv_writer = reader, writer
        self.conn_reader, self.conn_writer = await asyncio.open_connection('127.0.0.1', 4882)

    async def handle_conn_read(self):
        from_addr = self.conn_writer.get_extra_info('peername')
        to_addr = self.srv_writer.get_extra_info('peername')
        while True:
            data = await self.conn_reader.read(1000)
            message = data.decode()

            print(f"Received from {from_addr!r}: {message!r}")

            print(f"Send to {to_addr!r}: {message!r}")
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

            print(f"Received from {from_addr!r}: {message!r}")

            print(f"Send to {to_addr!r}: {message!r}")
            self.conn_writer.write(data)
            await self.conn_writer.drain()

            # if data == b'q' or len(data) == 0:
            if len(data) == 0:
                await self.close()
                break
        self.server.close()


async def run_server():
    tcp_server = TcpServer()
    tcp_server.server = await asyncio.start_server(tcp_server.handle, '127.0.0.1', 8888)
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
