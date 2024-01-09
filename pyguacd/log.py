from ctypes import cast, c_char_p
from os import getpid
from sys import stderr

from . import libguac_wrapper
from .constants import guac_status_to_string, GuacClientLogLevel, GuacStatus, GUACD_LOG_NAME


def guacd_log(level: GuacClientLogLevel, message):
    level_prefix = 'GUAC_LOG_'
    priority_name = level.name[len(level_prefix):] if level.name.startswith(level_prefix) else 'UNKNOWN'
    print(f'{GUACD_LOG_NAME}[{getpid()}]: {priority_name}:\t{message}', file=stderr)


def guacd_log_guac_error(level: GuacClientLogLevel, message: str):
    guac_error = libguac_wrapper.__guac_error()[0]
    guac_error_message = cast(libguac_wrapper.__guac_error_message()[0], c_char_p).value
    if guac_error != GuacStatus.GUAC_STATUS_SUCCESS:
        # If error message provided, include in log
        if guac_error_message:
            guacd_log(level, f'{message}: {guac_error_message.decode()}')

        # Otherwise just log with standard status string
        else:
            status_string = guac_status_to_string.get(guac_error, guac_status_to_string[None])
            guacd_log(level, f'{message}: {status_string}')

    # Just log message if no status code
    else:
        guacd_log(level, message)


def guacd_log_handshake_failure():
    guac_error = libguac_wrapper.__guac_error()[0]
    if guac_error == GuacStatus.GUAC_STATUS_CLOSED:
        guacd_log(
            GuacClientLogLevel.GUAC_LOG_DEBUG,
            "Guacamole connection closed during handshake"
        )
    elif guac_error == GuacStatus.GUAC_STATUS_PROTOCOL_ERROR:
        guacd_log(
            GuacClientLogLevel.GUAC_LOG_ERROR,
            "Guacamole protocol violation. Perhaps the version of "
            "guacamole-client is incompatible with this version of "
            "guacd?"
        )
    else:
        status_string = guac_status_to_string.get(guac_error, guac_status_to_string[None])
        guacd_log(
            GuacClientLogLevel.GUAC_LOG_WARNING,
            f"Guacamole handshake failed: {status_string}"
        )
