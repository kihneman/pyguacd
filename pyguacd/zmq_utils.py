from enum import Enum
from uuid import uuid4

import zmq
import zmq.asyncio
from zmq.devices import ThreadProxy


class ZsockStatus(Enum):
    CLIENT_READY = b'client_ready'
    USER_SOCKET_ERROR = b'user_socket_error'
    USER_SOCKET_RECV = b'user_socket_recv'


async def wait_for_status(zmq_async_sock: zmq.asyncio.Socket, status):
    """Wait for status"""
    msg_parts = await zmq_async_sock.recv_multipart()
    msg_key = msg_parts[0].decode()
    msg_status = msg_parts[1].decode()
    if msg_key != 'status' or msg_status != status:
        print(f'WARNING: Expected "status: {status}", but received status "{msg_key}: {msg_status}"')


def new_ipc_addr(base_path):
    uid = uuid4().hex
    return f'ipc://{base_path}{uid}'


def new_ipc_addr_pair(base_path, with_mon=False):
    ipc = new_ipc_addr(base_path)
    result = [f'{ipc}-in', f'{ipc}-out']
    if with_mon:
        result.append(f'{ipc}-mon')
    return result


class ZmqThreadProxy:
    def __init__(self, base_path, with_mon=False):
        addrs = new_ipc_addr_pair(base_path, with_mon)
        if with_mon:
            self.proxy = ThreadProxy(zmq.PAIR, zmq.PAIR, zmq.PAIR)
            self.addr_in, self.addr_out, self.addr_mon = addrs
        else:
            self.proxy = ThreadProxy(zmq.PAIR, zmq.PAIR)
            self.addr_in, self.addr_out = addrs
            self.addr_mon = ''

        self.proxy.bind_in(self.addr_in)
        self.proxy.bind_out(self.addr_out)
        if with_mon:
            self.proxy.bind_mon(self.addr_mon)
        self.proxy.start()

    def destroy(self):
        self.proxy.context_factory().destroy()
