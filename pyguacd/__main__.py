from .utils import libs


def main():
    """Check libraries and launch server

    This check is run before importing daemon.py which may load some of the libraries in question.
    """

    if libs.check_library_dependencies_found():
        from . import daemon
        daemon.main()


if __name__ == '__main__':
    main()
