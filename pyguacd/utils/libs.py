import sys
from glob import glob
from os.path import join
from subprocess import check_output, run

from ..constants import GUACD_LIB_DIR


def check_library_dependencies_found():
    """Check dependencies of libraries in GUACD_LIB_DIR

    Check the dependencies using "ldd" and make sure none of the dependencies report " => not found".
    Print a message to indicate which dependencies are missing if any are not found.

    :return: True if all the dependencies are found, otherwise return False
    """
    ret_val = True

    do_check_libs = (
        sys.platform.startswith('linux') and
        run(['which', 'ldd'], capture_output=True).returncode == 0
    )
    if do_check_libs:
        not_found_libs = set()
        for lib_file in glob(join(GUACD_LIB_DIR, '*.so')):
            ldd_lines = check_output(['ldd', lib_file], encoding='utf8').splitlines()
            not_found_libs.update([l.split()[0] for l in ldd_lines if l.endswith('=> not found')])

        if len(not_found_libs) > 0:
            print('ERROR: the following system libraries are missing.')
            print('\n'.join(not_found_libs))
            ret_val = False

    return ret_val
