from uuid import uuid4
from typing import Iterable

import zmq
import zmq.asyncio
from zmq.utils.monitor import parse_monitor_message


async def check_zmq_monitor_events(zmq_monitor: zmq.asyncio.Socket, zmq_events: Iterable[zmq.Event]):
    print('Waiting for connection...')
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
