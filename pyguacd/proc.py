import asyncio
import multiprocessing
import threading
from ctypes import c_int, POINTER
from dataclasses import dataclass
from multiprocessing import Process
from typing import Dict, Optional

import zmq
import zmq.asyncio

from . import libguac_wrapper
from .libguac_wrapper import (
    guac_client, guac_client_alloc, guac_client_free, guac_client_load_plugin, guac_client_stop,
    guac_socket_create_zmq, guac_socket_require_keep_alive,
    guac_user_alloc, guac_user_free, guac_user_handle_connection
)
from .constants import (
    GuacClientLogLevel, GuacStatus, GUACD_PROCESS_SOCKET_PATH , GUACD_USEC_TIMEOUT,
    GUACD_ZMQ_PROXY_CLIENT_SOCKET_PATH, GUACD_ZMQ_PROXY_USER_SOCKET_PATH, GUACD_USE_PROXY, GUACD_USE_PUB_SUB
)
from .log import guacd_log, guacd_log_guac_error
from .utils.zmq import new_ipc_addr, zmq_client_proxy


@dataclass
class GuacdProc:
    """Analogous to guacd_proc struct in proc.h"""
    client_ptr: POINTER(guac_client)
    zmq_base_addr: Optional[str] = None
    zmq_context: Optional[zmq.asyncio.Context] = None
    zmq_socket: Optional[zmq.asyncio.Socket] = None
    lock: Optional[asyncio.Lock] = None  # Prevents simultaneous use of connection when not using pubsub
    proxy: bool = GUACD_USE_PROXY
    pubsub: bool = GUACD_USE_PUB_SUB

    def __post_init__(self):
        self.zmq_base_addr = new_ipc_addr(GUACD_PROCESS_SOCKET_PATH)
        if not self.pubsub:
            self.lock = asyncio.Lock()

    @property
    def connection_id(self):
        return bytes(self.client_ptr.contents.connection_id)

    @property
    def zmq_client_addr(self):
        if self.pubsub:
            return f'ipc://{GUACD_ZMQ_PROXY_CLIENT_SOCKET_PATH}'
        elif self.proxy:
            return f'{self.zmq_base_addr}-out'
        else:
            return self.zmq_base_addr

    @property
    def zmq_user_addr(self):
        if self.pubsub:
            return f'ipc://{GUACD_ZMQ_PROXY_USER_SOCKET_PATH}'
        elif self.proxy:
            return f'{self.zmq_base_addr}-in'
        else:
            return self.zmq_base_addr

    def connect_client(self, client_id):
        """Create zmq_socket and connect client for receiving user socket addresses"""
        self.zmq_context = zmq.asyncio.Context()

        if self.pubsub:
            self.zmq_socket = self.zmq_context.socket(zmq.SUB)
            self.zmq_socket.subscribe(client_id)
            self.zmq_socket.connect(self.zmq_client_addr)
        else:
            self.zmq_socket = self.zmq_context.socket(zmq.PAIR)
            if self.proxy:
                self.zmq_socket.connect(self.zmq_client_addr)
            else:
                self.zmq_socket.bind(self.zmq_client_addr)

    def connect_user(self, zmq_context: zmq.asyncio.Context):
        """Create zmq_socket and connect user to client process for sending the socket address"""
        if self.pubsub:
            zmq_socket = zmq_context.socket(zmq.PUB)
            zmq_socket.connect(self.zmq_user_addr)

        else:
            zmq_socket = zmq_context.socket(zmq.PAIR)
            zmq_socket.connect(self.zmq_user_addr)

        return zmq_socket

    async def recv_user_socket_addr(self):
        """Receive new user connection from parent"""
        if self.pubsub:
            client_id, user_socket_addr = await self.zmq_socket.recv_multipart()
        else:
            user_socket_addr = await self.zmq_socket.recv()
        return user_socket_addr.decode()

    async def send_user_socket_addr(self, zmq_context: zmq.asyncio.Context, zmq_user_addr: str):
        if self.pubsub:
            zmq_socket = self.connect_user(zmq_context)
            await zmq_socket.send_multipart((self.connection_id, zmq_user_addr.encode()))
            zmq_socket.close()
        else:
            async with self.lock:
                zmq_socket = self.connect_user(zmq_context)
                await zmq_socket.send(zmq_user_addr.encode())
                zmq_socket.close()


def cleanup_client(client):
    # Request client to stop/disconnect
    guac_client_stop(client)

    # Attempt to free client cleanly
    guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, 'Requesting termination of client...')

    # Attempt to free client (this may never return if the client is malfunctioning)
    guac_client_free(client)
    guacd_log(GuacClientLogLevel.GUAC_LOG_DEBUG, 'Client terminated successfully.')

    # TODO: Forcibly terminate if timeout occurs during client free
    # result = guacd_timed_client_free(client, GUACD_CLIENT_FREE_TIMEOUT);
    # If client was unable to be freed, warn and forcibly kill
    # if (result) {
    # guacd_log(GUAC_LOG_WARNING, "Client did not terminate in a timely "
    # "manner. Forcibly terminating client and any child "
    # "processes.");
    # guacd_kill_current_proc_group();
    # }


def guacd_user_thread(client_ptr, owner, user_socket_addr, guacd_proc_stop_event):
    client = client_ptr.contents

    # Create skeleton user
    user_ptr = guac_user_alloc()
    user = user_ptr.contents
    user.socket = guac_socket_create_zmq(zmq.PAIR, user_socket_addr, False)
    user.client = client_ptr
    user.owner = owner
    guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Created user id "{user.user_id}"')

    # Handle user connection from handshake until disconnect/completion
    guac_user_handle_connection(user_ptr, c_int(GUACD_USEC_TIMEOUT))

    # Clean up
    guac_user_free(user_ptr)

    # Stop client and prevent future users if all users are disconnected
    if client.connected_users == 0:
        guacd_log(
            GuacClientLogLevel.GUAC_LOG_INFO, f'Last user of connection "{client.connection_id}" disconnected'
        )
        guacd_proc_stop_event.set()


async def guacd_proc_serve_users(proc: GuacdProc, proc_ready_event: multiprocessing.Event):

    client_ptr = proc.client_ptr
    client = client_ptr.contents

    # Store asyncio tasks of user threads by the user socket addr
    guacd_user_thread_tasks: Dict[str, asyncio.Task] = dict()

    # Create threading event with awaitable task
    guacd_proc_stop_event = threading.Event()
    guacd_proc_stop_coro = asyncio.to_thread(guacd_proc_stop_event.wait)
    guacd_proc_stop_task = asyncio.create_task(guacd_proc_stop_coro)

    # The first file descriptor is the owner
    owner = 1

    proc.connect_client(str(client.connection_id))
    proc_ready_event.set()

    while True:
        # Wait for either a new user socket or threading event "guacd_proc_stop_event"
        recv_user_socket_task = asyncio.create_task(proc.recv_user_socket_addr())
        recv_user_socket_tasks = [recv_user_socket_task, guacd_proc_stop_task]
        await asyncio.wait(recv_user_socket_tasks, return_when=asyncio.FIRST_COMPLETED)

        if guacd_proc_stop_event.set():
            # Gracefully exit process
            if not recv_user_socket_task.done():
                recv_user_socket_task.cancel()
                await recv_user_socket_task
                break

        user_socket_addr = recv_user_socket_task.result()
        if len(user_socket_addr) > 0:
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Received user_socket_addr "{user_socket_addr}"')
        else:
            guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Invalid user connection to client')
            continue

        # Launch user thread
        guacd_user_thread_coro = asyncio.to_thread(
            guacd_user_thread, client_ptr, owner, user_socket_addr, guacd_proc_stop_event
        )
        guacd_user_thread_tasks[user_socket_addr] = asyncio.create_task(guacd_user_thread_coro, name=user_socket_addr)

        # Future file descriptors are not owners
        owner = 0

        await asyncio.sleep(.1)


def guacd_exec_proc(proc: GuacdProc, protocol: str, proc_ready_event: multiprocessing.Event):

    client_ptr = proc.client_ptr
    client = client_ptr.contents

    # Init client for selected protocol
    if guac_client_load_plugin(client_ptr, protocol):
        # Log error
        guac_error = libguac_wrapper.__guac_error()[0]
        if guac_error == GuacStatus.GUAC_STATUS_NOT_FOUND:
            guacd_log(
                GuacClientLogLevel.GUAC_LOG_WARNING, f'Support for protocol "{protocol}" is not installed'
            )
        else:
            guacd_log_guac_error(GuacClientLogLevel.GUAC_LOG_ERROR, 'Unable to load client plugin')

        cleanup_client(client_ptr)
    else:
        # Extra debug
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Loaded plugin for connection id "{client.connection_id}"')

    # Enable keep alive on the broadcast socket
    client_socket_ptr = client.socket
    guac_socket_require_keep_alive(client_socket_ptr)

    if GUACD_USE_PROXY and not GUACD_USE_PUB_SUB:
        with zmq_client_proxy(base_path=proc.zmq_base_addr, pub_sub=False):
            asyncio.run(guacd_proc_serve_users(proc, proc_ready_event))
    else:
        asyncio.run(guacd_proc_serve_users(proc, proc_ready_event))

    # Clean up
    cleanup_client(client_ptr)


def guacd_create_proc(protocol: str):

    # Associate new client
    proc = GuacdProc(guac_client_alloc())

    # Init logging
    # client.log_handler = pointer(ctypes_wrapper.guac_client_log_handler(log.guacd_client_log))

    proc_ready_event = multiprocessing.Event()
    proc.process = Process(target=guacd_exec_proc, args=(proc, protocol, proc_ready_event))
    proc.process.start()

    # Wait for process to be ready
    proc_ready_event.wait(2)
    if proc_ready_event.is_set():
        print('Client process started')
        return proc
    else:
        print('ERROR: Client process failed to start')
        proc.process.kill()
        proc.process.close()
        return None
