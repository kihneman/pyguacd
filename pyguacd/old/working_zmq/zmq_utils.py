from enum import Enum
from uuid import uuid4

import zmq
import zmq.asyncio
from zmq.devices import ThreadProxy
from zmq.utils.monitor import parse_monitor_message


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


def zmq_connection_ready(zmq_socket: zmq.Socket, create_monitor=False):
    zmq_monitor = zmq_socket.get_monitor_socket() if create_monitor else zmq_socket
    print('Waiting for connection...')
    for expected in (zmq.Event.ACCEPTED, zmq.Event.HANDSHAKE_SUCCEEDED):
        zmq_monitor.poll()
        mon_msg = parse_monitor_message(zmq_monitor.recv_multipart())
        event = mon_msg.get('event')
        if event != expected:
            event_name = event.name if isinstance(event, zmq.Event) else event
            print(f'Expected "{expected.name}" but got "{event_name}"')
            print('ZMQ connection error')
            return False

    if zmq_socket.recv() == b'ready':
        print('ZMQ ready for connection')
        return True
    else:
        print('ZMQ returned unknown status message')
        return False


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
