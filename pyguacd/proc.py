from ctypes import c_int, pointer, POINTER
from dataclasses import dataclass
from enum import Enum
from multiprocessing import Event, Process
from typing import Optional

import zmq

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
from .zmq_utils import new_ipc_addr, ZsockStatus


@dataclass
class GuacdProc:
    """Analogous to guacd_proc struct in proc.h"""
    client_ptr: POINTER(guac_client)
    zmq_socket_addr: str = new_ipc_addr(GUACD_PROCESS_SOCKET_PATH)
    pid: Optional[int] = None
    process: Optional[Process] = None
    zmq_context: Optional[zmq.Context] = None
    zmq_socket: Optional[zmq.Socket] = None

    def bind(self, zmq_context):
        """Create and bind to process zmq_socket

        Not setting the socket property allows this method to be run before copying to another process
        """
        zmq_socket = zmq_context.socket(zmq.PAIR)
        zmq_socket.bind(self.zmq_socket_addr)
        return zmq_socket

    def connect(self, context=None):
        """Create and connect to process zmq_socket"""
        self.zmq_context = zmq.Context() if context is None else context
        self.zmq_socket = self.zmq_context.socket(zmq.PAIR)
        self.zmq_socket.connect(self.zmq_socket_addr)

    def client_ready(self):
        """Send process ready over socket"""
        self.zmq_socket.send_multipart((b'status', ZsockStatus.CLIENT_READY.value))

    def recv_user_socket_addr(self):
        user_socket_addr = self.zmq_socket.recv()
        # resp_status = ZsockStatus.USER_SOCKET_RECV if user_socket_path else ZsockStatus.USER_SOCKET_ERROR
        # self.zmq_socket.send_multipart({b'status': resp_status})
        return user_socket_addr

    # def send_new_user_socket(self, create_zsock=False):
    #     user_socket_path = self.set_user_socket_path()
    #     if create_zsock:
    #         self.zmq_user_socket = self.zmq_context.socket(zmq.PAIR)
    #         self.zmq_user_socket.bind(user_socket_path)
    #     self.zmq_socket.send_json({'user_socket_path': user_socket_path})
    #     self.wait_for_status(ZsockStatus.USER_SOCKET_RECV)
    #     return user_socket_path


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
    # Connect to socket for receiving new users
    proc.connect()

    # Temp debug for new add user
    proc.client_ready()
    user_socket_addr = proc.recv_user_socket_addr()
    print(f'Received user socket address "{user_socket_addr}"')
    return

    client_ptr = proc.client_ptr
    client = client_ptr.contents

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

    proc.client_ready()
    # Add each received file descriptor as a new user
    # while received_fd := guacd_recv_fd(fd_socket) != -1:
    #     guacd_proc_add_user(proc, received_fd, owner)

    #     # Future file descriptors are not owners
    #     owner = 0

    # Create skeleton user (guacd_user_thread())
    user_ptr = guac_user_alloc()
    user = user_ptr.contents
    user_socket_path = proc.recv_user_socket_path()
    user.socket = guac_socket_create_zmq(zmq.PAIR, user_socket_path, False)
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


def guacd_create_proc(protocol: bytes, zmq_context):
    # Associate new client
    proc = GuacdProc(guac_client_alloc())
    zmq_context, zmq_socket = proc.bind(zmq_context)

    # Init logging
    # client.log_handler = pointer(ctypes_wrapper.guac_client_log_handler(log.guacd_client_log))

    proc.process = Process(target=guacd_exec_proc, args=(proc, protocol))
    proc.process.start()

    # Set properties not passed to new process
    proc.zmq_context = zmq_context
    proc.zmq_socket = zmq_socket
    return proc
