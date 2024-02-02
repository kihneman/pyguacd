from typing import Iterable, Optional, Tuple

import zmq
import zmq.asyncio
from zmq.utils.monitor import parse_monitor_message


async def process_monitor_event(zmq_monitor: zmq.asyncio.Socket, expect_event: zmq.Event) -> Optional[str]:
    """Wait for single ZeroMQ socket monitor event and check if the event matches expect_event or not.
    Return an error message if event doesn't match.

    :param zmq_monitor:
        ZeroMQ Socket returned from the get_monitor_socket method of another ZeroMQ Socket object
    :param expect_event:
        The expected zmq.Event
    :param msg:
        The optional message to print if event matches
    :return:
        None if event matches, error message otherwise
    """

    # Wait for and parse the next monitor message
    mon_msg = parse_monitor_message(await zmq_monitor.recv_multipart())

    # Check the event key from the monitor message
    event = mon_msg.get('event')
    if event == expect_event:
        # Return None if event matches
        return None

    else:
        # Handle unexpected event error
        event_name = event.name if isinstance(event, zmq.Event) else event
        error_msg = f'Expected "{expect_event.name}" but got "{event_name}"'
        return error_msg


async def check_zmq_monitor_events(zmq_monitor: zmq.asyncio.Socket, zmq_events: Iterable[zmq.Event]) -> Optional[str]:
    """Wait for multiple ZeroMQ socket events and return an error message if any event doesn't match what is expected.

    :param zmq_monitor:
        ZeroMQ Socket returned from the get_monitor_socket of another ZeroMQ Socket object
    :param zmq_events:
        An iterable of events that are expected
    :return:
        None if all events match, error message of unexpected event otherwise
    """

    for expect_event in zmq_events:
        if error_msg := await process_monitor_event(zmq_monitor, expect_event) is not None:
            return error_msg

    return None
