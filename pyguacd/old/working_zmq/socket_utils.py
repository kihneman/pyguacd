import socket
from socket import getaddrinfo, getnameinfo

from ...constants import GuacClientLogLevel
from ...log import guacd_log


def get_addresses(host, port):
    """Get addresses for binding"""
    try:
        addresses = getaddrinfo(host, port, family=socket.AF_UNSPEC, type=socket.SOCK_STREAM, proto=socket.IPPROTO_TCP)

    except Exception as e:
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Error parsing given address or port: {e}')
        return None

    else:
        return addresses


def resolve_hostname(socket_address):
    try:
        host_port = getnameinfo(socket_address, socket.NI_NUMERICHOST | socket.NI_NUMERICSERV)

    except Exception as e:
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Unable to resolve host: {e}')
        return False

    else:
        return True


def socket_bind(sock, socket_address):
    try:
        # Allow socket reuse
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Attempt to bind socket to address
        sock.bind(socket_address)

    except Exception as e:
        # Try next address
        return False

    else:
        return True
