import asyncio
from asyncio import create_task

import aiofiles
import zmq
import zmq.asyncio
from zmq.utils.monitor import recv_monitor_message


async def recv_zmq_msg(zmq_sock):
    msg = await zmq_sock.recv()
    print(msg)
    return msg


class ZmqSocketListener:
    def __init__(self, addr=None, sock_type=None, serverish=False):
        self.context = zmq.asyncio.Context()
        self.disconnected: asyncio.Event = asyncio.Event()

        if addr is None or sock_type is None:
            self.zmq_sock = None
        else:
            self.zmq_sock = self.context.socket(sock_type)
            self.mon_sock = self.zmq_sock.get_monitor_socket()
            if serverish:
                self.zmq_sock.bind(addr)
            else:
                self.zmq_sock.connect(addr)

    def connect(self, addr, sock_type):
        socket = self.context.socket(sock_type)
        socket.connect(addr)
        return socket

    async def listen_mon(self):
        while True:
            event_msg = await recv_monitor_message(self.mon_sock)
            event = event_msg.get('event')
            if event == zmq.Event.ACCEPTED:
                print('ZMQ connection accepted')
            elif event == zmq.Event.HANDSHAKE_SUCCEEDED:
                print('ZMQ handshake successful')
            elif event == zmq.Event.DISCONNECTED:
                print('ZMQ disconnecting')
                self.disconnected.set()
                break

    async def listen_zmq(self):
        msg = await recv_zmq_msg(self.zmq_sock)
        while len(msg) > 0:
            msg = await recv_zmq_msg(self.zmq_sock)

    async def listen(self, zmq_sock=None):
        if zmq_sock is None:
            zmq_sock = self.zmq_sock

        mon_sock = zmq_sock.get_monitor_socket()
        poller = zmq.asyncio.Poller()
        poller.register(zmq_sock)
        poller.register(mon_sock)

        while True:
            socks = dict(await poller.poll())

            if zmq_sock in socks and socks[zmq_sock] == zmq.POLLIN:
                await recv_zmq_msg(zmq_sock)

            elif mon_sock in socks and socks[mon_sock] == zmq.POLLIN:
                event_msg = await recv_monitor_message(mon_sock)
                event = event_msg.get('event')
                if event == zmq.Event.ACCEPTED:
                    aiofiles.stdout.write('ZMQ connection accepted')
                elif event == zmq.Event.HANDSHAKE_SUCCEEDED:
                    aiofiles.stdout.write('ZMQ handshake successful')
                elif event == zmq.Event.DISCONNECTED:
                    aiofiles.stdout.write('ZMQ disconnecting')
                    self.disconnected.set()
                    break


async def run_server():
    zmq_sock_listener = ZmqSocketListener('tcp://10.0.0.15:8890', zmq.PAIR, False)
    # await zmq_sock_listener.listen()
    done, pending = await asyncio.wait(
        (create_task(zmq_sock_listener.listen_mon()), create_task(zmq_sock_listener.listen_zmq())),
        return_when=asyncio.FIRST_COMPLETED
    )
    for task in pending:
        task.cancel()


def main():
    asyncio.run(run_server())
