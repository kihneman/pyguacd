import asyncio
import multiprocessing
from asyncio.exceptions import CancelledError
from ctypes import c_int, POINTER
from dataclasses import dataclass
from multiprocessing import Process
from typing import Dict, Optional

import zmq
import zmq.asyncio

from .libguac_wrapper import guac_client
from .utils.ipc_addr import new_ipc_addr, remove_ipc_addr_file


@dataclass
class GuacdProc:
    """Data and methods used by parent and client process similar to C code guacd_proc struct in proc.h"""
    client_ptr: POINTER(guac_client)

    # Prevents simultaneous use of the process socket by multiple users
    lock: Optional[asyncio.Lock] = None

    # Used by parent to join client process
    process: Optional[Process] = None

    # Indicates when process socket is ready for connections
    ready_event: Optional[multiprocessing.Event] = None

    # Final asyncio task created by parent to clean up after joining process
    task: Optional[asyncio.Task] = None

    # Process socket ZeroMQ data
    zmq_socket_addr: Optional[str] = None
    zmq_context: Optional[zmq.asyncio.Context] = None
    zmq_socket: Optional[zmq.asyncio.Socket] = None

    def __post_init__(self):
        # Initialize synchronization vars
        self.lock = asyncio.Lock()
        self.ready_event = multiprocessing.Event()

        # Create new ZeroMQ IPC address shared between parent and client process
        self.zmq_socket_addr = new_ipc_addr()

    def bind_client(self):
        """Create zmq_socket and bind client for receiving user socket addresses from parent"""
        self.zmq_context = zmq.asyncio.Context()
        self.zmq_socket = self.zmq_context.socket(zmq.PAIR)
        self.zmq_socket.bind(self.zmq_socket_addr)
        self.ready_event.set()

    def connect_parent(self, zmq_context: zmq.asyncio.Context):
        """Create zmq_socket and connect parent to client process for sending user socket addresses

        :param zmq_context: parent ZeroMQ context used to create the new socket
        """
        self.zmq_socket = zmq_context.socket(zmq.PAIR)
        self.zmq_socket.connect(self.zmq_socket_addr)

    async def recv_user_socket_addr(self) -> Optional[str]:
        """Receive new user connection address from parent

        :return: None if asyncio cancel occurs while waiting, otherwise user socket address
        """
        try:
            user_socket_addr = await self.zmq_socket.recv()
        except CancelledError:
            return None
        else:
            return user_socket_addr.decode()

    async def send_user_socket_addr(self, zmq_user_addr: str):
        """Send new user connection address to client

        :param zmq_user_addr: New user socket address to send
        """
        async with self.lock:
            await self.zmq_socket.send(zmq_user_addr.encode())

    def close(self):
        """Close the ZeroMQ socket between parent and client"""
        self.zmq_socket.close()

    def remove_socket_file(self):
        """Remove the file for the socket"""
        remove_ipc_addr_file(self.zmq_socket_addr)
