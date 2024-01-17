from uuid import uuid4


def new_ipc_addr(base_path):
    uid = uuid4().hex
    return f'ipc://{base_path}{uid}'
