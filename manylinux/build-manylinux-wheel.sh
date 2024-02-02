#!/bin/bash

PYTHON_BIN=/opt/python/cp311-cp311/bin
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )


# TODO: Download rpms

# Build wheel
cd ~
mkdir wheels
$PYTHON_BIN/pip wheel src/pyguacd -w wheels

# Update LD_LIBRARY_PATH
export LD_LIBRARY_PATH=`$PYTHON_BIN/python $SCRIPT_DIR/new-ld-library-path.py`

# Repair wheel to get manylinux wheel
auditwheel repair wheels/pyguacd-*.whl -w wheels
