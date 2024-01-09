import socket
import threading
from ctypes import cast, c_char_p, c_int, POINTER

from . import libguac_wrapper
from .libguac_wrapper import (
    String, guac_parser_alloc, guac_parser_expect, guac_parser_free,
    guac_socket, guac_socket_free, guac_socket_write_string
)
from .client import guacd_create_client
from .proc import GuacdProc, guacd_create_proc
from .constants import GuacClientLogLevel, GuacStatus, GUAC_CLIENT_ID_PREFIX, GUACD_USEC_TIMEOUT
from .log import guacd_log, guacd_log_guac_error, guacd_log_handshake_failure
from .tcp_zmq_proxy import launch_proxy


def guac_socket_cleanup(guac_socket):
    print('Cleaning up guac socket...')
    guac_socket_free(guac_socket)


def guacd_add_user(proc: GuacdProc, parser, gsock, sock) -> int:
    # Wait for process to be ready
    proc.wait_for_process()

    # Send user zmq socket to process
    ipc_socket_path = proc.user_socket_path()
    t = threading.Thread(target=launch_proxy, args=(ipc_socket_path, sock, guac_socket_cleanup, (gsock,)))
    t.start()
    proc.send_new_user_socket()

    # Handle I/O from process to user
    # user_socket = proc.zmq_user_socket
    # data = user_socket.recv()
    # while len(data) > 0:
    #     guac_socket_write_string(gsock, String(data))
    #     data = user_socket.recv()


def guacd_route_connection(gsock: POINTER(guac_socket), sock: socket.socket) -> int:
    """Route a Guacamole connection

    Routes the connection on the given socket according to the Guacamole
    protocol, adding new users and creating new client processes as needed. If a
    new process is created, this function blocks until that process terminates,
    automatically deregistering the process at that point.

    The socket provided will be automatically freed when the connection
    terminates unless routing fails, in which case non-zero is returned.

    @param map
        The map of existing client processes.

    @param gsock
        The socket associated with the new connection that must be routed to
        a new or existing process within the given map.

    @param sock
        Python socket object

    @return
        Zero if the connection was successfully routed, non-zero if routing has
        failed.
    """
    parser_ptr = guac_parser_alloc()
    parser = parser_ptr.contents

    # Reset guac_error
    libguac_wrapper.__guac_error()[0] = c_int(GuacStatus.GUAC_STATUS_SUCCESS)
    libguac_wrapper.__guac_error_message()[0] = String(b'').raw

    # Get protocol from select instruction
    if parser_result := guac_parser_expect(parser_ptr, gsock, c_int(GUACD_USEC_TIMEOUT), String(b'select')):
        # Log error
        guacd_log_handshake_failure()
        guacd_log_guac_error(GuacClientLogLevel.GUAC_LOG_ERROR, f'Error reading "select" ({parser_result})')

        # Extra debug
        if parser.argc == 0:
            guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f"Didn't get any parser args")
        elif parser.argc == 1:
            identifier = cast(parser.argv[0], c_char_p).value
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Received protocol "{identifier}"')
        else:
            argv = [cast(parser.argv[i], c_char_p).value for i in range(parser.argc)] if 1 < parser.argc < 5 else None
            argv_str = f': {argv}' if argv else ''
            guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Received {parser.argc} args but expected 1{argv_str}')

        guac_parser_free(parser_ptr)
        return 1

    # Validate args to select
    if parser.argc != 1:
        # Log error
        guacd_log_handshake_failure()
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Bad number of arguments to "select" ({parser.argc})')
        guac_parser_free(parser_ptr)
        return 1

    identifier: bytes = cast(parser.argv[0], c_char_p).value

    # If connection ID, retrieve existing process
    if identifier[0] == GUAC_CLIENT_ID_PREFIX:
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, 'Selecting existing connection not implemented')
        guac_parser_free(parser_ptr)
        return 1

    # Otherwise, create new client
    else:
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Creating new client for protocol "{identifier.decode()}"')

        # Create new client in the same process
        # guacd_create_client(gsock, identifier)

        # Create new process
        proc = guacd_create_proc(identifier)
        new_process = 1

    guacd_add_user(proc, parser_ptr, gsock, sock)
    guac_parser_free(parser_ptr)
    return 0
