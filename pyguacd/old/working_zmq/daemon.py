import asyncio
import socket
from argparse import ArgumentParser
from multiprocessing import Process
from threading import Thread

import zmq
from zmq.devices import ThreadProxy
from zmq.utils.monitor import parse_monitor_message

from . import test_tcp_socket_monitor
from ..single_connection.connection import guacd_route_connection
from ...constants import (
    GUACD_CONTROL_SOCKET_PATH, GUACD_DEFAULT_BIND_HOST, GUACD_DEFAULT_BIND_PORT,
    GUACD_ROUTER_SOCKET_PATH, GUACD_TCP_PROXY_SOCKET_PATH
)
from ...libguac_wrapper import guac_socket_create_zmq, guac_socket_open
from .router import launch_router
from .user_proxy import run_tcp_proxy_in_loop, start_tcp_proxy_server


def create_zmq_control_pub():
    ctx = zmq.Context()
    zmq_control_pub = ctx.socket(zmq.PUB)
    control_ipc_addr = f'ipc://{GUACD_CONTROL_SOCKET_PATH}'
    zmq_control_pub.bind(control_ipc_addr)
    return zmq_control_pub


def create_zmq_router_proxy():
    zmq_router_proxy = ThreadProxy(zmq.PAIR, zmq.PAIR)
    zmq_router_proxy.bind_in(f'ipc://{GUACD_TCP_PROXY_SOCKET_PATH}')
    zmq_router_proxy.bind_out(f'ipc://{GUACD_ROUTER_SOCKET_PATH}')
    zmq_router_proxy.start()
    return zmq_router_proxy.context_factory()


def run_tcp_proxy_in_process():
    p = Process(target=run_tcp_proxy_in_loop, args=('127.0.0.1', 4822))
    p.start()


async def main(timeout):
    zmq_control_pub: zmq.Socket = create_zmq_control_pub()
    zmq_router_proxy_ctx: zmq.Context = create_zmq_router_proxy()
    launch_router_task = asyncio.create_task(launch_router(timeout))
    start_proxy_task = asyncio.create_task(start_tcp_proxy_server())
    done, pending = await asyncio.wait((launch_router_task, start_proxy_task), return_when=asyncio.FIRST_COMPLETED)

    # Cleanup
    for task in pending:
        if not task.done():
            task.cancel()
    zmq_router_proxy_ctx.destroy()
    zmq_control_pub.close()


def socket_no_async():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((GUACD_DEFAULT_BIND_HOST, int(GUACD_DEFAULT_BIND_PORT)))
    print(f'Listening on host "{GUACD_DEFAULT_BIND_HOST}", port {GUACD_DEFAULT_BIND_PORT}')
    sock.listen()
    conn, addr = sock.accept()
    print(f'Connection made by {addr}')
    guac_socket = guac_socket_open(conn.fileno())
    guacd_route_connection(guac_socket)


def zmq_no_async(host='0.0.0.0', port=8892):
    # zmq_sock = guac_socket_create_zmq(zmq.PAIR, f'tcp://{host}:{port}', False)
    guacd_route_connection(zmq_addr=f'tcp://{host}:{port}')


def zmq_connection_ready(zmq_status: zmq.Socket):
    zmq_status_mon = zmq_status.get_monitor_socket()
    print('Waiting for connection...')
    for expected in (zmq.Event.LISTENING, zmq.Event.ACCEPTED, zmq.Event.HANDSHAKE_SUCCEEDED):
        zmq_status_mon.poll()
        mon_msg = parse_monitor_message(zmq_status_mon.recv_multipart())
        event = mon_msg.get('event')
        if event != expected:
            event_name = event.name if isinstance(event, zmq.Event) else event
            print(f'Expected "{expected.name}" but got "{event_name}"')
            print('ZMQ connection error')
            return False

    if zmq_status.recv() == b'ready':
        print('ZMQ ready for connection')
        return True
    else:
        print('ZMQ returned unknown status message')
        return False


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-t', '--timeout', type=int)
    parser.add_argument('-p', '--proxy', action='store_true')
    parser.add_argument('-s', '--socket-no-async', action='store_true')
    parser.add_argument('-z', '--zmq-no-async', action='store_true')
    args = parser.parse_args()
    if args.socket_no_async:
        if args.proxy:
            t = Thread(target=socket_no_async)
            t.start()
            test_tcp_socket_monitor.main()
        else:
            socket_no_async()
    elif args.zmq_no_async:
        ctx = zmq.Context()
        zmq_ready = ctx.socket(zmq.PAIR)
        zmq_ready.bind('tcp://0.0.0.0:8891')

        t = Thread(target=test_tcp_socket_monitor.main, kwargs={'use_zmq': True})
        t.start()

        if zmq_connection_ready(zmq_ready):
            zmq_no_async('0.0.0.0', 8892)
    else:
        asyncio.run(main(timeout=args.timeout))