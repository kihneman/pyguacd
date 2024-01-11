from ctypes import cast, c_char_p, c_int, POINTER

from . import libguac_wrapper
from .constants import GuacClientLogLevel, GuacStatus, GUACD_USEC_TIMEOUT
from .libguac_wrapper import String, guac_parser, guac_parser_alloc, guac_parser_expect, guac_parser_free, guac_socket
from .log import guacd_log, guacd_log_guac_error, guacd_log_handshake_failure


def parse_identifier(parser_ptr: POINTER(guac_parser), guac_sock: POINTER(guac_socket)):
    parser = parser_ptr.contents

    # Reset guac_error
    libguac_wrapper.__guac_error()[0] = c_int(GuacStatus.GUAC_STATUS_SUCCESS)
    libguac_wrapper.__guac_error_message()[0] = String(b'').raw

    # Get protocol from select instruction
    if parser_result := guac_parser_expect(parser_ptr, guac_sock, c_int(GUACD_USEC_TIMEOUT), String(b'select')):
        # Log error
        guacd_log_handshake_failure()
        guacd_log_guac_error(GuacClientLogLevel.GUAC_LOG_ERROR, f'Error reading "select" ({parser_result})')

        # Extra debug
        if parser.argc == 0:
            guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f"Didn't get any parser args")
        elif parser.argc == 1:
            identifier = cast(parser.argv[0], c_char_p).value
            guacd_log(GuacClientLogLevel.GUAC_LOG_INFO, f'Received protocol "{identifier}"')
        else:
            argv = [cast(parser.argv[i], c_char_p).value for i in range(parser.argc)] if 1 < parser.argc < 5 else None
            argv_str = f': {argv}' if argv else ''
            guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Received {parser.argc} args but expected 1{argv_str}')

        return None

    # Validate args to select
    if parser.argc != 1:
        # Log error
        guacd_log_handshake_failure()
        guacd_log(GuacClientLogLevel.GUAC_LOG_ERROR, f'Bad number of arguments to "select" ({parser.argc})')
        return None

    identifier: bytes = cast(parser.argv[0], c_char_p).value
    return identifier, parser_ptr
