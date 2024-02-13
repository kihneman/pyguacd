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
from enum import auto, IntEnum
from os.path import dirname, expanduser, join


EXIT_SUCCESS = 0
EXIT_FAILURE = 1
GUACD_LOG_NAME = 'guacd'

# The character prefix which identifies a client ID.
GUAC_CLIENT_ID_PREFIX = '$'

# Time in seconds to wait for client process to startup before timeout
GUAC_CLIENT_PROC_START_TIMEOUT = 2

# The default host that guacd should bind to, if no other host is explicitly specified.
GUACD_DEFAULT_BIND_HOST = '0.0.0.0'

# The default port that guacd should bind to, if no other port is explicitly specified.
GUACD_DEFAULT_BIND_PORT = 4822

# Directory for *.so library files
GUACD_LIB_DIR = join(dirname(__file__), 'libguac')

# Unix Domain Socket file constants
GUACD_SOCKET_DEFAULT_DIR = join(expanduser('~'), '.pyguacd', 'ipc')
GUACD_SOCKET_DIR = os.environ.get('GUACD_SOCKET_DIR', GUACD_SOCKET_DEFAULT_DIR)

# The number of milliseconds to wait for messages in any phase before
# timing out and closing the connection with an error.
GUACD_TIMEOUT = 15000

# The number of microseconds to wait for messages in any phase before
# timing out and closing the conncetion with an error. This is always
# equal to GUACD_TIMEOUT * 1000.
GUACD_USEC_TIMEOUT = (GUACD_TIMEOUT*1000)

# The operation could not be performed as the requested resource does not exist.
GUAC_PROTOCOL_STATUS_RESOURCE_NOT_FOUND = 0x0204

# Error strings
GUAC_STATUS_SUCCESS_STR           = "Success"
GUAC_STATUS_NO_MEMORY_STR         = "Insufficient memory"
GUAC_STATUS_CLOSED_STR            = "Closed"
GUAC_STATUS_TIMEOUT_STR           = "Timed out"
GUAC_STATUS_IO_ERROR_STR          = "Input/output error"
GUAC_STATUS_INVALID_ARGUMENT_STR  = "Invalid argument"
GUAC_STATUS_INTERNAL_ERROR_STR    = "Internal error"
GUAC_STATUS_UNKNOWN_STATUS_STR    = "UNKNOWN STATUS CODE"
GUAC_STATUS_NO_SPACE_STR          = "Insufficient space"
GUAC_STATUS_INPUT_TOO_LARGE_STR   = "Input too large"
GUAC_STATUS_RESULT_TOO_LARGE_STR  = "Result too large"
GUAC_STATUS_PERMISSION_DENIED_STR = "Permission denied"
GUAC_STATUS_BUSY_STR              = "Resource busy"
GUAC_STATUS_NOT_AVAILABLE_STR     = "Resource not available"
GUAC_STATUS_NOT_SUPPORTED_STR     = "Not supported"
GUAC_STATUS_NOT_INPLEMENTED_STR   = "Not implemented"
GUAC_STATUS_TRY_AGAIN_STR         = "Temporary failure"
GUAC_STATUS_PROTOCOL_ERROR_STR    = "Protocol violation"
GUAC_STATUS_NOT_FOUND_STR         = "Not found"
GUAC_STATUS_CANCELED_STR          = "Canceled"
GUAC_STATUS_OUT_OF_RANGE_STR      = "Value out of range"
GUAC_STATUS_REFUSED_STR           = "Operation refused"
GUAC_STATUS_TOO_MANY_STR          = "Insufficient resources"
GUAC_STATUS_WOULD_BLOCK_STR       = "Operation would block"
GUAC_STATUS_ERRNO                 = "Error number needs to be checked"


class GuacClientLogLevel(IntEnum):
    """
    All supported log levels used by the logging subsystem of each Guacamole
    client. With the exception of GUAC_LOG_TRACE, these log levels correspond to
    a subset of the log levels defined by RFC 5424.
    """
    # Fatal errors.
    GUAC_LOG_ERROR = 3

    # Non-fatal conditions that indicate problems.
    GUAC_LOG_WARNING = 4

    # Informational messages of general interest to users or administrators.
    GUAC_LOG_INFO = 6

    # Informational messages which can be useful for debugging, but are
    # otherwise not useful to users or administrators. It is expected that
    # debug level messages, while verbose, will not negatively affect
    # performance.
    GUAC_LOG_DEBUG = 7
    # Hack to easily show debug messages
    # GUAC_LOG_DEBUG = GUAC_LOG_INFO

    # Informational messages which can be useful for debugging, like
    # GUAC_LOG_DEBUG, but which are so low-level that they may affect
    # performance.
    GUAC_LOG_TRACE = 8


class GuacClientState(IntEnum):
    """
    Possible current states of the Guacamole client. Currently, the only
    two states are GUAC_CLIENT_RUNNING and GUAC_CLIENT_STOPPING.
    """

    # The state of the client from when it has been allocated by the main
    # daemon until it is killed or disconnected.
    GUAC_CLIENT_RUNNING = 0

    # The state of the client when a stop has been requested, signalling the
    # I/O threads to shutdown.
    GUAC_CLIENT_STOPPING = auto()


class GuacProtocolVersion(IntEnum):
    """
    The set of protocol versions known to guacd to handle negotiation or feature
    support between differing versions of Guacamole clients and guacd.
    """
    # An unknown version of the Guacamole protocol.
    GUAC_PROTOCOL_VERSION_UNKNOWN = 0x000000

    # Original protocol version 1.0.0, which lacks support for negotiating
    # parameters and protocol version, and requires that parameters in the
    # client/server handshake be delivered in order.
    GUAC_PROTOCOL_VERSION_1_0_0 = 0x010000

    # Protocol version 1.1.0, which includes support for parameter and version
    # negotiation and for sending timezone information from the client
    # to the server.
    GUAC_PROTOCOL_VERSION_1_1_0 = 0x010100

    # Protocol version 1.3.0, which supports the "required" instruction,
    # allowing connections in guacd to request information from the client and
    # await a response.
    GUAC_PROTOCOL_VERSION_1_3_0 = 0x010300

    # Protocol version 1.5.0, which supports the "msg" instruction, allowing
    # messages to be sent to the client, and adds support for the "name"
    # handshake instruction.
    GUAC_PROTOCOL_VERSION_1_5_0 = 0x010500


class GuacStatus(IntEnum):
    # No errors occurred and the operation was successful.
    GUAC_STATUS_SUCCESS = 0

    # Insufficient memory to complete the operation.
    GUAC_STATUS_NO_MEMORY = auto()

    # The resource associated with the operation can no longer be used as it
    # has reached the end of its normal lifecycle.
    GUAC_STATUS_CLOSED = auto()

    # Time ran out before the operation could complete.
    GUAC_STATUS_TIMEOUT = auto()

    # An error occurred, and further information about the error is already
    # stored in errno.
    GUAC_STATUS_SEE_ERRNO = auto()

    # An I/O error prevented the operation from succeeding.
    GUAC_STATUS_IO_ERROR = auto()

    # The operation could not be performed because an invalid argument was
    # given.
    GUAC_STATUS_INVALID_ARGUMENT = auto()

    # The operation failed due to a bug in the software or a serious system
    # problem.
    GUAC_STATUS_INTERNAL_ERROR = auto()

    # Insufficient space remaining to complete the operation.
    GUAC_STATUS_NO_SPACE = auto()

    # The operation failed because the input provided is too large.
    GUAC_STATUS_INPUT_TOO_LARGE = auto()

    # The operation failed because the result could not be stored in the
    # space provided.
    GUAC_STATUS_RESULT_TOO_LARGE = auto()

    # Permission was denied to perform the operation.
    GUAC_STATUS_PERMISSION_DENIED = auto()

    # The operation could not be performed because associated resources are
    # busy.
    GUAC_STATUS_BUSY = auto()

    # The operation could not be performed because, while the associated
    # resources do exist, they are not currently available for use.
    GUAC_STATUS_NOT_AVAILABLE = auto()

    # The requested operation is not supported.
    GUAC_STATUS_NOT_SUPPORTED = auto()

    # Support for the requested operation is not yet implemented.
    GUAC_STATUS_NOT_INPLEMENTED = auto()

    # The operation is temporarily unable to be performed, but may succeed if
    # reattempted.
    GUAC_STATUS_TRY_AGAIN = auto()

    # A violation of the Guacamole protocol occurred.
    GUAC_STATUS_PROTOCOL_ERROR = auto()

    # The operation could not be performed because the requested resources do
    # not exist.
    GUAC_STATUS_NOT_FOUND = auto()

    # The operation was canceled prior to completion.
    GUAC_STATUS_CANCELED = auto()

    # The operation could not be performed because input values are outside
    # the allowed range.
    GUAC_STATUS_OUT_OF_RANGE = auto()

    # The operation could not be performed because access to an underlying
    # resource is explicitly not allowed, though not necessarily due to
    # permissions.
    GUAC_STATUS_REFUSED = auto()

    # The operation failed because too many resources are already in use.
    GUAC_STATUS_TOO_MANY = auto()

    # The operation was not performed because it would otherwise block.
    GUAC_STATUS_WOULD_BLOCK = auto()


guac_status_to_string = {
    # No error
    GuacStatus.GUAC_STATUS_SUCCESS: GUAC_STATUS_SUCCESS_STR,

    # Out of memory
    GuacStatus.GUAC_STATUS_NO_MEMORY: GUAC_STATUS_NO_MEMORY_STR,

    # End of stream
    GuacStatus.GUAC_STATUS_CLOSED: GUAC_STATUS_CLOSED_STR,

    # Timeout
    GuacStatus.GUAC_STATUS_TIMEOUT: GUAC_STATUS_TIMEOUT_STR,

    # Further information in errno
    GuacStatus.GUAC_STATUS_SEE_ERRNO: GUAC_STATUS_ERRNO,

    # Input/output error
    GuacStatus.GUAC_STATUS_IO_ERROR: GUAC_STATUS_IO_ERROR_STR,

    # Invalid argument
    GuacStatus.GUAC_STATUS_INVALID_ARGUMENT: GUAC_STATUS_INVALID_ARGUMENT_STR,

    # Internal error
    GuacStatus.GUAC_STATUS_INTERNAL_ERROR: GUAC_STATUS_INTERNAL_ERROR_STR,

    # Out of space
    GuacStatus.GUAC_STATUS_NO_SPACE: GUAC_STATUS_NO_SPACE_STR,

    # Input too large
    GuacStatus.GUAC_STATUS_INPUT_TOO_LARGE: GUAC_STATUS_INPUT_TOO_LARGE_STR,

    # Result too large
    GuacStatus.GUAC_STATUS_RESULT_TOO_LARGE: GUAC_STATUS_RESULT_TOO_LARGE_STR,

    # Permission denied
    GuacStatus.GUAC_STATUS_PERMISSION_DENIED: GUAC_STATUS_PERMISSION_DENIED_STR,

    # Resource is busy
    GuacStatus.GUAC_STATUS_BUSY: GUAC_STATUS_BUSY_STR,

    # Resource not available
    GuacStatus.GUAC_STATUS_NOT_AVAILABLE: GUAC_STATUS_NOT_AVAILABLE_STR,

    # Not supported
    GuacStatus.GUAC_STATUS_NOT_SUPPORTED: GUAC_STATUS_NOT_SUPPORTED_STR,

    # Not implemented
    GuacStatus.GUAC_STATUS_NOT_INPLEMENTED: GUAC_STATUS_NOT_INPLEMENTED_STR,

    # Temporary failure
    GuacStatus.GUAC_STATUS_TRY_AGAIN: GUAC_STATUS_TRY_AGAIN_STR,

    # Guacamole protocol error
    GuacStatus.GUAC_STATUS_PROTOCOL_ERROR: GUAC_STATUS_PROTOCOL_ERROR_STR,

    # Resource not found
    GuacStatus.GUAC_STATUS_NOT_FOUND: GUAC_STATUS_NOT_FOUND_STR,

    # Operation canceled
    GuacStatus.GUAC_STATUS_CANCELED: GUAC_STATUS_CANCELED_STR,

    # Value out of range
    GuacStatus.GUAC_STATUS_OUT_OF_RANGE: GUAC_STATUS_OUT_OF_RANGE_STR,

    # Operation refused
    GuacStatus.GUAC_STATUS_REFUSED: GUAC_STATUS_REFUSED_STR,

    # Too many resource in use
    GuacStatus.GUAC_STATUS_TOO_MANY: GUAC_STATUS_TOO_MANY_STR,

    # Operation would block
    GuacStatus.GUAC_STATUS_WOULD_BLOCK: GUAC_STATUS_WOULD_BLOCK_STR,

    # Unknown status code
    None: GUAC_STATUS_UNKNOWN_STATUS_STR
}
