# Pyguacd

Pyguacd is a Python ctypes wrapper of libguac.

Here are some items to help get started with `pyguacd`:
- This has only been tested on Linux.
- The ctypes wrapper works with the standard libguac.
- The libguac libraries are assumed to be in `/opt/guacamole`.
- Currently `pyguacd` only accepts one connection from one user at a time.

### Requirements:
- `libguac` must be installed in `/opt/guacamole`.
- Of course `python` must also be installed.
- In addition `git` needs to be installed if pip installing from Github.
- No 3rd party Python packages are needed at this time.

### Getting Started:
- It is recommended to create and use a virtual environment,
  for example the following commands create and activate a virtual environment `pyguacd`.
  ```
  python -m venv pyguacd
  source pyguacd/bin/activate
  ```
- Next, the following command will install `pyguad` from this repo into the current environment.
  ```
  pip install git+https://github.com/Keeper-Security/pyguacd.git
  ```
- Finally run `pyguacd` in place of where `guacd` would normally be run.
  ( Only the options `-b`, `-l`, and `-L` work for `pyguacd` at the moment. )
  ```
  pyguacd -b 0.0.0.0 -l 4822
  ```
