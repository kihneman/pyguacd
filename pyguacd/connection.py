import asyncio
from ctypes import cast, c_char_p, c_int
from typing import Optional

import zmq

from . import libguac_wrapper
from .constants import (
    GuacClientLogLevel, GuacStatus, GUAC_CLIENT_ID_PREFIX, GUACD_USEC_TIMEOUT, GUAC_PROTOCOL_STATUS_RESOURCE_NOT_FOUND
)
from .libguac_wrapper import (
    guac_parser_alloc, guac_parser_expect, guac_parser_free, guac_protocol_send_error,
    guac_socket_create_zmq, guac_socket, guac_socket_free, POINTER, String
)
from .log import guacd_log, guacd_log_guac_error, guacd_log_handshake_failure
from .proc import guacd_create_proc, GuacdProc, GuacdProcMap


def get_client_proc(proc_map: GuacdProcMap, zmq_addr: str) -> Optional[GuacdProc]:
    """Get or create the client process and return corresponding GuacdProc if successful

    :param proc_map:
        The map of existing client processes.

    :param zmq_addr:
        ZeroMQ address to create a new guac_socket for the user connection

    :return:
        The GuacdProc for the client process if successful, otherwise None
    """

    # Open a ZeroMQ guac_socket and parse identifier
    guac_sock = guac_socket_create_zmq(zmq.PAIR, zmq_addr, False)
    identifier = parse_identifier(guac_sock)

    if identifier is None:
        proc = None

    # If connection ID, retrieve existing process
    elif identifier[0] == GUAC_CLIENT_ID_PREFIX:
        proc = proc_map.get_process(identifier)

        # Warn and ward off client if requested connection does not exist
        if proc is None:
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection "{identifier}" does not exist')
            guac_protocol_send_error(guac_sock, "No such connection.", GUAC_PROTOCOL_STATUS_RESOURCE_NOT_FOUND)

        else:
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Joining existing connection "{identifier}"')

        guac_socket_free(guac_sock)

    # Otherwise, create new client
    else:
        guac_socket_free(guac_sock)

        # Create new process
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Creating new client for protocol "{identifier}"')
        proc = guacd_create_proc(identifier)

    return proc


def parse_identifier(guac_sock: POINTER(guac_socket)) -> Optional[str]:
    """Parse the identifier for a new user connection and return the identifier if successful

    :param guac_sock:
        Pointer to libguac ZeroMQ guac_socket
    :return:
        The identifer string if parsing is successful, otherwise None
    """

    parser_ptr = guac_parser_alloc()
    parser = parser_ptr.contents

    # Reset guac_error
    libguac_wrapper.__guac_error()[0] = c_int(GuacStatus.GUAC_STATUS_SUCCESS)
    libguac_wrapper.__guac_error_message()[0] = String(b'').raw

    # Get protocol from select instruction
    parser_result = guac_parser_expect(parser_ptr, guac_sock, c_int(GUACD_USEC_TIMEOUT), String(b'select'))

    if parser_result:
        # Log error
        guacd_log_handshake_failure()
        guacd_log_guac_error(GuacClientLogLevel.GUAC_LOG_ERROR, f'Error reading "select" ({parser_result})')
        identifier = None

    # Validate args to select
    elif parser.argc != 1:
        # Log error
        guacd_log_handshake_failure()
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Bad number of arguments to "select" ({parser.argc})')
        identifier = None

    else:
        # Get Python string from libguac parsed value
        identifier = bytes(cast(parser.argv[0], c_char_p).value).decode()

    # Close parser
    guac_parser_free(parser_ptr)
    return identifier


async def wait_for_process_cleanup(proc_map: GuacdProcMap, proc: GuacdProc):
    """Wait for client process to finish and cleanup

    :param proc_map:
        The map of existing client processes from which the process will be removed
    :param proc:
        The client process that will be removed and cleaned up
    """

    if await proc_map.wait_to_remove_process(proc):
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection "{proc.connection_id}" removed.')

        # Close ZeroMQ socket and remove ipc file to previously existing process
        proc.close()
        proc.remove_socket_file()

    else:
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection "{proc.connection_id}" does not exist for removal.')


async def guacd_route_connection(proc_map: GuacdProcMap, zmq_addr: str) -> int:
    """Route a Guacamole connection

    Routes the connection on the given socket according to the Guacamole
    protocol, adding new users and creating new client processes as needed.

    A socket on the provided address will be created and automatically freed when the connection terminates.

    :param proc_map:
        The map of existing client processes.

    :param zmq_addr:
        ZeroMQ address to create a new guac_socket for the user connection

    :return:
        Zero if the connection was successfully routed, non-zero if routing has failed.
    """

    proc: Optional[GuacdProc] = await asyncio.to_thread(get_client_proc, proc_map, zmq_addr)

    # Abort if no process exists for the requested connection
    if proc is None:
        guacd_log_guac_error(GuacClientLogLevel.GUAC_LOG_INFO, "Connection did not succeed")
        return 1

    # If new process was created, manage that process
    if proc_map.connect_new_process(proc):
        # Log connection ID
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection ID is "{proc.connection_id}"')

        # Add task to join process and wait to remove the process from proc_map
        proc.task = asyncio.create_task(wait_for_process_cleanup(proc_map, proc))

    # Add new user (in the case of a new process, this will be the owner)
    await proc.send_user_socket_addr(zmq_addr)

    return 0
