from typing import Optional

from .constants import GuacClientLogLevel, GUAC_CLIENT_ID_PREFIX
from .log import guacd_log
from .parser import parse_identifier
from .proc import guacd_create_proc


def guacd_route_connection(proc_map: dict, zmq_addr: str, identifier: Optional[str] = None) -> int:
    """Route a Guacamole connection

    Routes the connection on the given socket according to the Guacamole
    protocol, adding new users and creating new client processes as needed. If a
    new process is created, this function blocks until that process terminates,
    automatically deregistering the process at that point.

    The socket provided will be automatically freed when the connection
    terminates unless routing fails, in which case non-zero is returned.

    @param proc_map
        The map of existing client processes.

    @param zmq_addr
        ZeroMQ address for use in creating a new guac_socket to the new connection that will be routed

    @param identifier
        Protocol or connection id from parsing select instruction

    @return
        Zero if the connection was successfully routed, non-zero if routing has
        failed.
    """
    if identifier is None:
        identifier = parse_identifier(zmq_addr)

    if identifier is None:
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Invalid connection identifier from parsing "select"')
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

        # Create new process
        proc = guacd_create_proc(identifier)
        if proc is None:
            return 1

        # Add to proc_map
        client_ptr = proc.client_ptr
        client = client_ptr.contents
        proc_map[str(client.connection_id)] = proc

    proc.connect()
    guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connected to "{proc.zmq_socket_addr}"')
    proc.send_user_socket_addr(zmq_addr)
    proc.zmq_socket.close()

    return 0
