import asyncio
import socket
from asyncio import create_task
from os import makedirs
from uuid import uuid4

import zmq
import zmq.asyncio

from .constants import (
    GuacClientLogLevel, ZmqMsgKey, ZmqMsgVal, GUACD_SOCKET_DEFAULT_DIR,
    GUACD_CONTROL_SOCKET_PATH, GUACD_ROUTER_SOCKET_PATH, GUACD_USER_SOCKET_PATH
)
from .log import guacd_log
from .socket_utils import get_addresses, resolve_hostname, socket_bind


ZMQ_PAIR_IPC = 'zmq_pair_ipc'


def new_user_ipc_addr():
    uid = uuid4().hex
    return f'ipc://{GUACD_USER_SOCKET_PATH}{uid}'


class UserProxy:
    def __init__(self, router_ipc_addr=None):
        self.ctx = zmq.asyncio.Context()
        self.router_sock = self.ctx.socket(zmq.PAIR)

        if router_ipc_addr is None:
            makedirs(GUACD_SOCKET_DEFAULT_DIR, exist_ok=True)
            router_ipc_addr = f'ipc://{GUACD_ROUTER_SOCKET_PATH}'
        self.router_ipc_addr = router_ipc_addr
        self.router_sock.connect(self.router_ipc_addr)
        self.control_ipc_addr = f'ipc://{GUACD_CONTROL_SOCKET_PATH}'

    async def async_tcp_to_zmq(self, tcp_reader: asyncio.StreamReader, user_sock, user_stop: asyncio.Event):
        # Transfer data from socket to file descriptor
        # while ((length = guac_socket_read(params->socket, buffer, sizeof(buffer))) > 0) {
        #     if (__write_all(params->fd, buffer, length) < 0)
        #         break;
        # }
        data = await tcp_reader.read(100)
        while len(data) > 0:
            print(f'sending "{data.decode()}" from user')
            await user_sock.send(data)
            data = await tcp_reader.read(100)

    async def async_zmq_to_tcp(self, user_sock, tcp_writer: asyncio.StreamWriter):
        # Transfer data from file descriptor to socket
        # int length;
        # while ((length = read(params->fd, buffer, sizeof(buffer))) > 0) {
        #   if (guac_socket_write(params->socket, buffer, length))
        #       break;
        #   guac_socket_flush(params->socket);
        # }
        control_sock = self.ctx.socket(zmq.SUB)
        control_sock.connect(self.control_ipc_addr)
        control_sock.subscribe(ZmqMsgKey.CTRL_INT.value)

        poller = zmq.asyncio.Poller()
        poller.register(user_sock)
        poller.register(control_sock)

        while True:
            socks = dict(await poller.poll())

            if user_sock in socks and socks[user_sock] == zmq.POLLIN:
                msg = await user_sock.recv()
                if len(msg) == 0:
                    break
                print(f'sending "{msg.decode()}" to user')
                tcp_writer.write(msg)
                await tcp_writer.drain()

            elif control_sock in socks and socks[control_sock] == zmq.POLLIN:
                topic, ctrl_msg = await control_sock.recv_multipart()
                if ctrl_msg == ZmqMsgVal.CTRL_INT_STOP.value:
                    break

    async def handle_proxy(self, tcp_reader: asyncio.StreamReader, tcp_writer: asyncio.StreamWriter):
        # Send new user socket to router
        user_ipc_addr = new_user_ipc_addr()
        user_sock = self.ctx.socket(zmq.PAIR)
        user_sock.bind(user_ipc_addr)
        await self.router_sock.send_multipart([ZmqMsgKey.USER_ADDR, user_ipc_addr])

        # Proxy connection
        zmq_to_tcp_task = create_task(self.async_zmq_to_tcp(user_sock, tcp_writer))
        tcp_to_zmq_task = create_task(self.async_tcp_to_zmq(tcp_reader, user_sock))
        done, pending = await asyncio.wait((zmq_to_tcp_task, tcp_to_zmq_task), return_when=asyncio.FIRST_COMPLETED)

        # Cleanup
        for task in pending:
            if not task.done():
                task.cancel()

        tcp_writer.close()
        await tcp_writer.wait_closed()
        user_sock.close()


async def async_proxy(tcp_sock=None, router_ipc_addr=None, cb=None, cb_args=()):
    tcp_zmq_proxy = UserProxy(router_ipc_addr)
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


def launch_proxy(host, port):
    """Launch the asyncio proxy server on provided host and port"""
    if addresses := get_addresses(host, port) is None:
        return

    for address_info in addresses:
        if not resolve_hostname(address_info[-1]):
            continue

        # Get socket
        guac_socket = None
        with socket.socket(address_info[0], socket.SOCK_STREAM) as s:
            if not socket_bind(s, address_info[-1]):
                continue

            # Log listening status
            result_host, result_port = address_info[-1]
            guacd_log(
                GuacClientLogLevel.GUAC_LOG_INFO, f'Listening on host "{result_host}", port {result_port}'
            )

            # Accept connections
            asyncio.run(async_proxy(s))
        break

    else:
        # If unable to bind to anything, fail
        address_host_port = [a[-1] for a in addresses]
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f"Couldn't bind to addresses: {address_host_port}")


if __name__ == '__main__':
    launch_proxy(host='127.0.0.1', port=4822)
