import asyncio
from ctypes import cast, c_char_p, c_int
from typing import Dict

import zmq
import zmq.asyncio
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
from .proc import guacd_create_proc, GuacdProc


def parse_identifier(zmq_addr: str, existing_client_ids: tuple):

    parser_ptr = guac_parser_alloc()
    parser = parser_ptr.contents

    # Reset guac_error
    libguac_wrapper.__guac_error()[0] = c_int(GuacStatus.GUAC_STATUS_SUCCESS)
    libguac_wrapper.__guac_error_message()[0] = String(b'').raw

    # Get protocol from select instruction
    guac_sock = guac_socket_create_zmq(zmq.PAIR, zmq_addr, False)
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
        identifier = bytes(cast(parser.argv[0], c_char_p).value).decode()
        if identifier[0] == GUAC_CLIENT_ID_PREFIX and identifier not in existing_client_ids:
            guac_protocol_send_error(guac_sock, "No such connection.", GUAC_PROTOCOL_STATUS_RESOURCE_NOT_FOUND)
        ret_val = identifier

    guac_parser_free(parser_ptr)
    guac_socket_free(guac_sock)
    return ret_val


async def remove_process(proc_map: Dict[str, GuacdProc], connection_id: str):
    proc = proc_map[connection_id]

    # Wait for child to finish
    await asyncio.to_thread(proc.process.join)

    # Remove client
    if proc_map.pop(connection_id, None):
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection "{connection_id}" removed.')

        # Close ZeroMQ socket to previously existing process
        proc.close()
    else:
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection "{connection_id}" does not exist for removal.')


async def guacd_route_connection(proc_map: Dict[str, GuacdProc], zmq_addr: str, zmq_context: Context) -> int:
    """Route a Guacamole connection

    Routes the connection on the given socket according to the Guacamole
    protocol, adding new users and creating new client processes as needed. If a
    new process is created, an asyncio task will be created that waits until that process terminates,
    automatically deregistering the process at that point.

    @param proc_map
        The map of existing client processes.

    @param zmq_addr
        ZeroMQ address to create a new guac_socket for the user connection

    @param zmq_context
        For making ZeroMQ client process connection to send the above zmq_addr

    @return
        Zero if the connection was successfully routed, non-zero if routing has failed.
    """

    identifier = await asyncio.to_thread(parse_identifier, zmq_addr, tuple(proc_map.keys()))

    if identifier is None:
        return 1

    # If connection ID, retrieve existing process
    if identifier[0] == GUAC_CLIENT_ID_PREFIX:
        connection_id = identifier
        proc = proc_map.get(connection_id)

        if proc is None:
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection "{connection_id}" does not exist')
            guacd_log_guac_error(GuacClientLogLevel.GUAC_LOG_INFO, 'Connection did not succeed')
            return 1

        else:
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Joining existing connection "{connection_id}"')

    # Otherwise, create new client
    else:
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Creating new client for protocol "{identifier}"')

        # Create new process
        proc = await asyncio.to_thread(guacd_create_proc, identifier)

        # Abort if no process exists for the requested connection
        if proc is None:
            guacd_log_guac_error(GuacClientLogLevel.GUAC_LOG_INFO, "Connection did not succeed")
            return 1

        # Establish socket connection with process
        proc.connect_user(zmq_context)

        # Log connection ID
        client_ptr = proc.client_ptr
        client = client_ptr.contents
        connection_id = str(client.connection_id)
        guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection ID is "{connection_id}"')

        # Store process, allowing other users to join
        proc_map[connection_id] = proc

        # Add task to join process and wait to remove the process from proc_map
        proc.task = asyncio.create_task(remove_process(proc_map, connection_id))

    # Add new user (in the case of a new process, this will be the owner */
    await proc.send_user_socket_addr(zmq_addr)

    return 0
