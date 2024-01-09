import asyncio
import socket
from os import makedirs
from os.path import dirname, join

import zmq
import zmq.asyncio


IPC_DIR = join(dirname(__file__), 'ipc')
ZMQ_PAIR_IPC = 'zmq_pair_ipc'


class TcpZmqProxy:
    def __init__(self, ipc_socket_path=None):
        self.ctx = zmq.asyncio.Context()
        self.zsock = self.ctx.socket(zmq.PAIR)
        if ipc_socket_path is None:
            makedirs(IPC_DIR, exist_ok=True)
            ipc_socket_path = join(IPC_DIR, ZMQ_PAIR_IPC)
        self.ipc_socket_path = ipc_socket_path
        self.zsock.bind(f'ipc://{self.ipc_socket_path}')

    async def async_tcp_to_zmq(self, tcp_reader: asyncio.StreamReader):
        # Transfer data from socket to file descriptor
        # while ((length = guac_socket_read(params->socket, buffer, sizeof(buffer))) > 0) {
        #     if (__write_all(params->fd, buffer, length) < 0)
        #         break;
        # }
        data = await tcp_reader.read(100)
        while len(data) > 0:
            print(f'sending "{data.decode()}" to zsock')
            await self.zsock.send(data)
            data = await tcp_reader.read(100)

    async def async_zmq_to_tcp(self, tcp_writer: asyncio.StreamWriter):
        # Transfer data from file descriptor to socket
        # int length;
        # while ((length = read(params->fd, buffer, sizeof(buffer))) > 0) {
        #   if (guac_socket_write(params->socket, buffer, length))
        #       break;
        #   guac_socket_flush(params->socket);
        # }
        msg = await self.zsock.recv()
        while len(msg) > 0:
            print(f'sending "{msg.decode()}" to tcp connection')
            tcp_writer.write(msg)
            await tcp_writer.drain()
            msg = await self.zsock.recv()

    async def handle_proxy(self, tcp_reader: asyncio.StreamReader, tcp_writer: asyncio.StreamWriter):
        zmq_to_tcp = asyncio.create_task(self.async_zmq_to_tcp(tcp_writer))
        tcp_to_zmq = asyncio.create_task(self.async_tcp_to_zmq(tcp_reader))
        pending = (asyncio.create_task(zmq_to_tcp), asyncio.create_task(tcp_to_zmq))

        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)
        tcp_writer.close()
        await tcp_writer.wait_closed()
        self.zsock.close()
        await asyncio.wait(pending)


async def async_proxy(ipc_socket_path=None, tcp_sock=None, cb=None, cb_args=()):
    tcp_zmq_proxy = TcpZmqProxy(ipc_socket_path)
    if tcp_sock is None:
        server = await asyncio.start_server(tcp_zmq_proxy.handle_proxy, '127.0.0.1', 8888)
    else:
        server = await asyncio.start_server(tcp_zmq_proxy.handle_proxy, sock=tcp_sock)

    addrs = ', '.join(str(s.getsockname()) for s in server.sockets)
    print(f'Serving on {addrs}')

    async with server:
        try:
            await server.serve_forever()
        except asyncio.exceptions.CancelledError:
            print('Server closed after cancellation')

    # Run callback
    if cb is not None:
        cb(*cb_args)


def launch_proxy(*args, **kwargs):
    asyncio.run(async_proxy(*args, **kwargs))


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('127.0.0.1', 8888))
    launch_proxy(tcp_sock=sock)
