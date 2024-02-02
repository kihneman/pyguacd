# Copyright (c) 2024 Keeper Security, Inc. All rights reserved.
#
# Unless otherwise agreed in writing, this software and any associated
# documentation files (the "Software") may be used and distributed solely
# in accordance with the Keeper Connection Manager EULA:
#
#     https://www.keepersecurity.com/termsofuse.html?t=k
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
from uuid import uuid4

from ..constants import GUACD_SOCKET_DIR


def new_ipc_addr() -> str:
    """Create a new random ZeroMQ IPC address in GUACD_SOCKET_DIR

    :return: Returns the new IPC address as a string, e.g. ipc:///tmp/ipc/a2812a0d1aad435cb83d043dae5a935a
    """
    uid = uuid4().hex
    file_path = os.path.join(GUACD_SOCKET_DIR, uid)
    return f'ipc://{file_path}'


def remove_ipc_addr_file(ipc_addr: str):
    """Remove the ZeroMQ IPC address file for clean-up after socket is closed

    :param ipc_addr: The IPC address of the socket that has been closed,
        e.g. ipc:///tmp/ipc/a2812a0d1aad435cb83d043dae5a935a
    """
    if ipc_addr.startswith('ipc://'):
        os.remove(ipc_addr[len('ipc://'):])
