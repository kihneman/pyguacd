import socket
from socket import getaddrinfo, getnameinfo

from .conf import guacd_conf_parse_args
from .connection import guacd_route_connection
from .constants import EXIT_FAILURE, GuacClientLogLevel
from .libguac_wrapper import guac_socket_free, guac_socket_open
from .log import guacd_log


def main():
    # Load configuration
    config = guacd_conf_parse_args()
    if config is None:
        exit(EXIT_FAILURE)

    # Log start
    guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, 'Guacamole proxy daemon (guacd) started')

    # Get addresses for binding
    try:
        addresses = getaddrinfo(
            config.bind_host, config.bind_port,
            family=socket.AF_UNSPEC, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP
        )
    except Exception as e:
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Error parsing given address or port: {e}')
        exit(EXIT_FAILURE)

    # Attempt binding of each address until success
    current_address = None
    for current_address in addresses:
        # Resolve hostname
        try:
            bound_result = getnameinfo(current_address[-1], socket.NI_NUMERICHOST | socket.NI_NUMERICSERV)
        except Exception as e:
            guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Unable to resolve host: {e}')
            continue
        else:
            bound_address, bound_port = bound_result

        # Get socket
        guac_socket = None
        with socket.socket(current_address[0], socket.SOCK_STREAM) as s:
            try:
                # Allow socket reuse
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                # Attempt to bind socket to address
                s.bind(current_address[-1])

            except Exception as e:
                # Try next address
                continue

            # Log listening status
            guacd_log(
                GuacClientLogLevel.GUAC_LOG_INFO,
                f'Listening on host "{bound_address}", port {bound_port}'
            )

            # Listen for connections
            try:
                s.listen()
            except Exception as e:
                guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Could not listen on socket: {e}')
                exit(3)

            # Accept connection
            conn, addr = s.accept()
            with conn:
                guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Connection made by {addr}')
                guac_socket = guac_socket_open(conn.fileno())
                guacd_route_connection(conn, guac_socket)

        if guac_socket:
            guac_socket_free(guac_socket)
        break

    else:
        # If unable to bind to anything, fail
        address_host_port = [a[-1] for a in addresses]
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f"Couldn't bind to addresses: {address_host_port}")

    input('Press key to exit')


main()
