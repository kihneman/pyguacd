from argparse import ArgumentError, ArgumentParser
from dataclasses import dataclass
from typing import Optional

from .constants import GuacClientLogLevel, GUACD_DEFAULT_BIND_HOST, GUACD_DEFAULT_BIND_PORT


GUACD_ARG_TO_LOG_LEVEL = {
    'error': GuacClientLogLevel.GUAC_LOG_ERROR,
    'warning': GuacClientLogLevel.GUAC_LOG_WARNING,
    'info': GuacClientLogLevel.GUAC_LOG_INFO,
    'debug': GuacClientLogLevel.GUAC_LOG_DEBUG,
    'trace': GuacClientLogLevel.GUAC_LOG_TRACE
}


@dataclass
class GuacdConfig:
    bind_host: str = GUACD_DEFAULT_BIND_HOST
    bind_port: str = GUACD_DEFAULT_BIND_PORT

    # The file to write the PID in, if any.
    pidfile: Optional[str] = None

    # Whether guacd should run in the foreground.
    foreground: bool = False

    # Whether guacd should simply print its version information and exit.
    print_version: bool = False

    # SSL certificate file.
    cert_file: Optional[str] = None

    # SSL private key file.
    key_file: Optional[str] = None

    # The maximum log level to be logged by guacd.
    max_log_level: GuacClientLogLevel = GuacClientLogLevel.GUAC_LOG_INFO


def guacd_conf_parse_args():
    parser = ArgumentParser(exit_on_error=False)
    parser.add_argument('-l', dest='bind_port')
    parser.add_argument('-b', dest='bind_host')
    parser.add_argument('-f', dest='foreground', action='store_true')
    parser.add_argument('-v', dest='print_version', action='store_true')
    parser.add_argument('-p', dest='pidfile')
    parser.add_argument('-L', dest='max_log_level', choices=GUACD_ARG_TO_LOG_LEVEL)
    parser.add_argument('-C', dest='cert_file')
    parser.add_argument('-K', dest='key_file')

    try:
        ns = parser.parse_args()

    except ArgumentError as e:
        print(f'Error: {e}')
        return None

    else:
        kwargs = vars(ns)
        if kwargs.get('max_log_level'):
            kwargs['max_log_level'] = GUACD_ARG_TO_LOG_LEVEL[kwargs['max_log_level']]

        config_kwargs = {k: v for k, v in kwargs.items() if v not in (None, False)}
        return GuacdConfig(**config_kwargs)
