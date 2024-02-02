# Pyguacd

Pyguacd is a Python ctypes wrapper of libguac.

Here are some items to help get started with `pyguacd`:
- This has only been tested on Linux.
- Thus ctypes wrapper only works with an updated version of libguac that is included in the wheel.

### Requirements:
- A pip install of the manylinux wheel will also install one required dependency `pyzmq`.

### Getting Started:
- It is recommended to create and use a virtual environment,
  for example the following commands create and activate a virtual environment `pyguacd`.
  ```
  python -m venv pyguacd
  source pyguacd/bin/activate
  ```
