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
from .proc import guacd_create_proc
from .zmq_utils import wait_for_status, ZsockStatus


async def guac_socket_poll_forever(guac_socket):
    slept = 0
    while ret_val := guac_socket_select(guac_socket, 0) == 0:
        # Sleep 1ms
        await asyncio.sleep(.001)
        slept += 1
    # print(f'Slept {slept}ms')
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

    @staticmethod
    async def send_user_socket_addr(proc_sock: zmq.asyncio.Socket, user_socket_addr: bytes):
        await wait_for_status(proc_sock, ZsockStatus.CLIENT_READY)
        print('Client ready')
        await proc_sock.send(user_socket_addr)
        print('User socket address sent')
        # await self.zmq_socket.send_json({'user_socket_path': user_socket_path})
        # self.wait_for_status(ZsockStatus.USER_SOCKET_RECV)
        # return user_socket_path

    @staticmethod
    async def zmq_monitor_output(monitor_sock):
        while True:
            output = await monitor_sock.recv()
            print(f'MONITOR: {output.decode()}')

    async def zmq_listener(self):
        user_addr, mon_addr = await self.router_sock.recv_multipart()

        # This may need to be in another thread due to blocking libguac parser and libguac zmq
        # For now await availability of data before running
        guac_sock = guac_socket_create_zmq(c_int(zmq.PAIR), String(user_addr), False)
        await guac_socket_poll(guac_sock, 2)
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
            guacd_proc = guacd_create_proc(identifier, self.ctx)

        guac_parser_free(parser_ptr)
        guac_socket_free(guac_sock)

        await self.send_user_socket_addr(guacd_proc.zmq_socket, user_addr)

        # Test run for 60 seconds
        mon_sock = self.ctx.socket(zmq.PAIR)
        mon_sock.connect(mon_addr.decode())
        for i in range(60, 0, -5):
            print(f'TIMER: {i}...')
            return await wait_for(
                create_task(self.zmq_monitor_output(mon_sock)), timeout=5
            )


async def launch_router():
    router = Router()
    await router.zmq_listener()


def run_router_in_loop():
    asyncio.run(launch_router())


if __name__ == '__main__':
    run_router_in_loop()
