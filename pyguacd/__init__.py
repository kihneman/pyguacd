import asyncio

from .daemon import run_server


if __name__ == '__main__':
    asyncio.run(run_server())
