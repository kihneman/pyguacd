import asyncio
from ctypes import c_int
from os import makedirs

import zmq
import zmq.asyncio

from .constants import (
    GuacClientLogLevel, ZmqMsgTopic, GUAC_CLIENT_ID_PREFIX, GUACD_SOCKET_DEFAULT_DIR, GUACD_ROUTER_SOCKET_PATH
)
from .libguac_wrapper import guac_parser_alloc, guac_parser_free, guac_socket_create_zmq, guac_socket_free, String
from .log import guacd_log
from .parser import parse_identifier


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
        mon_sock.connect(mon_addr)
        data = await mon_sock.recv()
        print(f'Received initial user data "{data.decode()}" on ipc socket "{user_addr.decode()}"')

        # This may need to be in another thread due to blocking libguac parser and libguac zmq
        guac_sock = guac_socket_create_zmq(c_int(zmq.PAIR), String(user_addr), False)
        parser_ptr = guac_parser_alloc()
        identifier = parse_identifier(parser_ptr, guac_sock)
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
