from contextlib import contextmanager

import zmq
from zmq.devices import ThreadProxy


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
