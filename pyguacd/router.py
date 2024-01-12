import asyncio
from asyncio import create_task, wait_for
from ctypes import c_int
from os import makedirs

import zmq
import zmq.asyncio

from .constants import (
    GuacClientLogLevel, ZmqMsgTopic, GUAC_CLIENT_ID_PREFIX, GUACD_SOCKET_DEFAULT_DIR, GUACD_ROUTER_SOCKET_PATH
)
from .libguac_wrapper import (
    String, guac_parser_alloc, guac_parser_free, guac_socket_create_zmq, guac_socket_free, guac_socket_select
)
from .log import guacd_log
from .parser import parse_identifier


async def guac_socket_poll_forever(guac_socket):
    slept = 0
    while ret_val := guac_socket_select(guac_socket, 0) == 0:
        # Sleep 10ms
        await asyncio.sleep(.01)
        slept += 10
    print(f'Slept {slept}ms')
    return ret_val


async def guac_socket_poll(guac_sock, timeout):
    return await wait_for(
        create_task(guac_socket_poll_forever(guac_sock)),
        timeout=timeout
    )


class Router:
    def __init__(self, router_ipc_addr=None):
        self.ctx = zmq.asyncio.Context()
        self.router_sock = self.ctx.socket(zmq.PAIR)

        if router_ipc_addr is None:
            makedirs(GUACD_SOCKET_DEFAULT_DIR, exist_ok=True)
            router_ipc_addr = f'ipc://{GUACD_ROUTER_SOCKET_PATH}'
        self.router_ipc_addr = router_ipc_addr
        self.router_sock.connect(self.router_ipc_addr)

    async def zmq_listener(self):
        user_addr, mon_addr = await self.router_sock.recv_multipart()
        mon_sock = self.ctx.socket(zmq.PAIR)
        mon_sock.connect(mon_addr.decode())

        # This may need to be in another thread due to blocking libguac parser and libguac zmq
        # For now await availability of data before running
        guac_sock = guac_socket_create_zmq(c_int(zmq.PAIR), String(user_addr), False)
        await guac_socket_poll(guac_sock, 2)
        parser_ptr = guac_parser_alloc()
        identifier = parse_identifier(parser_ptr, guac_sock)

        item_count = await mon_sock.poll(1000)
        if item_count == 0:
            print("Couldn't get data from monitor port")
        else:
            data = await mon_sock.recv()
            print(f'Monitored initial user data "{data.decode()}" sent on ipc socket "{user_addr.decode()}"')

        if identifier is None:
            guac_parser_free(parser_ptr)
            return 1

        # If connection ID, retrieve existing process
        if identifier[0] == GUAC_CLIENT_ID_PREFIX:
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, 'Selecting existing connection not implemented')
            guac_parser_free(parser_ptr)
            return 1

        # Otherwise, create new client
        else:
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Creating new client for protocol "{identifier.decode()}"')

        guac_parser_free(parser_ptr)
        guac_socket_free(guac_sock)


async def launch_router():
    router = Router()
    await router.zmq_listener()


def run_router_in_loop():
    asyncio.run(launch_router())


if __name__ == '__main__':
    run_router_in_loop()
