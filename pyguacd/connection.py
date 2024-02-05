import asyncio
import threading
from ctypes import cast, c_char_p, c_int
from typing import Dict, Optional

import zmq
from zmq.asyncio import Context

from . import libguac_wrapper
from .constants import (
    GuacClientLogLevel, GuacStatus, GUAC_CLIENT_ID_PREFIX, GUACD_USEC_TIMEOUT, GUAC_PROTOCOL_STATUS_RESOURCE_NOT_FOUND
)
from .libguac_wrapper import (
    guac_parser_alloc, guac_parser_expect, guac_parser_free, guac_protocol_send_error,
    guac_socket_create_zmq, guac_socket, guac_socket_free, POINTER, String
)
from .log import guacd_log, guacd_log_guac_error, guacd_log_handshake_failure
from .proc import guacd_create_proc, GuacdProc


def get_client_proc(proc_map: Dict[str, GuacdProc], proc_map_lock: threading.Lock, zmq_addr: str) -> Optional[GuacdProc]:
    """Get or create the client process and return corresponding GuacdProc if successful

    :param proc_map:
        The map of existing client processes.

    :param proc_map_lock:
        Threading lock for controlling access to proc_map

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
        with proc_map_lock:
            proc = proc_map.get(identifier)

        # Warn and ward off client if requested connection does not exist
        if proc is None:
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection "{identifier}" does not exist')
            guac_protocol_send_error(guac_sock, "No such connection.", GUAC_PROTOCOL_STATUS_RESOURCE_NOT_FOUND)
            guacd_log_guac_error(GuacClientLogLevel.GUAC_LOG_INFO, 'Connection did not succeed')

        else:
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Joining existing connection "{identifier}"')

    # Otherwise, create new client
    else:
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Creating new client for protocol "{identifier}"')

        # Create new process
        proc = guacd_create_proc(identifier)

    guac_socket_free(guac_sock)
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


async def wait_for_process_cleanup(proc_map: Dict[str, GuacdProc], connection_id: str):
    """Wait for client process to finish and cleanup

    :param proc_map:
        The map of existing client processes from which the connection_id will be removed
    :param connection_id:
        The connection id of the client process that will be removed and cleaned up
    """

    proc = proc_map[connection_id]

    # Wait for child process to finish
    await asyncio.to_thread(proc.process.join)

    # Remove client
    if proc_map.pop(connection_id, None):
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection "{connection_id}" removed.')

        # Close ZeroMQ socket and remove ipc file to previously existing process
        proc.close()
        proc.remove_socket_file()
    else:
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection "{connection_id}" does not exist for removal.')


async def guacd_route_connection(proc_map: Dict[str, GuacdProc], proc_map_lock: threading.Lock, zmq_addr: str) -> int:
    """Route a Guacamole connection

    Routes the connection on the given socket according to the Guacamole
    protocol, adding new users and creating new client processes as needed.

    A socket on the provided address will be created and automatically freed when the connection terminates.

    :param proc_map:
        The map of existing client processes.

    :param proc_map_lock:
        Threading lock for controlling access to proc_map

    :param zmq_addr:
        ZeroMQ address to create a new guac_socket for the user connection

    :return:
        Zero if the connection was successfully routed, non-zero if routing has failed.
    """

    proc: Optional[GuacdProc] = await asyncio.to_thread(get_client_proc, proc_map, proc_map_lock, zmq_addr)

    # Abort if no process exists for the requested connection
    if proc is None:
        guacd_log_guac_error(GuacClientLogLevel.GUAC_LOG_INFO, "Connection did not succeed")
        return 1

    # If new process was created, manage that process
    if proc.new_process:

        # Establish socket connection with process
        proc.connect_parent()

        # Log connection ID
        client_ptr = proc.client_ptr
        client = client_ptr.contents
        connection_id = str(client.connection_id)
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection ID is "{connection_id}"')

        # Store process, allowing other users to join
        proc_map[connection_id] = proc

        # Add task to join process and wait to remove the process from proc_map
        proc.task = asyncio.create_task(wait_for_process_cleanup(proc_map, connection_id))

        # Finished managing new process
        proc.new_process = False

    # Add new user (in the case of a new process, this will be the owner)
    await proc.send_user_socket_addr(zmq_addr)

    return 0
