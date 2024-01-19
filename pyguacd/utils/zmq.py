from contextlib import contextmanager
from typing import Iterable
from uuid import uuid4

import zmq
import zmq.asyncio
from zmq.devices import ThreadProxy
from zmq.utils.monitor import parse_monitor_message

from ..constants import GUACD_ZMQ_PROXY_CLIENT_SOCKET_PATH, GUACD_ZMQ_PROXY_USER_SOCKET_PATH


async def check_zmq_monitor_events(zmq_monitor: zmq.asyncio.Socket, zmq_events: Iterable[zmq.Event]):
    for expect_event in zmq_events:
        await zmq_monitor.poll()
        mon_msg = parse_monitor_message(await zmq_monitor.recv_multipart())
        event = mon_msg.get('event')
        if event != expect_event:
            event_name = event.name if isinstance(event, zmq.Event) else event
            print(f'Expected "{expect_event.name}" but got "{event_name}"')
            print('ZMQ connection error')
            return False

    return True


def new_ipc_addr(base_path):
    uid = uuid4().hex
    return f'ipc://{base_path}{uid}'


def start_zmq_client_proxy(base_addr=None, pub_sub=False):
    """Connects users to existing clients for sending the user socket address"""

    if pub_sub:
        zmq_router_proxy = ThreadProxy(zmq.XSUB, zmq.XPUB)
    else:
        zmq_router_proxy = ThreadProxy(zmq.PAIR, zmq.PAIR)

    # Users connect to the in port
    if base_addr is None:
        zmq_router_proxy.bind_in(f'ipc://{GUACD_ZMQ_PROXY_USER_SOCKET_PATH}')
    else:
        zmq_router_proxy.bind_in(f'{base_addr}-in')

    # Clients connect to the out port
    if base_addr is None:
        zmq_router_proxy.bind_out(f'ipc://{GUACD_ZMQ_PROXY_CLIENT_SOCKET_PATH}')
    else:
        zmq_router_proxy.bind_out(f'{base_addr}-out')

    zmq_router_proxy.start()
    proxy_context = zmq_router_proxy.context_factory()

    return zmq_router_proxy, proxy_context


@contextmanager
def zmq_client_proxy(*args, **kwargs):
    zmq_router_proxy, proxy_context = start_zmq_client_proxy(*args, **kwargs)
    try:
        yield zmq_router_proxy
    finally:
        proxy_context.destroy()
