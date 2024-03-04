import ctypes
from ctypes import POINTER, c_char, c_int, c_size_t
from pathlib import Path

import pytest
import zmq
from zmq.utils.monitor import parse_monitor_message

from pyguacd.libguac_wrapper import (
    String, Structure, guac_socket_create_zmq, guac_socket_free, guac_socket_read, pthread_mutex_t, zsock_t
)


GUAC_SOCKET_OUTPUT_BUFFER_SIZE = 8192


class zmq_msg_t(Structure):
    pass


class guac_socket_zmq_data(Structure):
    pass


guac_socket_zmq_data.__slots__ = [
    'zsock', 'zmq_handle', 'zmq_msg', 'zmq_data_ptr', 'zmq_data_size',
    'written', 'out_buf', 'socket_lock', 'buffer_lock'
]


guac_socket_zmq_data._fields_ = [
    ('zsock', POINTER(zsock_t)),
    ('zmq_handle', POINTER(None)),
    ('zmq_msg', zmq_msg_t),
    ('zmq_data_ptr', String),
    ('zmq_data_size', c_size_t),
    ('written', c_int),
    ('out_buf', c_char * GUAC_SOCKET_OUTPUT_BUFFER_SIZE),
    ('socket_lock', pthread_mutex_t),
    ('buffer_lock', pthread_mutex_t)
]


@pytest.fixture(params=[True, False])
def socket_pair_with_monitor(request, tmp_path):
    ipc_file: Path = tmp_path / 'test_ipc_socket'
    ipc_address = f'ipc://{ipc_file}'
    guac_sock_bind = request.param

    ctx = zmq.Context()
    pyzmq_sock = ctx.socket(zmq.PAIR)
    pyzmq_monitor = pyzmq_sock.get_monitor_socket()

    if guac_sock_bind:
        guac_sock = guac_socket_create_zmq(zmq.PAIR, ipc_address, guac_sock_bind)
        pyzmq_sock.connect(ipc_address)
    else:
        pyzmq_sock.bind(ipc_address)
        guac_sock = guac_socket_create_zmq(zmq.PAIR, ipc_address, guac_sock_bind)

    yield ipc_file, guac_sock_bind, guac_sock, pyzmq_sock, pyzmq_monitor

    guac_socket_free(guac_sock)
    ctx.destroy()


@pytest.mark.parametrize('serverish', [True, False])
def test_guac_socket_create_zmq(tmp_path, serverish):
    # Setup
    ipc_file: Path = tmp_path / 'test_guac_socket_create_zmq_ipc_server'
    ipc_address = f'ipc://{ipc_file}'

    # Test create and free
    guac_sock = guac_socket_create_zmq(zmq.PAIR, ipc_address, serverish)
    if serverish:
        assert ipc_file.exists()
    assert guac_sock is not None
    guac_socket_free(guac_sock)


def test_zmq_guac_socket_connect(socket_pair_with_monitor):
    # Setup
    ipc_file, guac_sock_bind, guac_sock, pyzmq_sock, pyzmq_monitor = socket_pair_with_monitor
    if guac_sock_bind:
        # Events for pyzmq connect to guac_sock bind
        expect_events = [zmq.Event.CONNECTED]
    else:
        # Events for pyzmq bind and accept guac_sock connection
        expect_events = [zmq.Event.LISTENING, zmq.Event.ACCEPTED, zmq.Event.HANDSHAKE_SUCCEEDED]

    # Test connection
    assert ipc_file.exists()
    for expect_event in expect_events:
        try:
            mon_msg = parse_monitor_message(pyzmq_monitor.recv_multipart(flags=zmq.NOBLOCK))
        except zmq.Again:
            pytest.fail(f'Expected event "{expect_event.name}", but no event received')
        else:
            assert mon_msg.get('event') == expect_event
