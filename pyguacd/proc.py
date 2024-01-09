from ctypes import c_int, pointer, POINTER
from dataclasses import dataclass
from multiprocessing import Process
from typing import Optional
from uuid import uuid4

import zmq
from zmq import Context, Socket

from . import libguac_wrapper, log
from .libguac_wrapper import (
    String, guac_client, guac_client_alloc, guac_client_free, guac_client_load_plugin, guac_client_stop,
    guac_socket, guac_socket_create_zmq, guac_socket_require_keep_alive,
    guac_user_alloc, guac_user_free, guac_user_handle_connection
)
from .constants import (
    GuacClientLogLevel, GuacStatus, GUACD_PROCESS_SOCKET_PATH, GUACD_USER_SOCKET_PATH, GUACD_USEC_TIMEOUT
)
from .log import guacd_log, guacd_log_guac_error


@dataclass
class GuacdProc:
    client_ptr: POINTER(guac_client)
    pid: Optional[int] = None
    process: Optional[Process] = None
    user_socket_path: Optional[str] = None
    zmq_context: Optional[Context] = None
    zmq_socket: Optional[Socket] = None
    zmq_user_socket: Optional[Socket] = None

    def addr(self):
        client_connection_digits = self.client_ptr.contents.connection_id[1:]
        return f'ipc://{GUACD_PROCESS_SOCKET_PATH}{client_connection_digits}'

    def bind_process(self):
        """Bind socket for process receiving user connections"""
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PAIR)
        self.zmq_socket.bind(self.addr())

    def connect_user(self):
        """Connect user to process socket"""
        self.zmq_context = zmq.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PAIR)
        self.zmq_socket.connect(self.addr())

    def process_ready(self):
        """Send process ready over socket"""
        self.zmq_socket.send_json({'status': 'ready'})

    def send_new_user_socket(self, create_zsock=False):
        user_socket_path = self.set_user_socket_path()
        if create_zsock:
            self.zmq_user_socket = self.zmq_context.socket(zmq.PAIR)
            self.zmq_user_socket.bind(user_socket_path)
        self.zmq_socket.send_string(user_socket_path)

    def set_user_socket_path(self):
        uid = uuid4().hex
        self.user_socket_path = f'ipc//{GUACD_USER_SOCKET_PATH}{uid}'
        return self.user_socket_path

    def wait_for_process(self):
        """Wait for process to be ready to receive user connection"""
        msg = self.zmq_socket.recv_json()
        msg_status = msg.get('status', None)
        if msg_status != 'ready':
            guacd_log(
                GuacClientLogLevel.GUAC_LOG_WARNING, f'Unexpected status "{msg_status}" waiting for guacd process'
            )


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


def guacd_exec_proc(proc: GuacdProc, protocol: bytes):
    client_ptr = proc.client_ptr
    client = client_ptr.contents

    # Bind socket for receiving new users
    proc.bind_process()

    # Init client for selected protocol
    if guac_client_load_plugin(client_ptr, String(protocol)):
        # Log error
        guac_error = libguac_wrapper.__guac_error()[0]
        if guac_error == GuacStatus.GUAC_STATUS_NOT_FOUND:
            guacd_log(
                GuacClientLogLevel.GUAC_LOG_WARNING, f'Support for protocol "{protocol.decode()}" is not installed'
            )
        else:
            guacd_log_guac_error(GuacClientLogLevel.GUAC_LOG_ERROR, 'Unable to load client plugin')

        cleanup_client(client_ptr)
    else:
        # Extra debug
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Loaded plugin for connection id "{client.connection_id}"')

    # The first file descriptor is the owner
    owner = 1

    # Enable keep alive on the broadcast socket
    client_socket_ptr = client.socket
    guac_socket_require_keep_alive(client_socket_ptr)

    # Add each received file descriptor as a new user
    # while received_fd := guacd_recv_fd(fd_socket) != -1:
    #     guacd_proc_add_user(proc, received_fd, owner)

    #     # Future file descriptors are not owners
    #     owner = 0

    # Create skeleton user (guacd_user_thread())
    user_ptr = guac_user_alloc()
    user = user_ptr.contents
    user.socket = guac_socket_create_zmq(zmq.PAIR, proc.user_socket_path(), False)
    user.client = client_ptr
    user.owner = 1
    # Extra debug
    guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Created user id "{user.user_id}"')

    # Handle user connection from handshake until disconnect/completion
    guac_user_handle_connection(user_ptr, c_int(GUACD_USEC_TIMEOUT))

    # Stop client and prevent future users if all users are disconnected
    if client.connected_users == 0:
        guacd_log(
            GuacClientLogLevel.GUAC_LOG_INFO, f'Last user of connection "{client.connection_id}" disconnected'
        )

    # Clean up
    guac_user_free(user_ptr)
    cleanup_client(client_ptr)


def guacd_create_proc(protocol: bytes):
    # Associate new client
    proc = GuacdProc(guac_client_alloc())

    # Init logging
    # client.log_handler = pointer(ctypes_wrapper.guac_client_log_handler(log.guacd_client_log))

    proc.process = Process(target=guacd_exec_proc, args=(proc, protocol))
    proc.process.start()
    return proc
