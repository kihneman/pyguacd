import asyncio
from argparse import ArgumentParser
from multiprocessing import Process

import zmq
from zmq.devices import ThreadProxy

from .connection import guacd_route_connection
from .constants import (
    GUACD_CONTROL_SOCKET_PATH, GUACD_DEFAULT_BIND_HOST, GUACD_DEFAULT_BIND_PORT,
    GUACD_ROUTER_SOCKET_PATH, GUACD_TCP_PROXY_SOCKET_PATH
)
from .libguac_wrapper import guac_socket_create_zmq
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


def zmq_no_async():
    zmq_sock = guac_socket_create_zmq(zmq.STREAM, f'tcp://{GUACD_DEFAULT_BIND_HOST}:{GUACD_DEFAULT_BIND_PORT}', True)
    guacd_route_connection(zmq_sock)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-t', '--timeout', type=int)
    parser.add_argument('-z', '--zmq-no-async', action='store_true')
    args = parser.parse_args()
    if args.zmq_no_async:
        zmq_no_async()
    else:
        asyncio.run(main(timeout=args.timeout))
