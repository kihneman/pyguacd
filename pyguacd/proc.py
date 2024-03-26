import asyncio
import multiprocessing
import threading
import time
from asyncio.exceptions import CancelledError
from ctypes import CDLL, POINTER, cast, c_char_p, c_int, c_size_t, c_void_p, create_string_buffer, pointer
from dataclasses import dataclass, field
from multiprocessing import Process
from typing import Callable, Dict, Optional

import zmq

from . import libguac_wrapper
from .constants import (
    GuacClientLogLevel, GuacStatus, GUAC_CLIENT_LOG_MESSAGE_LEN, GUAC_CLIENT_PROC_START_TIMEOUT,
    GUACD_DEFAULT_LOG_LEVEL, GUACD_USEC_TIMEOUT
)
from .libguac_wrapper import (
    guac_client, guac_client_alloc, guac_client_free, guac_client_load_plugin, guac_client_log_handler, guac_client_stop,
    guac_socket_create_zmq, guac_socket_free, guac_socket_require_keep_alive,
    guac_user_alloc, guac_user_free, guac_user_handle_connection, String
)
from .log import guacd_log, guacd_log_guac_error
from .utils.ipc_addr import new_ipc_addr


@dataclass
class GuacdProc:
    """Data and methods used by parent and client process similar to C code guacd_proc struct in proc.h"""
    client_ptr: POINTER(guac_client)

    # Temporary directory for securely storing socket files
    tmp_dir: str

    # Same as client connection_id. Repeated here for convenience
    connection_id: Optional[str] = None

    # Map of user socket address to disconnect event
    user_address_to_disconnect_event: Dict[str, asyncio.Event] = field(default_factory=dict)

    # Used by parent to join client process
    process: Optional[Process] = None

    # Indicates when process socket is ready for connections
    ready_event: Optional[multiprocessing.Event] = None

    # Final asyncio task created by GuacdProcMap to clean up after joining process
    cleanup_task: Optional[asyncio.Task] = None
    user_disconnects_task: asyncio.Task = None

    # Process socket ZeroMQ data
    zmq_socket_addr: Optional[str] = None
    zmq_context: Optional[zmq.Context] = None
    zmq_socket: Optional[zmq.Socket] = None

    # Private check if parent has been connected
    _parent_connected = False

    def __post_init__(self):
        self.connection_id = str(self.client_ptr.contents.connection_id)

        # Initialize synchronization vars
        self.ready_event = multiprocessing.Event()

        # Create new ZeroMQ IPC address shared between parent and client process
        self.zmq_socket_addr = new_ipc_addr(self.tmp_dir)

    def bind_client(self):
        """Create zmq_socket and bind client for receiving user socket addresses from parent"""
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.CHANNEL)
        self.zmq_socket.bind(self.zmq_socket_addr)
        self.ready_event.set()

    def connect_parent(self) -> bool:
        """Create zmq_socket and connect parent to client process if process is new

        :return: True if created new connection, otherwise False
        """
        if self._parent_connected:
            return False

        else:
            self.zmq_context = zmq.Context()
            self.zmq_socket = self.zmq_context.socket(zmq.CHANNEL)
            self.zmq_socket.connect(self.zmq_socket_addr)
            self._parent_connected = True
            return True

    async def recv_user_socket_addr(self) -> Optional[str]:
        """Receive new user connection address from parent

        :return: None if asyncio cancel occurs while waiting, otherwise user socket address
        """
        try:
            user_socket_addr = await asyncio.to_thread(self.zmq_socket.recv)
        except CancelledError:
            return None
        else:
            return user_socket_addr.decode()

    async def recv_user_address_disconnects(self):
        while True:
            user_socket_addr = await asyncio.to_thread(self.zmq_socket.recv)
            disconnect = self.user_address_to_disconnect_event.get(user_socket_addr.decode())
            if disconnect is None:
                print('WARNING: Unknown user disconnect received')
            else:
                disconnect.set()

    def send_disconnect_user_addr_from_thread(self, user_socket_addr: str):
        self.zmq_socket.send(user_socket_addr.encode())

    async def send_user_socket_addr(self, zmq_user_addr: str):
        """Send new user connection address to client

        :param zmq_user_addr: New user socket address to send
        """
        await asyncio.to_thread(self.zmq_socket.send, zmq_user_addr.encode())

    def close(self):
        """Close the ZeroMQ socket and destroy context"""
        self.zmq_context.destroy()


class GuacdProcMap:
    """Map of guacd client processes

    This wraps a dictionary but also has thread-safety by using a threading.Lock.
    Furthermore, methods are included for easily adding (connecting), retrieving, and removing client processes.
    """
    def __init__(self):
        self._proc_map: Dict[str, GuacdProc] = dict()
        self._proc_map_lock: threading.Lock = threading.Lock()

    def connect_new_process(self, proc: GuacdProc) -> bool:
        """Connect to process and add to GuacdProcMap if process is new

        :param proc: The client process to check and connect if new
        :return: True if made new connection to process, otherwise False
        """
        if proc.connect_parent():
            with self._proc_map_lock:
                self._proc_map[proc.connection_id] = proc
                return True
        else:
            return False

    def get_process(self, connection_id: str) -> GuacdProc:
        """Get process associated with connection_id

        :param connection_id: The connection id to look for
        :return: The client process associated with connection_id or None if not found
        """
        with self._proc_map_lock:
            return self._proc_map.get(connection_id)

    async def wait_to_remove_process(self, proc: GuacdProc) -> bool:
        """Wait for child process to finish and remove from GuacdProcMap

        :param proc: The process to wait for and remove from GuacdProcMap
        :return: True if removed from GuacdProcMap, otherwise False
        """
        await asyncio.to_thread(proc.process.join)

        with self._proc_map_lock:
            pop_process = self._proc_map.pop(proc.connection_id, None)

        return pop_process is not None


def cleanup_client(client_ptr: POINTER(guac_client)):
    """Stop and free the guac client

    :param client_ptr: Guac client pointer to clean up
    """

    # Request client to stop/disconnect
    guac_client_stop(client_ptr)

    # Attempt to free client cleanly
    guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, 'Requesting termination of client...')

    # Attempt to free client (this may never return if the client is malfunctioning)
    guac_client_free(client_ptr)
    guacd_log(GuacClientLogLevel.GUAC_LOG_DEBUG, 'Client terminated successfully.')


def guacd_user_thread(proc: GuacdProc, owner: int, user_socket_addr: str,
                      guacd_proc_stop_event: threading.Event):
    """Handles a libguac guac_user lifecycle from allocation to guac_user_free

    :param client_ptr:
        Guac client pointer to which the new guac user will connect
    :param owner:
        Whether this user is the owner (1) or not (0)
    :param user_socket_addr:
        The address of the ZeroMQ socket for the user connection
    :param guacd_proc_stop_event:
        Threading event to stop process if this user disconnects and is the last user
    """

    client_ptr = proc.client_ptr
    client = client_ptr.contents

    # Create skeleton user
    user_ptr = guac_user_alloc()
    user = user_ptr.contents
    user.socket = guac_socket_create_zmq(zmq.CHANNEL, user_socket_addr, False)
    user.client = client_ptr
    user.owner = owner

    # Handle user connection from handshake until disconnect/completion
    guac_user_handle_connection(user_ptr, c_int(GUACD_USEC_TIMEOUT))

    # Save user_id before clean-up
    user_id = user.user_id

    # Clean-up
    guac_socket_free(user.socket)
    guac_user_free(user_ptr)

    # Send user disconnect to parent process
    proc.send_disconnect_user_addr_from_thread(user_socket_addr)

    # Stop client and prevent future users if all users are disconnected
    if client.connected_users == 0:
        guacd_log(
            GuacClientLogLevel.GUAC_LOG_INFO, f'Last user of connection "{client.connection_id}" disconnected'
        )
        guacd_proc_stop_event.set()


async def guacd_proc_serve_users(proc: GuacdProc):
    """Continuously serve user connections for this client until last user disconnects

    :param proc: Process data and methods
    """

    # Store asyncio tasks of user threads by the user socket addr
    guacd_user_thread_tasks: Dict[str, asyncio.Task] = dict()

    # Create threading event with awaitable task
    guacd_proc_stop_event = threading.Event()
    guacd_proc_stop_coro = asyncio.to_thread(guacd_proc_stop_event.wait)
    guacd_proc_stop_task = asyncio.create_task(guacd_proc_stop_coro)

    # The first file descriptor is the owner
    owner = 1

    # Bind socket to begin receiving user connections from parent
    proc.bind_client()

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
            guacd_user_thread, proc, owner, user_socket_addr, guacd_proc_stop_event
        )
        guacd_user_thread_tasks[user_socket_addr] = asyncio.create_task(guacd_user_thread_coro, name=user_socket_addr)

        # Future file descriptors are not owners
        owner = 0


def guacd_exec_proc(proc: GuacdProc, protocol: str):
    """
    Starts protocol-specific handling on the given process by loading the client
    plugin for that protocol. This function does NOT return. It initializes the
    process with protocol-specific handlers and then runs until guacd_proc_serve_users()
    completes.

    :param proc:
        The process that any new users received along proc.zmq_socket should be added
        to (after the process has been initialized for the given protocol).
    :param protocol:
        The protocol used to initialize the given process.
    """

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


class GuacClientLog:
    pyguacd_log_level: GuacClientLogLevel = GUACD_DEFAULT_LOG_LEVEL

    def __init__(self):
        libc = CDLL("libc.so.6")
        self.vsnprintf = libc.vsnprintf
        self.vsnprintf.restype = c_int

    def get_log_handler(self):
        @ guac_client_log_handler
        def log_handler(guac_client_ptr: POINTER(guac_client), log_level: c_int, msg: String, args: c_void_p):
            if log_level <= self.pyguacd_log_level:
                message = create_string_buffer(GUAC_CLIENT_LOG_MESSAGE_LEN)
                self.vsnprintf(message, c_size_t(GUAC_CLIENT_LOG_MESSAGE_LEN), msg.raw, cast(args, c_void_p))
                guacd_log(GuacClientLogLevel(log_level), str(String(message)))

        return log_handler


def guacd_create_proc(protocol: str, tmp_dir: str) -> Optional[GuacdProc]:
    """Creates new guacd client process and returns with process info

    :param protocol:
        The protocol used to initialize a new process.

    :param tmp_dir:
        Temporary directory for securely storing socket files

    :return:
        Returns the process info or None if starting the process times out
    """

    # Associate new client
    proc = GuacdProc(guac_client_alloc(), tmp_dir)
    guac_log = GuacClientLog()
    proc.client_ptr.contents.log_handler = guac_log.get_log_handler()

    proc.process = Process(target=guacd_exec_proc, args=(proc, protocol))
    proc.process.start()

    # Wait for process to be ready
    proc.ready_event.wait(GUAC_CLIENT_PROC_START_TIMEOUT)
    if proc.ready_event.is_set():
        return proc
    else:
        proc.process.kill()
        proc.process.close()
        return None
