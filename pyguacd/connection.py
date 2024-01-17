import socket
import threading
from ctypes import cast, c_char_p, c_int, POINTER
from typing import Optional

import zmq

from . import libguac_wrapper
from .constants import (
    GuacClientLogLevel, GuacStatus, GUAC_CLIENT_ID_PREFIX, GUACD_USEC_TIMEOUT, GUACD_USER_SOCKET_PATH
)
from .libguac_wrapper import (
    String, guac_parser_alloc, guac_parser_expect, guac_parser_free,
    guac_socket, guac_socket_create_zmq, guac_socket_free, guac_socket_write_string
)
from .log import guacd_log, guacd_log_guac_error, guacd_log_handshake_failure
from .parser import parse_identifier
from .proc import guacd_create_proc
from .old.single_connection.client import guacd_create_client


def guac_socket_cleanup(guac_socket):
    print('Cleaning up guac socket...')
    guac_socket_free(guac_socket)


def guacd_route_connection(proc_map: dict, guac_sock: POINTER(guac_socket) = None, zmq_addr: Optional[str] = None) -> int:
    """Route a Guacamole connection

    Routes the connection on the given socket according to the Guacamole
    protocol, adding new users and creating new client processes as needed. If a
    new process is created, this function blocks until that process terminates,
    automatically deregistering the process at that point.

    The socket provided will be automatically freed when the connection
    terminates unless routing fails, in which case non-zero is returned.

    @param proc_map
        The map of existing client processes.

    @param guac_sock
        The socket associated with the new connection that must be routed to
        a new or existing process within the given map.

    @param zmq_addr
        ZeroMQ address for use in creating a new guac_socket to the new connection that will be routed

    @return
        Zero if the connection was successfully routed, non-zero if routing has
        failed.
    """
    if guac_sock is None:
        if zmq_addr:
            guac_sock = guac_socket_create_zmq(zmq.PAIR, zmq_addr, False)
        else:
            print('ERROR: guac_socket or ZMQ address must be provided to guacd_route_connection')

    identifier = parse_identifier(guac_sock)
    if identifier is None:
        return 1

    # If connection ID, retrieve existing process
    if identifier[0] == GUAC_CLIENT_ID_PREFIX:
        proc = proc_map.get(identifier)

        if proc is None:
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection "{identifier}" does not exist')
            return 1
        else:
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Found existing connection "{identifier}"')

    # Otherwise, create new client
    else:
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Creating new client for protocol "{identifier}"')

        if zmq_addr:
            guac_socket_free(guac_sock)
            guac_sock = None

        #     # Create new client in the same process
        #     guacd_create_client(identifier, zmq_addr=zmq_addr)
        # else:
        #     guacd_create_client(identifier, guac_sock)

        # Create new process
        proc = guacd_create_proc(identifier)
        if proc is None:
            return 1
        new_process = 1

        # Add to proc_map
        client_ptr = proc.client_ptr
        client = client_ptr.contents
        proc_map[str(client.connection_id)] = proc

    proc.connect()
    guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connected to "{proc.zmq_socket_addr}"')
    proc.send_user_socket_addr(zmq_addr)
    proc.zmq_socket.close()

    return 0
