import os
from os.path import join
from site import getsitepackages


ld_library_paths = set(os.environ['LD_LIBRARY_PATH'].split(':'))
ld_library_paths.update(['/opt/keeper/lib64', '/opt/keeper/lib64/freerdp2'])
ld_library_paths.update([join(p, 'pyzmq.libs') for p in getsitepackages() if 'lib64' in p])
print(':'.join(ld_library_paths), end='')
