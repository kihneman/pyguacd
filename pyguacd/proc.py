import asyncio
import multiprocessing
import threading
from asyncio.exceptions import CancelledError
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
    GuacClientLogLevel, GuacStatus, GUACD_PROCESS_SOCKET_PATH, GUACD_USEC_TIMEOUT, MONITOR_ZMQ_CLIENT_SOCKET
)
from .log import guacd_log, guacd_log_guac_error
from .utils.zmq import check_zmq_monitor_events, new_ipc_addr


@dataclass
class GuacdProc:
    """Analogous to guacd_proc struct in proc.h"""
    client_ptr: POINTER(guac_client)

    # Prevents simultaneous use of connection when not using pubsub
    lock: Optional[asyncio.Lock] = None

    process: Optional[Process] = None
    ready_event: Optional[multiprocessing.Event] = None

    # Final asyncio task to clean up after process
    task: Optional[asyncio.Task] = None

    zmq_socket_addr: Optional[str] = None
    zmq_context: Optional[zmq.asyncio.Context] = None
    zmq_socket: Optional[zmq.asyncio.Socket] = None
    zmq_monitor_socket: Optional[zmq.asyncio.Socket] = None

    def __post_init__(self):
        self.lock = asyncio.Lock()
        self.ready_event = multiprocessing.Event()
        self.zmq_socket_addr = new_ipc_addr(GUACD_PROCESS_SOCKET_PATH)

    def connect_client(self, monitor=True):
        """Create zmq_socket and connect client for receiving user socket addresses"""
        self.zmq_context = zmq.asyncio.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PAIR)

        if monitor:
            self.zmq_monitor_socket = self.zmq_socket.get_monitor_socket()

        self.zmq_socket.bind(self.zmq_socket_addr)

    def connect_user(self, zmq_context: zmq.asyncio.Context):
        """Create zmq_socket and connect user to client process for sending the socket address"""
        self.zmq_socket = zmq_context.socket(zmq.PAIR)
        self.zmq_socket.connect(self.zmq_socket_addr)

    async def monitor_socket(self):
        zmq_events = [zmq.Event.LISTENING, zmq.Event.ACCEPTED, zmq.Event.HANDSHAKE_SUCCEEDED, zmq.Event.DISCONNECTED]
        event_msgs = [
            f'**** Listening on client socket "{self.zmq_socket_addr}"', None,
            f'**** Client socket "{self.zmq_socket_addr}" accepted router connection',
            f'**** Client socket "{self.zmq_socket_addr}" closed',
        ]
        await check_zmq_monitor_events(self.zmq_monitor_socket, zmq_events, event_msgs)
        self.zmq_monitor_socket.close()

    async def recv_user_socket_addr(self):
        """Receive new user connection from parent"""
        try:
            user_socket_addr = await self.zmq_socket.recv()
        except CancelledError:
            return None
        else:
            return user_socket_addr.decode()

    async def send_user_socket_addr(self, zmq_user_addr: str):
        async with self.lock:
            await self.zmq_socket.send(zmq_user_addr.encode())

    def close(self):
        self.zmq_socket.close()


def cleanup_client(client_ptr):
    # Request client to stop/disconnect
    guac_client_stop(client_ptr)

    # Attempt to free client cleanly
    guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, 'Requesting termination of client...')

    # Attempt to free client (this may never return if the client is malfunctioning)
    guac_client_free(client_ptr)
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


async def guacd_proc_serve_users(proc: GuacdProc):
    client_ptr = proc.client_ptr

    # Store asyncio tasks of user threads by the user socket addr
    guacd_user_thread_tasks: Dict[str, asyncio.Task] = dict()

    # Create threading event with awaitable task
    guacd_proc_stop_event = threading.Event()
    guacd_proc_stop_coro = asyncio.to_thread(guacd_proc_stop_event.wait)
    guacd_proc_stop_task = asyncio.create_task(guacd_proc_stop_coro)

    # The first file descriptor is the owner
    owner = 1

    proc.connect_client(monitor=MONITOR_ZMQ_CLIENT_SOCKET)
    if MONITOR_ZMQ_CLIENT_SOCKET:
        monitor_task = asyncio.create_task(proc.monitor_socket())
    proc.ready_event.set()

    while True:
        # Wait for either a new user socket or threading event "guacd_proc_stop_event"
        recv_user_socket_task = asyncio.create_task(proc.recv_user_socket_addr())
        done, pending = await asyncio.wait(
            [recv_user_socket_task, guacd_proc_stop_task], return_when=asyncio.FIRST_COMPLETED
        )

        if guacd_proc_stop_task in done:
            # Gracefully exit process
            recv_user_socket_task.cancel()
            await recv_user_socket_task
            break

        user_socket_addr = recv_user_socket_task.result()
        if not user_socket_addr:
            guacd_log(
                GuacClientLogLevel.GUAC_LOG_ERROR,
                'Client ZMQ socket was canceled' if user_socket_addr is None else 'Invalid (empty) user socket address'
            )
            continue

        # Launch user thread
        guacd_user_thread_coro = asyncio.to_thread(
            guacd_user_thread, client_ptr, owner, user_socket_addr, guacd_proc_stop_event
        )
        guacd_user_thread_tasks[user_socket_addr] = asyncio.create_task(guacd_user_thread_coro, name=user_socket_addr)

        # Future file descriptors are not owners
        owner = 0


def guacd_exec_proc(proc: GuacdProc, protocol: str):

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

    # Enable keep alive on the broadcast socket
    client_socket_ptr = client.socket
    guac_socket_require_keep_alive(client_socket_ptr)

    asyncio.run(guacd_proc_serve_users(proc))

    # Clean up
    proc.close()
    cleanup_client(client_ptr)


def guacd_create_proc(protocol: str):

    # Associate new client
    proc = GuacdProc(guac_client_alloc())

    # Init logging
    # client.log_handler = pointer(ctypes_wrapper.guac_client_log_handler(log.guacd_client_log))

    proc.process = Process(target=guacd_exec_proc, args=(proc, protocol))
    proc.process.start()

    # Wait for process to be ready
    proc.ready_event.wait(2)
    if proc.ready_event.is_set():
        return proc
    else:
        proc.process.kill()
        proc.process.close()
        return None
