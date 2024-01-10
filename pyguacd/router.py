import asyncio
from os import makedirs

import zmq
import zmq.asyncio

from .constants import (
    GuacClientLogLevel, ZmqMsgKey, GUAC_CLIENT_ID_PREFIX, GUACD_SOCKET_DEFAULT_DIR, GUACD_ROUTER_SOCKET_PATH
)
from .libguac_wrapper import guac_parser_alloc, guac_parser_free, guac_socket_create_zmq, guac_socket_free
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
        self.router_sock.bind(self.router_ipc_addr)

    async def zmq_listener(self):
        user_addr_key, user_ipc_addr = await self.router_sock.recv_multipart()
        if user_addr_key != ZmqMsgKey.USER_ADDR:
            print(f'Unexpected key for user socket "{user_addr_key}"')
            return

        # This may need to be in another thread due to blocking libguac parser and libguac zmq
        guac_sock = guac_socket_create_zmq(zmq.PAIR, user_ipc_addr, False)
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


def launch_router():
    router = Router()
    asyncio.run(router.zmq_listener())
