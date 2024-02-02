import asyncio
from ctypes import cast, c_char_p, c_int
from typing import Dict, Optional

import zmq
from zmq.asyncio import Context

from . import libguac_wrapper
from .constants import (
    GuacClientLogLevel, GuacStatus, GUAC_CLIENT_ID_PREFIX, GUACD_USEC_TIMEOUT, GUAC_PROTOCOL_STATUS_RESOURCE_NOT_FOUND
)
from .libguac_wrapper import (
    String, guac_parser_alloc, guac_parser_expect, guac_parser_free, guac_protocol_send_error,
    guac_socket_create_zmq, guac_socket_free
)
from .log import guacd_log, guacd_log_guac_error, guacd_log_handshake_failure
from .proc import GuacdProc


def parse_identifier(zmq_addr: str, existing_client_ids: tuple) -> Optional[str]:
    """Parse the identifier for a new user connection

    Blocking libguac calls are made to do the following:
    - Allocate a new libguac parser
    - Open a ZeroMQ guac_socket
    - Parse identifer on the new guac_socket
    - Close parser
    - Close ZeroMQ guac_socket

    The ZeroMQ guac_socket is not kept because ZeroMQ sockets are not thread safe,
    and this is blocking code intended to be run in an asyncio thread.

    :param zmq_addr:
        ZeroMQ socket address used for connection to the new user.
    :param existing_client_ids:
        The existing client ids from proc_map. This is used if the parsed identifier is a connection id.
        If the identifier connection id is not found then, then an error is sent to the user on the socket.
    :return:
        The identifer string if parsing is successful, otherwise None.
    """

    parser_ptr = guac_parser_alloc()
    parser = parser_ptr.contents

    # Reset guac_error
    libguac_wrapper.__guac_error()[0] = c_int(GuacStatus.GUAC_STATUS_SUCCESS)
    libguac_wrapper.__guac_error_message()[0] = String(b'').raw

    # Open a ZeroMQ guac_socket using libguac call
    guac_sock = guac_socket_create_zmq(zmq.PAIR, zmq_addr, False)

    # Get protocol from select instruction
    parser_result = guac_parser_expect(parser_ptr, guac_sock, c_int(GUACD_USEC_TIMEOUT), String(b'select'))

    if parser_result:
        # Log error
        guacd_log_handshake_failure()
        guacd_log_guac_error(GuacClientLogLevel.GUAC_LOG_ERROR, f'Error reading "select" ({parser_result})')
        ret_val = None

    # Validate args to select
    elif parser.argc != 1:
        # Log error
        guacd_log_handshake_failure()
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Bad number of arguments to "select" ({parser.argc})')
        ret_val = None

    else:
        # Get Python string from libguac parsed value
        identifier = bytes(cast(parser.argv[0], c_char_p).value).decode()

        # If identifier is connection id and not found send error on socket
        if identifier[0] == GUAC_CLIENT_ID_PREFIX and identifier not in existing_client_ids:
            guac_protocol_send_error(guac_sock, "No such connection.", GUAC_PROTOCOL_STATUS_RESOURCE_NOT_FOUND)
        ret_val = identifier

    # Close parser and socket
    guac_parser_free(parser_ptr)
    guac_socket_free(guac_sock)
    return ret_val


async def guacd_route_connection(proc_map: Dict[str, GuacdProc], zmq_addr: str, zmq_context: Context) -> int:
    """Route a Guacamole connection

    Routes the connection on the given socket according to the Guacamole
    protocol, adding new users and creating new client processes as needed. If a
    new process is created, this function blocks until that process terminates,
    automatically deregistering the process at that point.

    The socket provided will be automatically freed when the connection
    terminates unless routing fails, in which case non-zero is returned.

    :param proc_map:
        The map of existing client processes.

    :param zmq_addr:
        ZeroMQ address to create a new guac_socket for the user connection

    :param zmq_context:
        For making ZeroMQ client process connection to send the above zmq_addr

    :return:
        Zero if the connection was successfully routed, non-zero if routing has failed.
    """

    # Run blocking parse_identifier in asyncio thread
    identifier = await asyncio.to_thread(parse_identifier, zmq_addr, tuple(proc_map.keys()))

    if identifier is None:
        return 1

    # If connection ID, retrieve existing process
    if identifier[0] == GUAC_CLIENT_ID_PREFIX:
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, 'Selecting existing connection not implemented')
        return 1

    # Otherwise, create new client
    else:
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Creating new client for protocol "{identifier.decode()}"')

        # Create new client
        guacd_create_client(socket, identifier)

        return 0
