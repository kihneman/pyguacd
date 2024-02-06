from .utils import libs


def main():
    if libs.check_libs():
        from . import daemon
        daemon.main()


if __name__ == '__main__':
    main()
