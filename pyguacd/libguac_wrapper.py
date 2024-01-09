r"""Wrapper for user-handlers.h

Generated with:
/tmp/guacamole-server/venv-ctypesgen/bin/ctypesgen -llibguac -L /opt/guacamole/lib -I /opt/guacamole/include -I . -o libguac_wrapper.py src/libguac/user-handlers.h src/libguac/guacamole/client.h src/libguac/client-internal.h src/libguac/guacamole/error.h src/libguac/guacamole/error-types.h src/libguac/guacamole/parser.h src/libguac/guacamole/protocol.h src/libguac/guacamole/socket.h src/libguac/guacamole/socket-zmq.h src/libguac/guacamole/user.h

Do not modify this file.
"""

__docformat__ = "restructuredtext"

# Begin preamble for Python

import ctypes
import sys
from ctypes import *  # noqa: F401, F403

_int_types = (ctypes.c_int16, ctypes.c_int32)
if hasattr(ctypes, "c_int64"):
    # Some builds of ctypes apparently do not have ctypes.c_int64
    # defined; it's a pretty good bet that these builds do not
    # have 64-bit pointers.
    _int_types += (ctypes.c_int64,)
for t in _int_types:
    if ctypes.sizeof(t) == ctypes.sizeof(ctypes.c_size_t):
        c_ptrdiff_t = t
del t
del _int_types



class UserString:
    def __init__(self, seq):
        if isinstance(seq, bytes):
            self.data = seq
        elif isinstance(seq, UserString):
            self.data = seq.data[:]
        else:
            self.data = str(seq).encode()

    def __bytes__(self):
        return self.data

    def __str__(self):
        return self.data.decode()

    def __repr__(self):
        return repr(self.data)

    def __int__(self):
        return int(self.data.decode())

    def __long__(self):
        return int(self.data.decode())

    def __float__(self):
        return float(self.data.decode())

    def __complex__(self):
        return complex(self.data.decode())

    def __hash__(self):
        return hash(self.data)

    def __le__(self, string):
        if isinstance(string, UserString):
            return self.data <= string.data
        else:
            return self.data <= string

    def __lt__(self, string):
        if isinstance(string, UserString):
            return self.data < string.data
        else:
            return self.data < string

    def __ge__(self, string):
        if isinstance(string, UserString):
            return self.data >= string.data
        else:
            return self.data >= string

    def __gt__(self, string):
        if isinstance(string, UserString):
            return self.data > string.data
        else:
            return self.data > string

    def __eq__(self, string):
        if isinstance(string, UserString):
            return self.data == string.data
        else:
            return self.data == string

    def __ne__(self, string):
        if isinstance(string, UserString):
            return self.data != string.data
        else:
            return self.data != string

    def __contains__(self, char):
        return char in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.__class__(self.data[index])

    def __getslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        return self.__class__(self.data[start:end])

    def __add__(self, other):
        if isinstance(other, UserString):
            return self.__class__(self.data + other.data)
        elif isinstance(other, bytes):
            return self.__class__(self.data + other)
        else:
            return self.__class__(self.data + str(other).encode())

    def __radd__(self, other):
        if isinstance(other, bytes):
            return self.__class__(other + self.data)
        else:
            return self.__class__(str(other).encode() + self.data)

    def __mul__(self, n):
        return self.__class__(self.data * n)

    __rmul__ = __mul__

    def __mod__(self, args):
        return self.__class__(self.data % args)

    # the following methods are defined in alphabetical order:
    def capitalize(self):
        return self.__class__(self.data.capitalize())

    def center(self, width, *args):
        return self.__class__(self.data.center(width, *args))

    def count(self, sub, start=0, end=sys.maxsize):
        return self.data.count(sub, start, end)

    def decode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.decode(encoding, errors))
            else:
                return self.__class__(self.data.decode(encoding))
        else:
            return self.__class__(self.data.decode())

    def encode(self, encoding=None, errors=None):  # XXX improve this?
        if encoding:
            if errors:
                return self.__class__(self.data.encode(encoding, errors))
            else:
                return self.__class__(self.data.encode(encoding))
        else:
            return self.__class__(self.data.encode())

    def endswith(self, suffix, start=0, end=sys.maxsize):
        return self.data.endswith(suffix, start, end)

    def expandtabs(self, tabsize=8):
        return self.__class__(self.data.expandtabs(tabsize))

    def find(self, sub, start=0, end=sys.maxsize):
        return self.data.find(sub, start, end)

    def index(self, sub, start=0, end=sys.maxsize):
        return self.data.index(sub, start, end)

    def isalpha(self):
        return self.data.isalpha()

    def isalnum(self):
        return self.data.isalnum()

    def isdecimal(self):
        return self.data.isdecimal()

    def isdigit(self):
        return self.data.isdigit()

    def islower(self):
        return self.data.islower()

    def isnumeric(self):
        return self.data.isnumeric()

    def isspace(self):
        return self.data.isspace()

    def istitle(self):
        return self.data.istitle()

    def isupper(self):
        return self.data.isupper()

    def join(self, seq):
        return self.data.join(seq)

    def ljust(self, width, *args):
        return self.__class__(self.data.ljust(width, *args))

    def lower(self):
        return self.__class__(self.data.lower())

    def lstrip(self, chars=None):
        return self.__class__(self.data.lstrip(chars))

    def partition(self, sep):
        return self.data.partition(sep)

    def replace(self, old, new, maxsplit=-1):
        return self.__class__(self.data.replace(old, new, maxsplit))

    def rfind(self, sub, start=0, end=sys.maxsize):
        return self.data.rfind(sub, start, end)

    def rindex(self, sub, start=0, end=sys.maxsize):
        return self.data.rindex(sub, start, end)

    def rjust(self, width, *args):
        return self.__class__(self.data.rjust(width, *args))

    def rpartition(self, sep):
        return self.data.rpartition(sep)

    def rstrip(self, chars=None):
        return self.__class__(self.data.rstrip(chars))

    def split(self, sep=None, maxsplit=-1):
        return self.data.split(sep, maxsplit)

    def rsplit(self, sep=None, maxsplit=-1):
        return self.data.rsplit(sep, maxsplit)

    def splitlines(self, keepends=0):
        return self.data.splitlines(keepends)

    def startswith(self, prefix, start=0, end=sys.maxsize):
        return self.data.startswith(prefix, start, end)

    def strip(self, chars=None):
        return self.__class__(self.data.strip(chars))

    def swapcase(self):
        return self.__class__(self.data.swapcase())

    def title(self):
        return self.__class__(self.data.title())

    def translate(self, *args):
        return self.__class__(self.data.translate(*args))

    def upper(self):
        return self.__class__(self.data.upper())

    def zfill(self, width):
        return self.__class__(self.data.zfill(width))


class MutableString(UserString):
    """mutable string objects

    Python strings are immutable objects.  This has the advantage, that
    strings may be used as dictionary keys.  If this property isn't needed
    and you insist on changing string values in place instead, you may cheat
    and use MutableString.

    But the purpose of this class is an educational one: to prevent
    people from inventing their own mutable string class derived
    from UserString and than forget thereby to remove (override) the
    __hash__ method inherited from UserString.  This would lead to
    errors that would be very hard to track down.

    A faster and better solution is to rewrite your program using lists."""

    def __init__(self, string=""):
        self.data = string

    def __hash__(self):
        raise TypeError("unhashable type (it is mutable)")

    def __setitem__(self, index, sub):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + sub + self.data[index + 1 :]

    def __delitem__(self, index):
        if index < 0:
            index += len(self.data)
        if index < 0 or index >= len(self.data):
            raise IndexError
        self.data = self.data[:index] + self.data[index + 1 :]

    def __setslice__(self, start, end, sub):
        start = max(start, 0)
        end = max(end, 0)
        if isinstance(sub, UserString):
            self.data = self.data[:start] + sub.data + self.data[end:]
        elif isinstance(sub, bytes):
            self.data = self.data[:start] + sub + self.data[end:]
        else:
            self.data = self.data[:start] + str(sub).encode() + self.data[end:]

    def __delslice__(self, start, end):
        start = max(start, 0)
        end = max(end, 0)
        self.data = self.data[:start] + self.data[end:]

    def immutable(self):
        return UserString(self.data)

    def __iadd__(self, other):
        if isinstance(other, UserString):
            self.data += other.data
        elif isinstance(other, bytes):
            self.data += other
        else:
            self.data += str(other).encode()
        return self

    def __imul__(self, n):
        self.data *= n
        return self


class String(MutableString, ctypes.Union):

    _fields_ = [("raw", ctypes.POINTER(ctypes.c_char)), ("data", ctypes.c_char_p)]

    def __init__(self, obj=b""):
        if isinstance(obj, (bytes, UserString)):
            self.data = bytes(obj)
        else:
            self.raw = obj

    def __len__(self):
        return self.data and len(self.data) or 0

    def from_param(cls, obj):
        # Convert None or 0
        if obj is None or obj == 0:
            return cls(ctypes.POINTER(ctypes.c_char)())

        # Convert from String
        elif isinstance(obj, String):
            return obj

        # Convert from bytes
        elif isinstance(obj, bytes):
            return cls(obj)

        # Convert from str
        elif isinstance(obj, str):
            return cls(obj.encode())

        # Convert from c_char_p
        elif isinstance(obj, ctypes.c_char_p):
            return obj

        # Convert from POINTER(ctypes.c_char)
        elif isinstance(obj, ctypes.POINTER(ctypes.c_char)):
            return obj

        # Convert from raw pointer
        elif isinstance(obj, int):
            return cls(ctypes.cast(obj, ctypes.POINTER(ctypes.c_char)))

        # Convert from ctypes.c_char array
        elif isinstance(obj, ctypes.c_char * len(obj)):
            return obj

        # Convert from object
        else:
            return String.from_param(obj._as_parameter_)

    from_param = classmethod(from_param)


def ReturnString(obj, func=None, arguments=None):
    return String.from_param(obj)


# As of ctypes 1.0, ctypes does not support custom error-checking
# functions on callbacks, nor does it support custom datatypes on
# callbacks, so we must ensure that all callbacks return
# primitive datatypes.
#
# Non-primitive return values wrapped with UNCHECKED won't be
# typechecked, and will be converted to ctypes.c_void_p.
def UNCHECKED(type):
    if hasattr(type, "_type_") and isinstance(type._type_, str) and type._type_ != "P":
        return type
    else:
        return ctypes.c_void_p


# ctypes doesn't have direct support for variadic functions, so we have to write
# our own wrapper class
class _variadic_function(object):
    def __init__(self, func, restype, argtypes, errcheck):
        self.func = func
        self.func.restype = restype
        self.argtypes = argtypes
        if errcheck:
            self.func.errcheck = errcheck

    def _as_parameter_(self):
        # So we can pass this variadic function as a function pointer
        return self.func

    def __call__(self, *args):
        fixed_args = []
        i = 0
        for argtype in self.argtypes:
            # Typecheck what we can
            fixed_args.append(argtype.from_param(args[i]))
            i += 1
        return self.func(*fixed_args + list(args[i:]))


def ord_if_char(value):
    """
    Simple helper used for casts to simple builtin types:  if the argument is a
    string type, it will be converted to it's ordinal value.

    This function will raise an exception if the argument is string with more
    than one characters.
    """
    return ord(value) if (isinstance(value, bytes) or isinstance(value, str)) else value

# End preamble

_libs = {}
if sys.platform.startswith('linux'):
    _libdirs = ['/opt/guacamole/lib']
elif sys.platform.startswith('win'):
    # _libdirs = [
    #     '\\Users\\KevinKihneman\\Downloads\\windows-guac-build\\mingw64\\bin',
    #     '\\Users\\KevinKihneman\\Downloads\\windows-guac-build\\mingw64\\lib\\freerdp2',
    # ]
    _libdirs = ['\\msys64\\usr\\bin', '\\msys64\\mingw64\\bin', '\\msys64\\mingw64\\lib']

# Begin loader

"""
Load libraries - appropriately for all our supported platforms
"""
# ----------------------------------------------------------------------------
# Copyright (c) 2008 David James
# Copyright (c) 2006-2008 Alex Holkner
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#  * Neither the name of pyglet nor the names of its
#    contributors may be used to endorse or promote products
#    derived from this software without specific prior written
#    permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------------

import ctypes
import ctypes.util
import glob
import os.path
import platform
import re
import sys


def _environ_path(name):
    """Split an environment variable into a path-like list elements"""
    if name in os.environ:
        return os.environ[name].split(":")
    return []


class LibraryLoader:
    """
    A base class For loading of libraries ;-)
    Subclasses load libraries for specific platforms.
    """

    # library names formatted specifically for platforms
    name_formats = ["%s"]

    class Lookup:
        """Looking up calling conventions for a platform"""

        mode = ctypes.DEFAULT_MODE

        def __init__(self, path):
            super(LibraryLoader.Lookup, self).__init__()
            self.access = dict(cdecl=ctypes.CDLL(path, self.mode))

        def get(self, name, calling_convention="cdecl"):
            """Return the given name according to the selected calling convention"""
            if calling_convention not in self.access:
                raise LookupError(
                    "Unknown calling convention '{}' for function '{}'".format(
                        calling_convention, name
                    )
                )
            return getattr(self.access[calling_convention], name)

        def has(self, name, calling_convention="cdecl"):
            """Return True if this given calling convention finds the given 'name'"""
            if calling_convention not in self.access:
                return False
            return hasattr(self.access[calling_convention], name)

        def __getattr__(self, name):
            return getattr(self.access["cdecl"], name)

    def __init__(self):
        self.other_dirs = []

    def __call__(self, libname):
        """Given the name of a library, load it."""
        paths = self.getpaths(libname)

        for path in paths:
            # noinspection PyBroadException
            try:
                return self.Lookup(path)
            except Exception:  # pylint: disable=broad-except
                pass

        raise ImportError("Could not load %s." % libname)

    def getpaths(self, libname):
        """Return a list of paths where the library might be found."""
        if os.path.isabs(libname):
            yield libname
        else:
            # search through a prioritized series of locations for the library

            # we first search any specific directories identified by user
            for dir_i in self.other_dirs:
                for fmt in self.name_formats:
                    # dir_i should be absolute already
                    yield os.path.join(dir_i, fmt % libname)

            # check if this code is even stored in a physical file
            try:
                this_file = __file__
            except NameError:
                this_file = None

            # then we search the directory where the generated python interface is stored
            if this_file is not None:
                for fmt in self.name_formats:
                    yield os.path.abspath(os.path.join(os.path.dirname(__file__), fmt % libname))

            # now, use the ctypes tools to try to find the library
            for fmt in self.name_formats:
                path = ctypes.util.find_library(fmt % libname)
                if path:
                    yield path

            # then we search all paths identified as platform-specific lib paths
            for path in self.getplatformpaths(libname):
                yield path

            # Finally, we'll try the users current working directory
            for fmt in self.name_formats:
                yield os.path.abspath(os.path.join(os.path.curdir, fmt % libname))

    def getplatformpaths(self, _libname):  # pylint: disable=no-self-use
        """Return all the library paths available in this platform"""
        return []


# Darwin (Mac OS X)


class DarwinLibraryLoader(LibraryLoader):
    """Library loader for MacOS"""

    name_formats = [
        "lib%s.dylib",
        "lib%s.so",
        "lib%s.bundle",
        "%s.dylib",
        "%s.so",
        "%s.bundle",
        "%s",
    ]

    class Lookup(LibraryLoader.Lookup):
        """
        Looking up library files for this platform (Darwin aka MacOS)
        """

        # Darwin requires dlopen to be called with mode RTLD_GLOBAL instead
        # of the default RTLD_LOCAL.  Without this, you end up with
        # libraries not being loadable, resulting in "Symbol not found"
        # errors
        mode = ctypes.RTLD_GLOBAL

    def getplatformpaths(self, libname):
        if os.path.pathsep in libname:
            names = [libname]
        else:
            names = [fmt % libname for fmt in self.name_formats]

        for directory in self.getdirs(libname):
            for name in names:
                yield os.path.join(directory, name)

    @staticmethod
    def getdirs(libname):
        """Implements the dylib search as specified in Apple documentation:

        http://developer.apple.com/documentation/DeveloperTools/Conceptual/
            DynamicLibraries/Articles/DynamicLibraryUsageGuidelines.html

        Before commencing the standard search, the method first checks
        the bundle's ``Frameworks`` directory if the application is running
        within a bundle (OS X .app).
        """

        dyld_fallback_library_path = _environ_path("DYLD_FALLBACK_LIBRARY_PATH")
        if not dyld_fallback_library_path:
            dyld_fallback_library_path = [
                os.path.expanduser("~/lib"),
                "/usr/local/lib",
                "/usr/lib",
            ]

        dirs = []

        if "/" in libname:
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
        else:
            dirs.extend(_environ_path("LD_LIBRARY_PATH"))
            dirs.extend(_environ_path("DYLD_LIBRARY_PATH"))
            dirs.extend(_environ_path("LD_RUN_PATH"))

        if hasattr(sys, "frozen") and getattr(sys, "frozen") == "macosx_app":
            dirs.append(os.path.join(os.environ["RESOURCEPATH"], "..", "Frameworks"))

        dirs.extend(dyld_fallback_library_path)

        return dirs


# Posix


class PosixLibraryLoader(LibraryLoader):
    """Library loader for POSIX-like systems (including Linux)"""

    _ld_so_cache = None

    _include = re.compile(r"^\s*include\s+(?P<pattern>.*)")

    name_formats = ["lib%s.so", "%s.so", "%s"]

    class _Directories(dict):
        """Deal with directories"""

        def __init__(self):
            dict.__init__(self)
            self.order = 0

        def add(self, directory):
            """Add a directory to our current set of directories"""
            if len(directory) > 1:
                directory = directory.rstrip(os.path.sep)
            # only adds and updates order if exists and not already in set
            if not os.path.exists(directory):
                return
            order = self.setdefault(directory, self.order)
            if order == self.order:
                self.order += 1

        def extend(self, directories):
            """Add a list of directories to our set"""
            for a_dir in directories:
                self.add(a_dir)

        def ordered(self):
            """Sort the list of directories"""
            return (i[0] for i in sorted(self.items(), key=lambda d: d[1]))

    def _get_ld_so_conf_dirs(self, conf, dirs):
        """
        Recursive function to help parse all ld.so.conf files, including proper
        handling of the `include` directive.
        """

        try:
            with open(conf) as fileobj:
                for dirname in fileobj:
                    dirname = dirname.strip()
                    if not dirname:
                        continue

                    match = self._include.match(dirname)
                    if not match:
                        dirs.add(dirname)
                    else:
                        for dir2 in glob.glob(match.group("pattern")):
                            self._get_ld_so_conf_dirs(dir2, dirs)
        except IOError:
            pass

    def _create_ld_so_cache(self):
        # Recreate search path followed by ld.so.  This is going to be
        # slow to build, and incorrect (ld.so uses ld.so.cache, which may
        # not be up-to-date).  Used only as fallback for distros without
        # /sbin/ldconfig.
        #
        # We assume the DT_RPATH and DT_RUNPATH binary sections are omitted.

        directories = self._Directories()
        for name in (
            "LD_LIBRARY_PATH",
            "SHLIB_PATH",  # HP-UX
            "LIBPATH",  # OS/2, AIX
            "LIBRARY_PATH",  # BE/OS
        ):
            if name in os.environ:
                directories.extend(os.environ[name].split(os.pathsep))

        self._get_ld_so_conf_dirs("/etc/ld.so.conf", directories)

        bitage = platform.architecture()[0]

        unix_lib_dirs_list = []
        if bitage.startswith("64"):
            # prefer 64 bit if that is our arch
            unix_lib_dirs_list += ["/lib64", "/usr/lib64"]

        # must include standard libs, since those paths are also used by 64 bit
        # installs
        unix_lib_dirs_list += ["/lib", "/usr/lib"]
        if sys.platform.startswith("linux"):
            # Try and support multiarch work in Ubuntu
            # https://wiki.ubuntu.com/MultiarchSpec
            if bitage.startswith("32"):
                # Assume Intel/AMD x86 compat
                unix_lib_dirs_list += ["/lib/i386-linux-gnu", "/usr/lib/i386-linux-gnu"]
            elif bitage.startswith("64"):
                # Assume Intel/AMD x86 compatible
                unix_lib_dirs_list += [
                    "/lib/x86_64-linux-gnu",
                    "/usr/lib/x86_64-linux-gnu",
                ]
            else:
                # guess...
                unix_lib_dirs_list += glob.glob("/lib/*linux-gnu")
        directories.extend(unix_lib_dirs_list)

        cache = {}
        lib_re = re.compile(r"lib(.*)\.s[ol]")
        # ext_re = re.compile(r"\.s[ol]$")
        for our_dir in directories.ordered():
            try:
                for path in glob.glob("%s/*.s[ol]*" % our_dir):
                    file = os.path.basename(path)

                    # Index by filename
                    cache_i = cache.setdefault(file, set())
                    cache_i.add(path)

                    # Index by library name
                    match = lib_re.match(file)
                    if match:
                        library = match.group(1)
                        cache_i = cache.setdefault(library, set())
                        cache_i.add(path)
            except OSError:
                pass

        self._ld_so_cache = cache

    def getplatformpaths(self, libname):
        if self._ld_so_cache is None:
            self._create_ld_so_cache()

        result = self._ld_so_cache.get(libname, set())
        for i in result:
            # we iterate through all found paths for library, since we may have
            # actually found multiple architectures or other library types that
            # may not load
            yield i


# Windows


class WindowsLibraryLoader(LibraryLoader):
    """Library loader for Microsoft Windows"""

    name_formats = ["%s.dll", "lib%s.dll", "%slib.dll", "%s"]

    class Lookup(LibraryLoader.Lookup):
        """Lookup class for Windows libraries..."""

        def __init__(self, path):
            super(WindowsLibraryLoader.Lookup, self).__init__(path)
            self.access["stdcall"] = ctypes.windll.LoadLibrary(path)


# Platform switching

# If your value of sys.platform does not appear in this dict, please contact
# the Ctypesgen maintainers.

loaderclass = {
    "darwin": DarwinLibraryLoader,
    "cygwin": WindowsLibraryLoader,
    "win32": WindowsLibraryLoader,
    "msys": WindowsLibraryLoader,
}

load_library = loaderclass.get(sys.platform, PosixLibraryLoader)()


def add_library_search_dirs(other_dirs):
    """
    Add libraries to search paths.
    If library paths are relative, convert them to absolute with respect to this
    file's directory
    """
    for path in other_dirs:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        load_library.other_dirs.append(path)


del loaderclass

# End loader

if sys.platform.startswith('linux'):
    add_library_search_dirs(['/opt/guacamole/lib'])
    # Begin libraries
    _libs["libguac"] = load_library("libguac")
elif sys.platform.startswith('win'):
    # add_library_search_dirs([
    #     '\\Users\\KevinKihneman\\Downloads\\windows-guac-build\\mingw64\\bin',
    #     '\\Users\\KevinKihneman\\Downloads\\windows-guac-build\\mingw64\\lib\\freerdp2',
    # ])
    add_library_search_dirs(['\\msys64\\usr\\bin', '\\msys64\\mingw64\\bin', '\\msys64\\mingw64\\lib'])
    # Begin libraries
    _libs["libguac"] = load_library("libguac")

# 1 libraries
# End libraries

# No modules

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 59
class struct_guac_client(Structure):
    pass

guac_client = struct_guac_client# /tmp/guacamole-server/src/libguac/guacamole/client-types.h: 35

enum_guac_client_state = c_int# /tmp/guacamole-server/src/libguac/guacamole/client-types.h: 55

guac_client_state = enum_guac_client_state# /tmp/guacamole-server/src/libguac/guacamole/client-types.h: 55

enum_guac_client_log_level = c_int# /tmp/guacamole-server/src/libguac/guacamole/client-types.h: 94

guac_client_log_level = enum_guac_client_log_level# /tmp/guacamole-server/src/libguac/guacamole/client-types.h: 94

# /tmp/guacamole-server/src/libguac/guacamole/object-types.h: 32
class struct_guac_object(Structure):
    pass

guac_object = struct_guac_object# /tmp/guacamole-server/src/libguac/guacamole/object-types.h: 32

enum_guac_protocol_status = c_int# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 164

guac_protocol_status = enum_guac_protocol_status# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 164

enum_guac_composite_mode = c_int# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 213

guac_composite_mode = enum_guac_composite_mode# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 213

enum_guac_transfer_function = c_int# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 259

guac_transfer_function = enum_guac_transfer_function# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 259

enum_guac_line_cap_style = c_int# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 268

guac_line_cap_style = enum_guac_line_cap_style# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 268

enum_guac_line_join_style = c_int# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 277

guac_line_join_style = enum_guac_line_join_style# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 277

enum_guac_protocol_version = c_int# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 318

guac_protocol_version = enum_guac_protocol_version# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 318

enum_guac_message_type = c_int# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 342

guac_message_type = enum_guac_message_type# /tmp/guacamole-server/src/libguac/guacamole/protocol-types.h: 342

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 39
class struct_guac_socket(Structure):
    pass

guac_socket = struct_guac_socket# /tmp/guacamole-server/src/libguac/guacamole/socket-types.h: 33

enum_guac_socket_state = c_int# /tmp/guacamole-server/src/libguac/guacamole/socket-types.h: 50

guac_socket_state = enum_guac_socket_state# /tmp/guacamole-server/src/libguac/guacamole/socket-types.h: 50

guac_socket_read_handler = CFUNCTYPE(UNCHECKED(c_ptrdiff_t), POINTER(guac_socket), POINTER(None), c_size_t)# /tmp/guacamole-server/src/libguac/guacamole/socket-fntypes.h: 43

guac_socket_write_handler = CFUNCTYPE(UNCHECKED(c_ptrdiff_t), POINTER(guac_socket), POINTER(None), c_size_t)# /tmp/guacamole-server/src/libguac/guacamole/socket-fntypes.h: 56

guac_socket_select_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_socket), c_int)# /tmp/guacamole-server/src/libguac/guacamole/socket-fntypes.h: 70

guac_socket_flush_handler = CFUNCTYPE(UNCHECKED(c_ptrdiff_t), POINTER(guac_socket))# /tmp/guacamole-server/src/libguac/guacamole/socket-fntypes.h: 83

guac_socket_lock_handler = CFUNCTYPE(UNCHECKED(None), POINTER(guac_socket))# /tmp/guacamole-server/src/libguac/guacamole/socket-fntypes.h: 93

guac_socket_unlock_handler = CFUNCTYPE(UNCHECKED(None), POINTER(guac_socket))# /tmp/guacamole-server/src/libguac/guacamole/socket-fntypes.h: 103

guac_socket_free_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_socket))# /tmp/guacamole-server/src/libguac/guacamole/socket-fntypes.h: 113

guac_timestamp = c_int64# /tmp/guacamole-server/src/libguac/guacamole/timestamp-types.h: 34

# /usr/include/bits/alltypes.h: 273
class struct___pthread(Structure):
    pass

pthread_t = POINTER(struct___pthread)# /usr/include/bits/alltypes.h: 273

pthread_key_t = c_uint# /usr/include/bits/alltypes.h: 284

# /usr/include/bits/alltypes.h: 383
class union_anon_7(Union):
    pass

union_anon_7.__slots__ = [
    '__i',
    '__vi',
    '__p',
]
union_anon_7._fields_ = [
    ('__i', c_int * int((sizeof(c_long) == 8) and 10 or 6)),
    ('__vi', c_int * int((sizeof(c_long) == 8) and 10 or 6)),
    ('__p', POINTER(None) * int((sizeof(c_long) == 8) and 5 or 6)),
]

# /usr/include/bits/alltypes.h: 383
class struct_anon_8(Structure):
    pass

struct_anon_8.__slots__ = [
    '__u',
]
struct_anon_8._fields_ = [
    ('__u', union_anon_7),
]

pthread_mutex_t = struct_anon_8# /usr/include/bits/alltypes.h: 383

# /usr/include/bits/alltypes.h: 403
class union_anon_11(Union):
    pass

union_anon_11.__slots__ = [
    '__i',
    '__vi',
    '__p',
]
union_anon_11._fields_ = [
    ('__i', c_int * int((sizeof(c_long) == 8) and 14 or 8)),
    ('__vi', c_int * int((sizeof(c_long) == 8) and 14 or 8)),
    ('__p', POINTER(None) * int((sizeof(c_long) == 8) and 7 or 8)),
]

# /usr/include/bits/alltypes.h: 403
class struct_anon_12(Structure):
    pass

struct_anon_12.__slots__ = [
    '__u',
]
struct_anon_12._fields_ = [
    ('__u', union_anon_11),
]

pthread_rwlock_t = struct_anon_12# /usr/include/bits/alltypes.h: 403

timer_t = POINTER(None)# /usr/include/bits/alltypes.h: 209

struct_guac_socket.__slots__ = [
    'data',
    'read_handler',
    'write_handler',
    'flush_handler',
    'lock_handler',
    'unlock_handler',
    'select_handler',
    'free_handler',
    'state',
    'last_write_timestamp',
    '__ready',
    '__ready_buf',
    '__encoded_buf',
    '__keep_alive_enabled',
    '__keep_alive_thread',
]
struct_guac_socket._fields_ = [
    ('data', POINTER(None)),
    ('read_handler', POINTER(guac_socket_read_handler)),
    ('write_handler', POINTER(guac_socket_write_handler)),
    ('flush_handler', POINTER(guac_socket_flush_handler)),
    ('lock_handler', POINTER(guac_socket_lock_handler)),
    ('unlock_handler', POINTER(guac_socket_unlock_handler)),
    ('select_handler', POINTER(guac_socket_select_handler)),
    ('free_handler', POINTER(guac_socket_free_handler)),
    ('state', guac_socket_state),
    ('last_write_timestamp', guac_timestamp),
    ('__ready', c_int),
    ('__ready_buf', c_ubyte * int(768)),
    ('__encoded_buf', c_char * int(1024)),
    ('__keep_alive_enabled', c_int),
    ('__keep_alive_thread', pthread_t),
]

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 130
if _libs["libguac"].has("guac_socket_alloc", "cdecl"):
    guac_socket_alloc = _libs["libguac"].get("guac_socket_alloc", "cdecl")
    guac_socket_alloc.argtypes = []
    guac_socket_alloc.restype = POINTER(guac_socket)

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 137
if _libs["libguac"].has("guac_socket_free", "cdecl"):
    guac_socket_free = _libs["libguac"].get("guac_socket_free", "cdecl")
    guac_socket_free.argtypes = [POINTER(guac_socket)]
    guac_socket_free.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 147
if _libs["libguac"].has("guac_socket_require_keep_alive", "cdecl"):
    guac_socket_require_keep_alive = _libs["libguac"].get("guac_socket_require_keep_alive", "cdecl")
    guac_socket_require_keep_alive.argtypes = [POINTER(guac_socket)]
    guac_socket_require_keep_alive.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 155
if _libs["libguac"].has("guac_socket_instruction_begin", "cdecl"):
    guac_socket_instruction_begin = _libs["libguac"].get("guac_socket_instruction_begin", "cdecl")
    guac_socket_instruction_begin.argtypes = [POINTER(guac_socket)]
    guac_socket_instruction_begin.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 163
if _libs["libguac"].has("guac_socket_instruction_end", "cdecl"):
    guac_socket_instruction_end = _libs["libguac"].get("guac_socket_instruction_end", "cdecl")
    guac_socket_instruction_end.argtypes = [POINTER(guac_socket)]
    guac_socket_instruction_end.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 178
if _libs["libguac"].has("guac_socket_open", "cdecl"):
    guac_socket_open = _libs["libguac"].get("guac_socket_open", "cdecl")
    guac_socket_open.argtypes = [c_int]
    guac_socket_open.restype = POINTER(guac_socket)

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 202
if _libs["libguac"].has("guac_socket_nest", "cdecl"):
    guac_socket_nest = _libs["libguac"].get("guac_socket_nest", "cdecl")
    guac_socket_nest.argtypes = [POINTER(guac_socket), c_int]
    guac_socket_nest.restype = POINTER(guac_socket)

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 234
if _libs["libguac"].has("guac_socket_tee", "cdecl"):
    guac_socket_tee = _libs["libguac"].get("guac_socket_tee", "cdecl")
    guac_socket_tee.argtypes = [POINTER(guac_socket), POINTER(guac_socket)]
    guac_socket_tee.restype = POINTER(guac_socket)

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 260
if _libs["libguac"].has("guac_socket_broadcast", "cdecl"):
    guac_socket_broadcast = _libs["libguac"].get("guac_socket_broadcast", "cdecl")
    guac_socket_broadcast.argtypes = [POINTER(guac_client)]
    guac_socket_broadcast.restype = POINTER(guac_socket)

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 286
if _libs["libguac"].has("guac_socket_broadcast_pending", "cdecl"):
    guac_socket_broadcast_pending = _libs["libguac"].get("guac_socket_broadcast_pending", "cdecl")
    guac_socket_broadcast_pending.argtypes = [POINTER(guac_client)]
    guac_socket_broadcast_pending.restype = POINTER(guac_socket)

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 300
if _libs["libguac"].has("guac_socket_write_int", "cdecl"):
    guac_socket_write_int = _libs["libguac"].get("guac_socket_write_int", "cdecl")
    guac_socket_write_int.argtypes = [POINTER(guac_socket), c_int64]
    guac_socket_write_int.restype = c_ptrdiff_t

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 314
if _libs["libguac"].has("guac_socket_write_string", "cdecl"):
    guac_socket_write_string = _libs["libguac"].get("guac_socket_write_string", "cdecl")
    guac_socket_write_string.argtypes = [POINTER(guac_socket), String]
    guac_socket_write_string.restype = c_ptrdiff_t

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 332
if _libs["libguac"].has("guac_socket_write_base64", "cdecl"):
    guac_socket_write_base64 = _libs["libguac"].get("guac_socket_write_base64", "cdecl")
    guac_socket_write_base64.argtypes = [POINTER(guac_socket), POINTER(None), c_size_t]
    guac_socket_write_base64.restype = c_ptrdiff_t

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 346
if _libs["libguac"].has("guac_socket_write", "cdecl"):
    guac_socket_write = _libs["libguac"].get("guac_socket_write", "cdecl")
    guac_socket_write.argtypes = [POINTER(guac_socket), POINTER(None), c_size_t]
    guac_socket_write.restype = c_ptrdiff_t

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 361
if _libs["libguac"].has("guac_socket_read", "cdecl"):
    guac_socket_read = _libs["libguac"].get("guac_socket_read", "cdecl")
    guac_socket_read.argtypes = [POINTER(guac_socket), POINTER(None), c_size_t]
    guac_socket_read.restype = c_ptrdiff_t

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 372
if _libs["libguac"].has("guac_socket_flush_base64", "cdecl"):
    guac_socket_flush_base64 = _libs["libguac"].get("guac_socket_flush_base64", "cdecl")
    guac_socket_flush_base64.argtypes = [POINTER(guac_socket)]
    guac_socket_flush_base64.restype = c_ptrdiff_t

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 383
if _libs["libguac"].has("guac_socket_flush", "cdecl"):
    guac_socket_flush = _libs["libguac"].get("guac_socket_flush", "cdecl")
    guac_socket_flush.argtypes = [POINTER(guac_socket)]
    guac_socket_flush.restype = c_ptrdiff_t

# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 401
if _libs["libguac"].has("guac_socket_select", "cdecl"):
    guac_socket_select = _libs["libguac"].get("guac_socket_select", "cdecl")
    guac_socket_select.argtypes = [POINTER(guac_socket), c_int]
    guac_socket_select.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/stream-types.h: 32
class struct_guac_stream(Structure):
    pass

guac_stream = struct_guac_stream# /tmp/guacamole-server/src/libguac/guacamole/stream-types.h: 32

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 115
class struct_guac_user(Structure):
    pass

guac_user = struct_guac_user# /tmp/guacamole-server/src/libguac/guacamole/user-types.h: 33

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 46
class struct_guac_user_info(Structure):
    pass

guac_user_info = struct_guac_user_info# /tmp/guacamole-server/src/libguac/guacamole/user-types.h: 39

guac_user_callback = CFUNCTYPE(UNCHECKED(POINTER(c_ubyte)), POINTER(guac_user), POINTER(None))# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 59

guac_user_mouse_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), c_int, c_int, c_int)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 95

guac_user_touch_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), c_int, c_int, c_int, c_int, c_int, c_double, c_double)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 140

guac_user_key_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), c_int, c_int)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 161

guac_user_audio_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), POINTER(guac_stream), String)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 183

guac_user_clipboard_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), POINTER(guac_stream), String)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 206

guac_user_size_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), c_int, c_int)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 227

guac_user_file_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), POINTER(guac_stream), String, String)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 253

guac_user_pipe_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), POINTER(guac_stream), String, String)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 282

guac_user_argv_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), POINTER(guac_stream), String, String)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 312

guac_user_blob_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), POINTER(guac_stream), POINTER(None), c_int)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 335

guac_user_ack_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), POINTER(guac_stream), String, guac_protocol_status)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 364

guac_user_end_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), POINTER(guac_stream))# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 381

guac_user_join_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), c_int, POINTER(POINTER(c_char)))# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 411

guac_user_leave_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user))# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 430

guac_user_sync_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), guac_timestamp)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 451

guac_user_get_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), POINTER(guac_object), String)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 472

guac_user_put_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), POINTER(guac_object), POINTER(guac_stream), String, String)# /tmp/guacamole-server/src/libguac/guacamole/user-fntypes.h: 499

guac_client_free_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_client))# /tmp/guacamole-server/src/libguac/guacamole/client-fntypes.h: 51

guac_client_join_pending_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_client))# /tmp/guacamole-server/src/libguac/guacamole/client-fntypes.h: 65

guac_client_log_handler = CFUNCTYPE(UNCHECKED(None), POINTER(guac_client), guac_client_log_level, String, c_void_p)# /tmp/guacamole-server/src/libguac/guacamole/client-fntypes.h: 83

# /tmp/guacamole-server/src/libguac/guacamole/layer-types.h: 32
class struct_guac_layer(Structure):
    pass

guac_layer = struct_guac_layer# /tmp/guacamole-server/src/libguac/guacamole/layer-types.h: 32

# /tmp/guacamole-server/src/libguac/guacamole/pool-types.h: 40
class struct_guac_pool(Structure):
    pass

guac_pool = struct_guac_pool# /tmp/guacamole-server/src/libguac/guacamole/pool-types.h: 40

# /tmp/guacamole-server/src/libguac/guacamole/rwlock.h: 62
class struct_guac_rwlock(Structure):
    pass

struct_guac_rwlock.__slots__ = [
    'lock',
    'key',
]
struct_guac_rwlock._fields_ = [
    ('lock', pthread_rwlock_t),
    ('key', pthread_key_t),
]

guac_rwlock = struct_guac_rwlock# /tmp/guacamole-server/src/libguac/guacamole/rwlock.h: 62

# /usr/include/cairo/cairo.h: 164
class struct__cairo_surface(Structure):
    pass

cairo_surface_t = struct__cairo_surface# /usr/include/cairo/cairo.h: 164

# /tmp/guacamole-server/src/libguac/client-internal.h: 44
class struct_guac_client_internal(Structure):
    pass

guac_client_internal = struct_guac_client_internal# /tmp/guacamole-server/src/libguac/guacamole/client.h: 57

struct_guac_client.__slots__ = [
    'socket',
    'pending_socket',
    'state',
    'data',
    'last_sent_timestamp',
    'free_handler',
    'log_handler',
    'connection_id',
    'connected_users',
    'join_handler',
    'join_pending_handler',
    'leave_handler',
    'args',
    'internal',
]
struct_guac_client._fields_ = [
    ('socket', POINTER(guac_socket)),
    ('pending_socket', POINTER(guac_socket)),
    ('state', guac_client_state),
    ('data', POINTER(None)),
    ('last_sent_timestamp', guac_timestamp),
    ('free_handler', POINTER(guac_client_free_handler)),
    ('log_handler', POINTER(guac_client_log_handler)),
    ('connection_id', String),
    ('connected_users', c_int),
    ('join_handler', POINTER(guac_user_join_handler)),
    ('join_pending_handler', POINTER(guac_client_join_pending_handler)),
    ('leave_handler', POINTER(guac_user_leave_handler)),
    ('args', POINTER(POINTER(c_char))),
    ('internal', POINTER(guac_client_internal)),
]

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 259
if _libs["libguac"].has("guac_client_alloc", "cdecl"):
    guac_client_alloc = _libs["libguac"].get("guac_client_alloc", "cdecl")
    guac_client_alloc.argtypes = []
    guac_client_alloc.restype = POINTER(guac_client)

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 266
if _libs["libguac"].has("guac_client_free", "cdecl"):
    guac_client_free = _libs["libguac"].get("guac_client_free", "cdecl")
    guac_client_free.argtypes = [POINTER(guac_client)]
    guac_client_free.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 278
if _libs["libguac"].has("guac_client_log", "cdecl"):
    _func = _libs["libguac"].get("guac_client_log", "cdecl")
    _restype = None
    _errcheck = None
    _argtypes = [POINTER(guac_client), guac_client_log_level, String]
    guac_client_log = _variadic_function(_func,_restype,_argtypes,_errcheck)

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 292
if _libs["libguac"].has("vguac_client_log", "cdecl"):
    vguac_client_log = _libs["libguac"].get("vguac_client_log", "cdecl")
    vguac_client_log.argtypes = [POINTER(guac_client), guac_client_log_level, String, c_void_p]
    vguac_client_log.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 302
if _libs["libguac"].has("guac_client_stop", "cdecl"):
    guac_client_stop = _libs["libguac"].get("guac_client_stop", "cdecl")
    guac_client_stop.argtypes = [POINTER(guac_client)]
    guac_client_stop.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 315
if _libs["libguac"].has("guac_client_abort", "cdecl"):
    _func = _libs["libguac"].get("guac_client_abort", "cdecl")
    _restype = None
    _errcheck = None
    _argtypes = [POINTER(guac_client), guac_protocol_status, String]
    guac_client_abort = _variadic_function(_func,_restype,_argtypes,_errcheck)

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 330
if _libs["libguac"].has("vguac_client_abort", "cdecl"):
    vguac_client_abort = _libs["libguac"].get("vguac_client_abort", "cdecl")
    vguac_client_abort.argtypes = [POINTER(guac_client), guac_protocol_status, String, c_void_p]
    vguac_client_abort.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 340
if _libs["libguac"].has("guac_client_alloc_buffer", "cdecl"):
    guac_client_alloc_buffer = _libs["libguac"].get("guac_client_alloc_buffer", "cdecl")
    guac_client_alloc_buffer.argtypes = [POINTER(guac_client)]
    guac_client_alloc_buffer.restype = POINTER(guac_layer)

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 349
if _libs["libguac"].has("guac_client_alloc_layer", "cdecl"):
    guac_client_alloc_layer = _libs["libguac"].get("guac_client_alloc_layer", "cdecl")
    guac_client_alloc_layer.argtypes = [POINTER(guac_client)]
    guac_client_alloc_layer.restype = POINTER(guac_layer)

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 358
if _libs["libguac"].has("guac_client_free_buffer", "cdecl"):
    guac_client_free_buffer = _libs["libguac"].get("guac_client_free_buffer", "cdecl")
    guac_client_free_buffer.argtypes = [POINTER(guac_client), POINTER(guac_layer)]
    guac_client_free_buffer.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 367
if _libs["libguac"].has("guac_client_free_layer", "cdecl"):
    guac_client_free_layer = _libs["libguac"].get("guac_client_free_layer", "cdecl")
    guac_client_free_layer.argtypes = [POINTER(guac_client), POINTER(guac_layer)]
    guac_client_free_layer.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 380
if _libs["libguac"].has("guac_client_alloc_stream", "cdecl"):
    guac_client_alloc_stream = _libs["libguac"].get("guac_client_alloc_stream", "cdecl")
    guac_client_alloc_stream.argtypes = [POINTER(guac_client)]
    guac_client_alloc_stream.restype = POINTER(guac_stream)

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 392
if _libs["libguac"].has("guac_client_free_stream", "cdecl"):
    guac_client_free_stream = _libs["libguac"].get("guac_client_free_stream", "cdecl")
    guac_client_free_stream.argtypes = [POINTER(guac_client), POINTER(guac_stream)]
    guac_client_free_stream.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 406
if _libs["libguac"].has("guac_client_add_user", "cdecl"):
    guac_client_add_user = _libs["libguac"].get("guac_client_add_user", "cdecl")
    guac_client_add_user.argtypes = [POINTER(guac_client), POINTER(guac_user), c_int, POINTER(POINTER(c_char))]
    guac_client_add_user.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 415
if _libs["libguac"].has("guac_client_remove_user", "cdecl"):
    guac_client_remove_user = _libs["libguac"].get("guac_client_remove_user", "cdecl")
    guac_client_remove_user.argtypes = [POINTER(guac_client), POINTER(guac_user)]
    guac_client_remove_user.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 437
if _libs["libguac"].has("guac_client_foreach_user", "cdecl"):
    guac_client_foreach_user = _libs["libguac"].get("guac_client_foreach_user", "cdecl")
    guac_client_foreach_user.argtypes = [POINTER(guac_client), POINTER(guac_user_callback), POINTER(None)]
    guac_client_foreach_user.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 457
if _libs["libguac"].has("guac_client_foreach_pending_user", "cdecl"):
    guac_client_foreach_pending_user = _libs["libguac"].get("guac_client_foreach_pending_user", "cdecl")
    guac_client_foreach_pending_user.argtypes = [POINTER(guac_client), POINTER(guac_user_callback), POINTER(None)]
    guac_client_foreach_pending_user.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 486
if _libs["libguac"].has("guac_client_for_owner", "cdecl"):
    guac_client_for_owner = _libs["libguac"].get("guac_client_for_owner", "cdecl")
    guac_client_for_owner.argtypes = [POINTER(guac_client), POINTER(guac_user_callback), POINTER(None)]
    guac_client_for_owner.restype = POINTER(c_ubyte)
    guac_client_for_owner.errcheck = lambda v,*a : cast(v, c_void_p)

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 519
if _libs["libguac"].has("guac_client_for_user", "cdecl"):
    guac_client_for_user = _libs["libguac"].get("guac_client_for_user", "cdecl")
    guac_client_for_user.argtypes = [POINTER(guac_client), POINTER(guac_user), POINTER(guac_user_callback), POINTER(None)]
    guac_client_for_user.restype = POINTER(c_ubyte)
    guac_client_for_user.errcheck = lambda v,*a : cast(v, c_void_p)

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 538
if _libs["libguac"].has("guac_client_end_frame", "cdecl"):
    guac_client_end_frame = _libs["libguac"].get("guac_client_end_frame", "cdecl")
    guac_client_end_frame.argtypes = [POINTER(guac_client)]
    guac_client_end_frame.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 562
if _libs["libguac"].has("guac_client_end_multiple_frames", "cdecl"):
    guac_client_end_multiple_frames = _libs["libguac"].get("guac_client_end_multiple_frames", "cdecl")
    guac_client_end_multiple_frames.argtypes = [POINTER(guac_client), c_int]
    guac_client_end_multiple_frames.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 576
if _libs["libguac"].has("guac_client_load_plugin", "cdecl"):
    guac_client_load_plugin = _libs["libguac"].get("guac_client_load_plugin", "cdecl")
    guac_client_load_plugin.argtypes = [POINTER(guac_client), String]
    guac_client_load_plugin.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 590
if _libs["libguac"].has("guac_client_get_processing_lag", "cdecl"):
    guac_client_get_processing_lag = _libs["libguac"].get("guac_client_get_processing_lag", "cdecl")
    guac_client_get_processing_lag.argtypes = [POINTER(guac_client)]
    guac_client_get_processing_lag.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 606
if _libs["libguac"].has("guac_client_owner_send_required", "cdecl"):
    guac_client_owner_send_required = _libs["libguac"].get("guac_client_owner_send_required", "cdecl")
    guac_client_owner_send_required.argtypes = [POINTER(guac_client), POINTER(POINTER(c_char))]
    guac_client_owner_send_required.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 632
if _libs["libguac"].has("guac_client_stream_argv", "cdecl"):
    guac_client_stream_argv = _libs["libguac"].get("guac_client_stream_argv", "cdecl")
    guac_client_stream_argv.argtypes = [POINTER(guac_client), POINTER(guac_socket), String, String, String]
    guac_client_stream_argv.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 664
if _libs["libguac"].has("guac_client_stream_png", "cdecl"):
    guac_client_stream_png = _libs["libguac"].get("guac_client_stream_png", "cdecl")
    guac_client_stream_png.argtypes = [POINTER(guac_client), POINTER(guac_socket), guac_composite_mode, POINTER(guac_layer), c_int, c_int, POINTER(cairo_surface_t)]
    guac_client_stream_png.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 702
if _libs["libguac"].has("guac_client_stream_jpeg", "cdecl"):
    guac_client_stream_jpeg = _libs["libguac"].get("guac_client_stream_jpeg", "cdecl")
    guac_client_stream_jpeg.argtypes = [POINTER(guac_client), POINTER(guac_socket), guac_composite_mode, POINTER(guac_layer), c_int, c_int, POINTER(cairo_surface_t), c_int]
    guac_client_stream_jpeg.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 747
if _libs["libguac"].has("guac_client_stream_webp", "cdecl"):
    guac_client_stream_webp = _libs["libguac"].get("guac_client_stream_webp", "cdecl")
    guac_client_stream_webp.argtypes = [POINTER(guac_client), POINTER(guac_socket), guac_composite_mode, POINTER(guac_layer), c_int, c_int, POINTER(cairo_surface_t), c_int, c_int]
    guac_client_stream_webp.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 764
if _libs["libguac"].has("guac_client_owner_supports_msg", "cdecl"):
    guac_client_owner_supports_msg = _libs["libguac"].get("guac_client_owner_supports_msg", "cdecl")
    guac_client_owner_supports_msg.argtypes = [POINTER(guac_client)]
    guac_client_owner_supports_msg.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 779
if _libs["libguac"].has("guac_client_owner_supports_required", "cdecl"):
    guac_client_owner_supports_required = _libs["libguac"].get("guac_client_owner_supports_required", "cdecl")
    guac_client_owner_supports_required.argtypes = [POINTER(guac_client)]
    guac_client_owner_supports_required.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 797
if _libs["libguac"].has("guac_client_owner_notify_join", "cdecl"):
    guac_client_owner_notify_join = _libs["libguac"].get("guac_client_owner_notify_join", "cdecl")
    guac_client_owner_notify_join.argtypes = [POINTER(guac_client), POINTER(guac_user)]
    guac_client_owner_notify_join.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 815
if _libs["libguac"].has("guac_client_owner_notify_leave", "cdecl"):
    guac_client_owner_notify_leave = _libs["libguac"].get("guac_client_owner_notify_leave", "cdecl")
    guac_client_owner_notify_leave.argtypes = [POINTER(guac_client), POINTER(guac_user)]
    guac_client_owner_notify_leave.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 828
if _libs["libguac"].has("guac_client_supports_webp", "cdecl"):
    guac_client_supports_webp = _libs["libguac"].get("guac_client_supports_webp", "cdecl")
    guac_client_supports_webp.argtypes = [POINTER(guac_client)]
    guac_client_supports_webp.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/client.h: 833
try:
    GUAC_DEFAULT_LAYER = (POINTER(guac_layer)).in_dll(_libs["libguac"], "GUAC_DEFAULT_LAYER")
except:
    pass

__guac_instruction_handler = CFUNCTYPE(UNCHECKED(c_int), POINTER(guac_user), c_int, POINTER(POINTER(c_char)))# /tmp/guacamole-server/src/libguac/user-handlers.h: 55

# /tmp/guacamole-server/src/libguac/user-handlers.h: 72
class struct___guac_instruction_handler_mapping(Structure):
    pass

struct___guac_instruction_handler_mapping.__slots__ = [
    'opcode',
    'handler',
]
struct___guac_instruction_handler_mapping._fields_ = [
    ('opcode', String),
    ('handler', POINTER(__guac_instruction_handler)),
]

__guac_instruction_handler_mapping = struct___guac_instruction_handler_mapping# /tmp/guacamole-server/src/libguac/user-handlers.h: 72

# /tmp/guacamole-server/src/libguac/user-handlers.h: 79
try:
    __guac_handle_sync = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_sync")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 86
try:
    __guac_handle_mouse = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_mouse")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 93
try:
    __guac_handle_touch = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_touch")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 100
try:
    __guac_handle_key = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_key")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 107
try:
    __guac_handle_audio = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_audio")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 114
try:
    __guac_handle_clipboard = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_clipboard")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 121
try:
    __guac_handle_file = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_file")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 128
try:
    __guac_handle_pipe = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_pipe")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 135
try:
    __guac_handle_argv = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_argv")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 142
try:
    __guac_handle_ack = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_ack")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 149
try:
    __guac_handle_blob = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_blob")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 156
try:
    __guac_handle_end = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_end")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 163
try:
    __guac_handle_get = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_get")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 170
try:
    __guac_handle_put = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_put")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 177
try:
    __guac_handle_size = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_size")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 185
try:
    __guac_handle_disconnect = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_disconnect")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 192
try:
    __guac_handle_nop = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handle_nop")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 198
try:
    __guac_handshake_size_handler = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handshake_size_handler")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 205
try:
    __guac_handshake_audio_handler = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handshake_audio_handler")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 212
try:
    __guac_handshake_video_handler = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handshake_video_handler")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 219
try:
    __guac_handshake_image_handler = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handshake_image_handler")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 226
try:
    __guac_handshake_name_handler = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handshake_name_handler")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 233
try:
    __guac_handshake_timezone_handler = (__guac_instruction_handler).in_dll(_libs["libguac"], "__guac_handshake_timezone_handler")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 242
try:
    __guac_instruction_handler_map = (POINTER(__guac_instruction_handler_mapping)).in_dll(_libs["libguac"], "__guac_instruction_handler_map")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 251
try:
    __guac_handshake_handler_map = (POINTER(__guac_instruction_handler_mapping)).in_dll(_libs["libguac"], "__guac_handshake_handler_map")
except:
    pass

# /tmp/guacamole-server/src/libguac/user-handlers.h: 262
if _libs["libguac"].has("guac_free_mimetypes", "cdecl"):
    guac_free_mimetypes = _libs["libguac"].get("guac_free_mimetypes", "cdecl")
    guac_free_mimetypes.argtypes = [POINTER(POINTER(c_char))]
    guac_free_mimetypes.restype = None

# /tmp/guacamole-server/src/libguac/user-handlers.h: 280
if _libs["libguac"].has("guac_copy_mimetypes", "cdecl"):
    guac_copy_mimetypes = _libs["libguac"].get("guac_copy_mimetypes", "cdecl")
    guac_copy_mimetypes.argtypes = [POINTER(POINTER(c_char)), c_int]
    guac_copy_mimetypes.restype = POINTER(POINTER(c_char))

# /tmp/guacamole-server/src/libguac/user-handlers.h: 309
if _libs["libguac"].has("__guac_user_call_opcode_handler", "cdecl"):
    __guac_user_call_opcode_handler = _libs["libguac"].get("__guac_user_call_opcode_handler", "cdecl")
    __guac_user_call_opcode_handler.argtypes = [POINTER(__guac_instruction_handler_mapping), POINTER(guac_user), String, c_int, POINTER(POINTER(c_char))]
    __guac_user_call_opcode_handler.restype = c_int

struct_guac_client_internal.__slots__ = [
    '__buffer_pool',
    '__layer_pool',
    '__stream_pool',
    '__output_streams',
    '__users_lock',
    '__users',
    '__pending_users_lock',
    '__pending_users_timer',
    '__pending_users_timer_state',
    '__pending_users_timer_mutex',
    '__pending_users',
    '__owner',
    '__plugin_handle',
]
struct_guac_client_internal._fields_ = [
    ('__buffer_pool', POINTER(guac_pool)),
    ('__layer_pool', POINTER(guac_pool)),
    ('__stream_pool', POINTER(guac_pool)),
    ('__output_streams', POINTER(guac_stream)),
    ('__users_lock', guac_rwlock),
    ('__users', POINTER(guac_user)),
    ('__pending_users_lock', guac_rwlock),
    ('__pending_users_timer', timer_t),
    ('__pending_users_timer_state', c_int),
    ('__pending_users_timer_mutex', pthread_mutex_t),
    ('__pending_users', POINTER(guac_user)),
    ('__owner', POINTER(guac_user)),
    ('__plugin_handle', POINTER(None)),
]

enum_guac_status = c_int# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_SUCCESS = 0# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_NO_MEMORY = (GUAC_STATUS_SUCCESS + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_CLOSED = (GUAC_STATUS_NO_MEMORY + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_TIMEOUT = (GUAC_STATUS_CLOSED + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_SEE_ERRNO = (GUAC_STATUS_TIMEOUT + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_IO_ERROR = (GUAC_STATUS_SEE_ERRNO + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_INVALID_ARGUMENT = (GUAC_STATUS_IO_ERROR + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_INTERNAL_ERROR = (GUAC_STATUS_INVALID_ARGUMENT + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_NO_SPACE = (GUAC_STATUS_INTERNAL_ERROR + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_INPUT_TOO_LARGE = (GUAC_STATUS_NO_SPACE + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_RESULT_TOO_LARGE = (GUAC_STATUS_INPUT_TOO_LARGE + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_PERMISSION_DENIED = (GUAC_STATUS_RESULT_TOO_LARGE + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_BUSY = (GUAC_STATUS_PERMISSION_DENIED + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_NOT_AVAILABLE = (GUAC_STATUS_BUSY + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_NOT_SUPPORTED = (GUAC_STATUS_NOT_AVAILABLE + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_NOT_INPLEMENTED = (GUAC_STATUS_NOT_SUPPORTED + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_TRY_AGAIN = (GUAC_STATUS_NOT_INPLEMENTED + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_PROTOCOL_ERROR = (GUAC_STATUS_TRY_AGAIN + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_NOT_FOUND = (GUAC_STATUS_PROTOCOL_ERROR + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_CANCELED = (GUAC_STATUS_NOT_FOUND + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_OUT_OF_RANGE = (GUAC_STATUS_CANCELED + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_REFUSED = (GUAC_STATUS_OUT_OF_RANGE + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_TOO_MANY = (GUAC_STATUS_REFUSED + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

GUAC_STATUS_WOULD_BLOCK = (GUAC_STATUS_TOO_MANY + 1)# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

guac_status = enum_guac_status# /tmp/guacamole-server/src/libguac/guacamole/error-types.h: 178

# /tmp/guacamole-server/src/libguac/guacamole/error.h: 41
if _libs["libguac"].has("guac_status_string", "cdecl"):
    guac_status_string = _libs["libguac"].get("guac_status_string", "cdecl")
    guac_status_string.argtypes = [guac_status]
    if sizeof(c_int) == sizeof(c_void_p):
        guac_status_string.restype = ReturnString
    else:
        guac_status_string.restype = String
        guac_status_string.errcheck = ReturnString

# /tmp/guacamole-server/src/libguac/guacamole/error.h: 53
if _libs["libguac"].has("__guac_error", "cdecl"):
    __guac_error = _libs["libguac"].get("__guac_error", "cdecl")
    __guac_error.argtypes = []
    __guac_error.restype = POINTER(guac_status)

# /tmp/guacamole-server/src/libguac/guacamole/error.h: 66
if _libs["libguac"].has("__guac_error_message", "cdecl"):
    __guac_error_message = _libs["libguac"].get("__guac_error_message", "cdecl")
    __guac_error_message.argtypes = []
    __guac_error_message.restype = POINTER(POINTER(c_char))

enum_guac_parse_state = c_int# /tmp/guacamole-server/src/libguac/guacamole/parser-types.h: 57

guac_parse_state = enum_guac_parse_state# /tmp/guacamole-server/src/libguac/guacamole/parser-types.h: 57

# /tmp/guacamole-server/src/libguac/guacamole/parser.h: 34
class struct_guac_parser(Structure):
    pass

guac_parser = struct_guac_parser# /tmp/guacamole-server/src/libguac/guacamole/parser-types.h: 63

struct_guac_parser.__slots__ = [
    'opcode',
    'argc',
    'argv',
    'state',
    '__element_length',
    '__elementc',
    '__elementv',
    '__instructionbuf_unparsed_start',
    '__instructionbuf_unparsed_end',
    '__instructionbuf',
]
struct_guac_parser._fields_ = [
    ('opcode', String),
    ('argc', c_int),
    ('argv', POINTER(POINTER(c_char))),
    ('state', guac_parse_state),
    ('__element_length', c_int),
    ('__elementc', c_int),
    ('__elementv', POINTER(c_char) * int(128)),
    ('__instructionbuf_unparsed_start', String),
    ('__instructionbuf_unparsed_end', String),
    ('__instructionbuf', c_char * int(32768)),
]

# /tmp/guacamole-server/src/libguac/guacamole/parser.h: 97
if _libs["libguac"].has("guac_parser_alloc", "cdecl"):
    guac_parser_alloc = _libs["libguac"].get("guac_parser_alloc", "cdecl")
    guac_parser_alloc.argtypes = []
    guac_parser_alloc.restype = POINTER(guac_parser)

# /tmp/guacamole-server/src/libguac/guacamole/parser.h: 113
if _libs["libguac"].has("guac_parser_append", "cdecl"):
    guac_parser_append = _libs["libguac"].get("guac_parser_append", "cdecl")
    guac_parser_append.argtypes = [POINTER(guac_parser), POINTER(None), c_int]
    guac_parser_append.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/parser.h: 122
if _libs["libguac"].has("guac_parser_length", "cdecl"):
    guac_parser_length = _libs["libguac"].get("guac_parser_length", "cdecl")
    guac_parser_length.argtypes = [POINTER(guac_parser)]
    guac_parser_length.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/parser.h: 133
if _libs["libguac"].has("guac_parser_shift", "cdecl"):
    guac_parser_shift = _libs["libguac"].get("guac_parser_shift", "cdecl")
    guac_parser_shift.argtypes = [POINTER(guac_parser), POINTER(None), c_int]
    guac_parser_shift.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/parser.h: 140
if _libs["libguac"].has("guac_parser_free", "cdecl"):
    guac_parser_free = _libs["libguac"].get("guac_parser_free", "cdecl")
    guac_parser_free.argtypes = [POINTER(guac_parser)]
    guac_parser_free.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/parser.h: 163
if _libs["libguac"].has("guac_parser_read", "cdecl"):
    guac_parser_read = _libs["libguac"].get("guac_parser_read", "cdecl")
    guac_parser_read.argtypes = [POINTER(guac_parser), POINTER(guac_socket), c_int]
    guac_parser_read.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/parser.h: 186
if _libs["libguac"].has("guac_parser_expect", "cdecl"):
    guac_parser_expect = _libs["libguac"].get("guac_parser_expect", "cdecl")
    guac_parser_expect.argtypes = [POINTER(guac_parser), POINTER(guac_socket), c_int, String]
    guac_parser_expect.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 58
if _libs["libguac"].has("guac_protocol_send_ack", "cdecl"):
    guac_protocol_send_ack = _libs["libguac"].get("guac_protocol_send_ack", "cdecl")
    guac_protocol_send_ack.argtypes = [POINTER(guac_socket), POINTER(guac_stream), String, guac_protocol_status]
    guac_protocol_send_ack.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 71
if _libs["libguac"].has("guac_protocol_send_args", "cdecl"):
    guac_protocol_send_args = _libs["libguac"].get("guac_protocol_send_args", "cdecl")
    guac_protocol_send_args.argtypes = [POINTER(guac_socket), POINTER(POINTER(c_char))]
    guac_protocol_send_args.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 83
if _libs["libguac"].has("guac_protocol_send_connect", "cdecl"):
    guac_protocol_send_connect = _libs["libguac"].get("guac_protocol_send_connect", "cdecl")
    guac_protocol_send_connect.argtypes = [POINTER(guac_socket), POINTER(POINTER(c_char))]
    guac_protocol_send_connect.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 94
if _libs["libguac"].has("guac_protocol_send_disconnect", "cdecl"):
    guac_protocol_send_disconnect = _libs["libguac"].get("guac_protocol_send_disconnect", "cdecl")
    guac_protocol_send_disconnect.argtypes = [POINTER(guac_socket)]
    guac_protocol_send_disconnect.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 107
if _libs["libguac"].has("guac_protocol_send_error", "cdecl"):
    guac_protocol_send_error = _libs["libguac"].get("guac_protocol_send_error", "cdecl")
    guac_protocol_send_error.argtypes = [POINTER(guac_socket), String, guac_protocol_status]
    guac_protocol_send_error.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 133
if _libs["libguac"].has("guac_protocol_send_key", "cdecl"):
    guac_protocol_send_key = _libs["libguac"].get("guac_protocol_send_key", "cdecl")
    guac_protocol_send_key.argtypes = [POINTER(guac_socket), c_int, c_int, guac_timestamp]
    guac_protocol_send_key.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 148
if _libs["libguac"].has("guac_protocol_send_log", "cdecl"):
    _func = _libs["libguac"].get("guac_protocol_send_log", "cdecl")
    _restype = c_int
    _errcheck = None
    _argtypes = [POINTER(guac_socket), String]
    guac_protocol_send_log = _variadic_function(_func,_restype,_argtypes,_errcheck)

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 171
if _libs["libguac"].has("vguac_protocol_send_log", "cdecl"):
    vguac_protocol_send_log = _libs["libguac"].get("vguac_protocol_send_log", "cdecl")
    vguac_protocol_send_log.argtypes = [POINTER(guac_socket), String, c_void_p]
    vguac_protocol_send_log.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 192
if _libs["libguac"].has("guac_protocol_send_msg", "cdecl"):
    guac_protocol_send_msg = _libs["libguac"].get("guac_protocol_send_msg", "cdecl")
    guac_protocol_send_msg.argtypes = [POINTER(guac_socket), guac_message_type, POINTER(POINTER(c_char))]
    guac_protocol_send_msg.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 230
if _libs["libguac"].has("guac_protocol_send_mouse", "cdecl"):
    guac_protocol_send_mouse = _libs["libguac"].get("guac_protocol_send_mouse", "cdecl")
    guac_protocol_send_mouse.argtypes = [POINTER(guac_socket), c_int, c_int, c_int, guac_timestamp]
    guac_protocol_send_mouse.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 276
if _libs["libguac"].has("guac_protocol_send_touch", "cdecl"):
    guac_protocol_send_touch = _libs["libguac"].get("guac_protocol_send_touch", "cdecl")
    guac_protocol_send_touch.argtypes = [POINTER(guac_socket), c_int, c_int, c_int, c_int, c_int, c_double, c_double, guac_timestamp]
    guac_protocol_send_touch.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 300
if _libs["libguac"].has("guac_protocol_send_nest", "cdecl"):
    guac_protocol_send_nest = _libs["libguac"].get("guac_protocol_send_nest", "cdecl")
    guac_protocol_send_nest.argtypes = [POINTER(guac_socket), c_int, String]
    guac_protocol_send_nest.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 313
if _libs["libguac"].has("guac_protocol_send_nop", "cdecl"):
    guac_protocol_send_nop = _libs["libguac"].get("guac_protocol_send_nop", "cdecl")
    guac_protocol_send_nop.argtypes = [POINTER(guac_socket)]
    guac_protocol_send_nop.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 325
if _libs["libguac"].has("guac_protocol_send_ready", "cdecl"):
    guac_protocol_send_ready = _libs["libguac"].get("guac_protocol_send_ready", "cdecl")
    guac_protocol_send_ready.argtypes = [POINTER(guac_socket), String]
    guac_protocol_send_ready.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 339
if _libs["libguac"].has("guac_protocol_send_set", "cdecl"):
    guac_protocol_send_set = _libs["libguac"].get("guac_protocol_send_set", "cdecl")
    guac_protocol_send_set.argtypes = [POINTER(guac_socket), POINTER(guac_layer), String, String]
    guac_protocol_send_set.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 365
if _libs["libguac"].has("guac_protocol_send_set_int", "cdecl"):
    guac_protocol_send_set_int = _libs["libguac"].get("guac_protocol_send_set_int", "cdecl")
    guac_protocol_send_set_int.argtypes = [POINTER(guac_socket), POINTER(guac_layer), String, c_int]
    guac_protocol_send_set_int.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 378
if _libs["libguac"].has("guac_protocol_send_select", "cdecl"):
    guac_protocol_send_select = _libs["libguac"].get("guac_protocol_send_select", "cdecl")
    guac_protocol_send_select.argtypes = [POINTER(guac_socket), String]
    guac_protocol_send_select.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 401
if _libs["libguac"].has("guac_protocol_send_sync", "cdecl"):
    guac_protocol_send_sync = _libs["libguac"].get("guac_protocol_send_sync", "cdecl")
    guac_protocol_send_sync.argtypes = [POINTER(guac_socket), guac_timestamp, c_int]
    guac_protocol_send_sync.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 431
if _libs["libguac"].has("guac_protocol_send_body", "cdecl"):
    guac_protocol_send_body = _libs["libguac"].get("guac_protocol_send_body", "cdecl")
    guac_protocol_send_body.argtypes = [POINTER(guac_socket), POINTER(guac_object), POINTER(guac_stream), String, String]
    guac_protocol_send_body.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 452
if _libs["libguac"].has("guac_protocol_send_filesystem", "cdecl"):
    guac_protocol_send_filesystem = _libs["libguac"].get("guac_protocol_send_filesystem", "cdecl")
    guac_protocol_send_filesystem.argtypes = [POINTER(guac_socket), POINTER(guac_object), String]
    guac_protocol_send_filesystem.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 470
if _libs["libguac"].has("guac_protocol_send_undefine", "cdecl"):
    guac_protocol_send_undefine = _libs["libguac"].get("guac_protocol_send_undefine", "cdecl")
    guac_protocol_send_undefine.argtypes = [POINTER(guac_socket), POINTER(guac_object)]
    guac_protocol_send_undefine.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 493
if _libs["libguac"].has("guac_protocol_send_audio", "cdecl"):
    guac_protocol_send_audio = _libs["libguac"].get("guac_protocol_send_audio", "cdecl")
    guac_protocol_send_audio.argtypes = [POINTER(guac_socket), POINTER(guac_stream), String]
    guac_protocol_send_audio.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 508
if _libs["libguac"].has("guac_protocol_send_file", "cdecl"):
    guac_protocol_send_file = _libs["libguac"].get("guac_protocol_send_file", "cdecl")
    guac_protocol_send_file.argtypes = [POINTER(guac_socket), POINTER(guac_stream), String, String]
    guac_protocol_send_file.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 523
if _libs["libguac"].has("guac_protocol_send_pipe", "cdecl"):
    guac_protocol_send_pipe = _libs["libguac"].get("guac_protocol_send_pipe", "cdecl")
    guac_protocol_send_pipe.argtypes = [POINTER(guac_socket), POINTER(guac_stream), String, String]
    guac_protocol_send_pipe.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 540
if _libs["libguac"].has("guac_protocol_send_blob", "cdecl"):
    guac_protocol_send_blob = _libs["libguac"].get("guac_protocol_send_blob", "cdecl")
    guac_protocol_send_blob.argtypes = [POINTER(guac_socket), POINTER(guac_stream), POINTER(None), c_int]
    guac_protocol_send_blob.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 571
if _libs["libguac"].has("guac_protocol_send_blobs", "cdecl"):
    guac_protocol_send_blobs = _libs["libguac"].get("guac_protocol_send_blobs", "cdecl")
    guac_protocol_send_blobs.argtypes = [POINTER(guac_socket), POINTER(guac_stream), POINTER(None), c_int]
    guac_protocol_send_blobs.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 584
if _libs["libguac"].has("guac_protocol_send_end", "cdecl"):
    guac_protocol_send_end = _libs["libguac"].get("guac_protocol_send_end", "cdecl")
    guac_protocol_send_end.argtypes = [POINTER(guac_socket), POINTER(guac_stream)]
    guac_protocol_send_end.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 607
if _libs["libguac"].has("guac_protocol_send_video", "cdecl"):
    guac_protocol_send_video = _libs["libguac"].get("guac_protocol_send_video", "cdecl")
    guac_protocol_send_video.argtypes = [POINTER(guac_socket), POINTER(guac_stream), POINTER(guac_layer), String]
    guac_protocol_send_video.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 629
if _libs["libguac"].has("guac_protocol_send_arc", "cdecl"):
    guac_protocol_send_arc = _libs["libguac"].get("guac_protocol_send_arc", "cdecl")
    guac_protocol_send_arc.argtypes = [POINTER(guac_socket), POINTER(guac_layer), c_int, c_int, c_int, c_double, c_double, c_int]
    guac_protocol_send_arc.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 648
if _libs["libguac"].has("guac_protocol_send_cfill", "cdecl"):
    guac_protocol_send_cfill = _libs["libguac"].get("guac_protocol_send_cfill", "cdecl")
    guac_protocol_send_cfill.argtypes = [POINTER(guac_socket), guac_composite_mode, POINTER(guac_layer), c_int, c_int, c_int, c_int]
    guac_protocol_send_cfill.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 662
if _libs["libguac"].has("guac_protocol_send_clip", "cdecl"):
    guac_protocol_send_clip = _libs["libguac"].get("guac_protocol_send_clip", "cdecl")
    guac_protocol_send_clip.argtypes = [POINTER(guac_socket), POINTER(guac_layer)]
    guac_protocol_send_clip.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 674
if _libs["libguac"].has("guac_protocol_send_close", "cdecl"):
    guac_protocol_send_close = _libs["libguac"].get("guac_protocol_send_close", "cdecl")
    guac_protocol_send_close.argtypes = [POINTER(guac_socket), POINTER(guac_layer)]
    guac_protocol_send_close.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 696
if _libs["libguac"].has("guac_protocol_send_copy", "cdecl"):
    guac_protocol_send_copy = _libs["libguac"].get("guac_protocol_send_copy", "cdecl")
    guac_protocol_send_copy.argtypes = [POINTER(guac_socket), POINTER(guac_layer), c_int, c_int, c_int, c_int, guac_composite_mode, POINTER(guac_layer), c_int, c_int]
    guac_protocol_send_copy.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 718
if _libs["libguac"].has("guac_protocol_send_cstroke", "cdecl"):
    guac_protocol_send_cstroke = _libs["libguac"].get("guac_protocol_send_cstroke", "cdecl")
    guac_protocol_send_cstroke.argtypes = [POINTER(guac_socket), guac_composite_mode, POINTER(guac_layer), guac_line_cap_style, guac_line_join_style, c_int, c_int, c_int, c_int, c_int]
    guac_protocol_send_cstroke.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 739
if _libs["libguac"].has("guac_protocol_send_cursor", "cdecl"):
    guac_protocol_send_cursor = _libs["libguac"].get("guac_protocol_send_cursor", "cdecl")
    guac_protocol_send_cursor.argtypes = [POINTER(guac_socket), c_int, c_int, POINTER(guac_layer), c_int, c_int, c_int, c_int]
    guac_protocol_send_cursor.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 758
if _libs["libguac"].has("guac_protocol_send_curve", "cdecl"):
    guac_protocol_send_curve = _libs["libguac"].get("guac_protocol_send_curve", "cdecl")
    guac_protocol_send_curve.argtypes = [POINTER(guac_socket), POINTER(guac_layer), c_int, c_int, c_int, c_int, c_int, c_int]
    guac_protocol_send_curve.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 771
if _libs["libguac"].has("guac_protocol_send_identity", "cdecl"):
    guac_protocol_send_identity = _libs["libguac"].get("guac_protocol_send_identity", "cdecl")
    guac_protocol_send_identity.argtypes = [POINTER(guac_socket), POINTER(guac_layer)]
    guac_protocol_send_identity.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 785
if _libs["libguac"].has("guac_protocol_send_lfill", "cdecl"):
    guac_protocol_send_lfill = _libs["libguac"].get("guac_protocol_send_lfill", "cdecl")
    guac_protocol_send_lfill.argtypes = [POINTER(guac_socket), guac_composite_mode, POINTER(guac_layer), POINTER(guac_layer)]
    guac_protocol_send_lfill.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 801
if _libs["libguac"].has("guac_protocol_send_line", "cdecl"):
    guac_protocol_send_line = _libs["libguac"].get("guac_protocol_send_line", "cdecl")
    guac_protocol_send_line.argtypes = [POINTER(guac_socket), POINTER(guac_layer), c_int, c_int]
    guac_protocol_send_line.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 819
if _libs["libguac"].has("guac_protocol_send_lstroke", "cdecl"):
    guac_protocol_send_lstroke = _libs["libguac"].get("guac_protocol_send_lstroke", "cdecl")
    guac_protocol_send_lstroke.argtypes = [POINTER(guac_socket), guac_composite_mode, POINTER(guac_layer), guac_line_cap_style, guac_line_join_style, c_int, POINTER(guac_layer)]
    guac_protocol_send_lstroke.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 857
if _libs["libguac"].has("guac_protocol_send_img", "cdecl"):
    guac_protocol_send_img = _libs["libguac"].get("guac_protocol_send_img", "cdecl")
    guac_protocol_send_img.argtypes = [POINTER(guac_socket), POINTER(guac_stream), guac_composite_mode, POINTER(guac_layer), String, c_int, c_int]
    guac_protocol_send_img.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 871
if _libs["libguac"].has("guac_protocol_send_pop", "cdecl"):
    guac_protocol_send_pop = _libs["libguac"].get("guac_protocol_send_pop", "cdecl")
    guac_protocol_send_pop.argtypes = [POINTER(guac_socket), POINTER(guac_layer)]
    guac_protocol_send_pop.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 883
if _libs["libguac"].has("guac_protocol_send_push", "cdecl"):
    guac_protocol_send_push = _libs["libguac"].get("guac_protocol_send_push", "cdecl")
    guac_protocol_send_push.argtypes = [POINTER(guac_socket), POINTER(guac_layer)]
    guac_protocol_send_push.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 899
if _libs["libguac"].has("guac_protocol_send_rect", "cdecl"):
    guac_protocol_send_rect = _libs["libguac"].get("guac_protocol_send_rect", "cdecl")
    guac_protocol_send_rect.argtypes = [POINTER(guac_socket), POINTER(guac_layer), c_int, c_int, c_int, c_int]
    guac_protocol_send_rect.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 916
if _libs["libguac"].has("guac_protocol_send_required", "cdecl"):
    guac_protocol_send_required = _libs["libguac"].get("guac_protocol_send_required", "cdecl")
    guac_protocol_send_required.argtypes = [POINTER(guac_socket), POINTER(POINTER(c_char))]
    guac_protocol_send_required.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 928
if _libs["libguac"].has("guac_protocol_send_reset", "cdecl"):
    guac_protocol_send_reset = _libs["libguac"].get("guac_protocol_send_reset", "cdecl")
    guac_protocol_send_reset.argtypes = [POINTER(guac_socket), POINTER(guac_layer)]
    guac_protocol_send_reset.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 942
if _libs["libguac"].has("guac_protocol_send_start", "cdecl"):
    guac_protocol_send_start = _libs["libguac"].get("guac_protocol_send_start", "cdecl")
    guac_protocol_send_start.argtypes = [POINTER(guac_socket), POINTER(guac_layer), c_int, c_int]
    guac_protocol_send_start.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 965
if _libs["libguac"].has("guac_protocol_send_transfer", "cdecl"):
    guac_protocol_send_transfer = _libs["libguac"].get("guac_protocol_send_transfer", "cdecl")
    guac_protocol_send_transfer.argtypes = [POINTER(guac_socket), POINTER(guac_layer), c_int, c_int, c_int, c_int, guac_transfer_function, POINTER(guac_layer), c_int, c_int]
    guac_protocol_send_transfer.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 985
if _libs["libguac"].has("guac_protocol_send_transform", "cdecl"):
    guac_protocol_send_transform = _libs["libguac"].get("guac_protocol_send_transform", "cdecl")
    guac_protocol_send_transform.argtypes = [POINTER(guac_socket), POINTER(guac_layer), c_double, c_double, c_double, c_double, c_double, c_double]
    guac_protocol_send_transform.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 1002
if _libs["libguac"].has("guac_protocol_send_dispose", "cdecl"):
    guac_protocol_send_dispose = _libs["libguac"].get("guac_protocol_send_dispose", "cdecl")
    guac_protocol_send_dispose.argtypes = [POINTER(guac_socket), POINTER(guac_layer)]
    guac_protocol_send_dispose.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 1020
if _libs["libguac"].has("guac_protocol_send_distort", "cdecl"):
    guac_protocol_send_distort = _libs["libguac"].get("guac_protocol_send_distort", "cdecl")
    guac_protocol_send_distort.argtypes = [POINTER(guac_socket), POINTER(guac_layer), c_double, c_double, c_double, c_double, c_double, c_double]
    guac_protocol_send_distort.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 1040
if _libs["libguac"].has("guac_protocol_send_move", "cdecl"):
    guac_protocol_send_move = _libs["libguac"].get("guac_protocol_send_move", "cdecl")
    guac_protocol_send_move.argtypes = [POINTER(guac_socket), POINTER(guac_layer), POINTER(guac_layer), c_int, c_int, c_int]
    guac_protocol_send_move.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 1054
if _libs["libguac"].has("guac_protocol_send_shade", "cdecl"):
    guac_protocol_send_shade = _libs["libguac"].get("guac_protocol_send_shade", "cdecl")
    guac_protocol_send_shade.argtypes = [POINTER(guac_socket), POINTER(guac_layer), c_int]
    guac_protocol_send_shade.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 1069
if _libs["libguac"].has("guac_protocol_send_size", "cdecl"):
    guac_protocol_send_size = _libs["libguac"].get("guac_protocol_send_size", "cdecl")
    guac_protocol_send_size.argtypes = [POINTER(guac_socket), POINTER(guac_layer), c_int, c_int]
    guac_protocol_send_size.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 1096
if _libs["libguac"].has("guac_protocol_send_argv", "cdecl"):
    guac_protocol_send_argv = _libs["libguac"].get("guac_protocol_send_argv", "cdecl")
    guac_protocol_send_argv.argtypes = [POINTER(guac_socket), POINTER(guac_stream), String, String]
    guac_protocol_send_argv.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 1110
if _libs["libguac"].has("guac_protocol_send_clipboard", "cdecl"):
    guac_protocol_send_clipboard = _libs["libguac"].get("guac_protocol_send_clipboard", "cdecl")
    guac_protocol_send_clipboard.argtypes = [POINTER(guac_socket), POINTER(guac_stream), String]
    guac_protocol_send_clipboard.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 1120
if _libs["libguac"].has("guac_protocol_send_name", "cdecl"):
    guac_protocol_send_name = _libs["libguac"].get("guac_protocol_send_name", "cdecl")
    guac_protocol_send_name.argtypes = [POINTER(guac_socket), String]
    guac_protocol_send_name.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 1129
if _libs["libguac"].has("guac_protocol_decode_base64", "cdecl"):
    guac_protocol_decode_base64 = _libs["libguac"].get("guac_protocol_decode_base64", "cdecl")
    guac_protocol_decode_base64.argtypes = [String]
    guac_protocol_decode_base64.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 1143
if _libs["libguac"].has("guac_protocol_string_to_version", "cdecl"):
    guac_protocol_string_to_version = _libs["libguac"].get("guac_protocol_string_to_version", "cdecl")
    guac_protocol_string_to_version.argtypes = [String]
    guac_protocol_string_to_version.restype = guac_protocol_version

# /tmp/guacamole-server/src/libguac/guacamole/protocol.h: 1156
if _libs["libguac"].has("guac_protocol_version_to_string", "cdecl"):
    guac_protocol_version_to_string = _libs["libguac"].get("guac_protocol_version_to_string", "cdecl")
    guac_protocol_version_to_string.argtypes = [guac_protocol_version]
    guac_protocol_version_to_string.restype = c_char_p

# /usr/include/bits/alltypes.h: 355
class struct_iovec(Structure):
    pass

struct_iovec.__slots__ = [
    'iov_base',
    'iov_len',
]
struct_iovec._fields_ = [
    ('iov_base', POINTER(None)),
    ('iov_len', c_size_t),
]

socklen_t = c_uint# /usr/include/bits/alltypes.h: 367

sa_family_t = c_ushort# /usr/include/bits/alltypes.h: 372

# /usr/include/sys/socket.h: 22
class struct_msghdr(Structure):
    pass

struct_msghdr.__slots__ = [
    'msg_name',
    'msg_namelen',
    'msg_iov',
    'msg_iovlen',
    '__pad1',
    'msg_control',
    'msg_controllen',
    '__pad2',
    'msg_flags',
]
struct_msghdr._fields_ = [
    ('msg_name', POINTER(None)),
    ('msg_namelen', socklen_t),
    ('msg_iov', POINTER(struct_iovec)),
    ('msg_iovlen', c_int),
    ('__pad1', c_int),
    ('msg_control', POINTER(None)),
    ('msg_controllen', socklen_t),
    ('__pad2', c_int),
    ('msg_flags', c_int),
]

# /usr/include/sys/socket.h: 44
class struct_cmsghdr(Structure):
    pass

struct_cmsghdr.__slots__ = [
    'cmsg_len',
    '__pad1',
    'cmsg_level',
    'cmsg_type',
]
struct_cmsghdr._fields_ = [
    ('cmsg_len', socklen_t),
    ('__pad1', c_int),
    ('cmsg_level', c_int),
    ('cmsg_type', c_int),
]

# /usr/include/sys/socket.h: 74
class struct_linger(Structure):
    pass

struct_linger.__slots__ = [
    'l_onoff',
    'l_linger',
]
struct_linger._fields_ = [
    ('l_onoff', c_int),
    ('l_linger', c_int),
]

# /usr/include/sys/socket.h: 369
class struct_sockaddr(Structure):
    pass

struct_sockaddr.__slots__ = [
    'sa_family',
    'sa_data',
]
struct_sockaddr._fields_ = [
    ('sa_family', sa_family_t),
    ('sa_data', c_char * int(14)),
]

# /usr/include/sys/socket.h: 374
class struct_sockaddr_storage(Structure):
    pass

struct_sockaddr_storage.__slots__ = [
    'ss_family',
    '__ss_padding',
    '__ss_align',
]
struct_sockaddr_storage._fields_ = [
    ('ss_family', sa_family_t),
    ('__ss_padding', c_char * int(((128 - sizeof(c_long)) - sizeof(sa_family_t)))),
    ('__ss_align', c_ulong),
]

# /usr/include/sys/socket.h: 380
if _libs["libguac"].has("socket", "cdecl"):
    socket = _libs["libguac"].get("socket", "cdecl")
    socket.argtypes = [c_int, c_int, c_int]
    socket.restype = c_int

# /usr/include/sys/socket.h: 381
if _libs["libguac"].has("socketpair", "cdecl"):
    socketpair = _libs["libguac"].get("socketpair", "cdecl")
    socketpair.argtypes = [c_int, c_int, c_int, c_int * int(2)]
    socketpair.restype = c_int

# /usr/include/sys/socket.h: 383
if _libs["libguac"].has("shutdown", "cdecl"):
    shutdown = _libs["libguac"].get("shutdown", "cdecl")
    shutdown.argtypes = [c_int, c_int]
    shutdown.restype = c_int

# /usr/include/sys/socket.h: 385
if _libs["libguac"].has("bind", "cdecl"):
    bind = _libs["libguac"].get("bind", "cdecl")
    bind.argtypes = [c_int, POINTER(struct_sockaddr), socklen_t]
    bind.restype = c_int

# /usr/include/sys/socket.h: 386
if _libs["libguac"].has("connect", "cdecl"):
    connect = _libs["libguac"].get("connect", "cdecl")
    connect.argtypes = [c_int, POINTER(struct_sockaddr), socklen_t]
    connect.restype = c_int

# /usr/include/sys/socket.h: 387
if _libs["libguac"].has("listen", "cdecl"):
    listen = _libs["libguac"].get("listen", "cdecl")
    listen.argtypes = [c_int, c_int]
    listen.restype = c_int

# /usr/include/sys/socket.h: 388
if _libs["libguac"].has("accept", "cdecl"):
    accept = _libs["libguac"].get("accept", "cdecl")
    accept.argtypes = [c_int, POINTER(struct_sockaddr), POINTER(socklen_t)]
    accept.restype = c_int

# /usr/include/sys/socket.h: 389
if _libs["libguac"].has("accept4", "cdecl"):
    accept4 = _libs["libguac"].get("accept4", "cdecl")
    accept4.argtypes = [c_int, POINTER(struct_sockaddr), POINTER(socklen_t), c_int]
    accept4.restype = c_int

# /usr/include/sys/socket.h: 391
if _libs["libguac"].has("getsockname", "cdecl"):
    getsockname = _libs["libguac"].get("getsockname", "cdecl")
    getsockname.argtypes = [c_int, POINTER(struct_sockaddr), POINTER(socklen_t)]
    getsockname.restype = c_int

# /usr/include/sys/socket.h: 392
if _libs["libguac"].has("getpeername", "cdecl"):
    getpeername = _libs["libguac"].get("getpeername", "cdecl")
    getpeername.argtypes = [c_int, POINTER(struct_sockaddr), POINTER(socklen_t)]
    getpeername.restype = c_int

# /usr/include/sys/socket.h: 394
if _libs["libguac"].has("send", "cdecl"):
    send = _libs["libguac"].get("send", "cdecl")
    send.argtypes = [c_int, POINTER(None), c_size_t, c_int]
    send.restype = c_ptrdiff_t

# /usr/include/sys/socket.h: 395
if _libs["libguac"].has("recv", "cdecl"):
    recv = _libs["libguac"].get("recv", "cdecl")
    recv.argtypes = [c_int, POINTER(None), c_size_t, c_int]
    recv.restype = c_ptrdiff_t

# /usr/include/sys/socket.h: 396
if _libs["libguac"].has("sendto", "cdecl"):
    sendto = _libs["libguac"].get("sendto", "cdecl")
    sendto.argtypes = [c_int, POINTER(None), c_size_t, c_int, POINTER(struct_sockaddr), socklen_t]
    sendto.restype = c_ptrdiff_t

# /usr/include/sys/socket.h: 397
if _libs["libguac"].has("recvfrom", "cdecl"):
    recvfrom = _libs["libguac"].get("recvfrom", "cdecl")
    recvfrom.argtypes = [c_int, POINTER(None), c_size_t, c_int, POINTER(struct_sockaddr), POINTER(socklen_t)]
    recvfrom.restype = c_ptrdiff_t

# /usr/include/sys/socket.h: 398
if _libs["libguac"].has("sendmsg", "cdecl"):
    sendmsg = _libs["libguac"].get("sendmsg", "cdecl")
    sendmsg.argtypes = [c_int, POINTER(struct_msghdr), c_int]
    sendmsg.restype = c_ptrdiff_t

# /usr/include/sys/socket.h: 399
if _libs["libguac"].has("recvmsg", "cdecl"):
    recvmsg = _libs["libguac"].get("recvmsg", "cdecl")
    recvmsg.argtypes = [c_int, POINTER(struct_msghdr), c_int]
    recvmsg.restype = c_ptrdiff_t

# /usr/include/sys/socket.h: 401
if _libs["libguac"].has("getsockopt", "cdecl"):
    getsockopt = _libs["libguac"].get("getsockopt", "cdecl")
    getsockopt.argtypes = [c_int, c_int, c_int, POINTER(None), POINTER(socklen_t)]
    getsockopt.restype = c_int

# /usr/include/sys/socket.h: 402
if _libs["libguac"].has("setsockopt", "cdecl"):
    setsockopt = _libs["libguac"].get("setsockopt", "cdecl")
    setsockopt.argtypes = [c_int, c_int, c_int, POINTER(None), socklen_t]
    setsockopt.restype = c_int

# /usr/include/sys/socket.h: 404
if _libs["libguac"].has("sockatmark", "cdecl"):
    sockatmark = _libs["libguac"].get("sockatmark", "cdecl")
    sockatmark.argtypes = [c_int]
    sockatmark.restype = c_int

# /usr/include/czmq_library.h: 108
class struct__zsock_t(Structure):
    pass

zsock_t = struct__zsock_t# /usr/include/czmq_library.h: 108

# /tmp/guacamole-server/src/libguac/guacamole/socket-zmq.h: 32
if _libs["libguac"].has("guac_socket_open_zmq", "cdecl"):
    guac_socket_open_zmq = _libs["libguac"].get("guac_socket_open_zmq", "cdecl")
    guac_socket_open_zmq.argtypes = [zsock_t]
    guac_socket_open_zmq.restype = POINTER(guac_socket)

# /tmp/guacamole-server/src/libguac/guacamole/socket-zmq.h: 67
if _libs["libguac"].has("guac_socket_create_zmq", "cdecl"):
    guac_socket_create_zmq = _libs["libguac"].get("guac_socket_create_zmq", "cdecl")
    guac_socket_create_zmq.argtypes = [c_int, String, c_bool]
    guac_socket_create_zmq.restype = POINTER(guac_socket)

struct_guac_user_info.__slots__ = [
    'optimal_width',
    'optimal_height',
    'audio_mimetypes',
    'video_mimetypes',
    'image_mimetypes',
    'optimal_resolution',
    'timezone',
    'protocol_version',
    'name',
]
struct_guac_user_info._fields_ = [
    ('optimal_width', c_int),
    ('optimal_height', c_int),
    ('audio_mimetypes', POINTER(POINTER(c_char))),
    ('video_mimetypes', POINTER(POINTER(c_char))),
    ('image_mimetypes', POINTER(POINTER(c_char))),
    ('optimal_resolution', c_int),
    ('timezone', String),
    ('protocol_version', guac_protocol_version),
    ('name', String),
]

struct_guac_user.__slots__ = [
    'client',
    'socket',
    'user_id',
    'owner',
    'active',
    '__prev',
    '__next',
    'last_received_timestamp',
    'last_frame_duration',
    'processing_lag',
    'info',
    '__stream_pool',
    '__output_streams',
    '__input_streams',
    '__object_pool',
    '__objects',
    'data',
    'mouse_handler',
    'key_handler',
    'clipboard_handler',
    'size_handler',
    'file_handler',
    'pipe_handler',
    'ack_handler',
    'blob_handler',
    'end_handler',
    'sync_handler',
    'leave_handler',
    'get_handler',
    'put_handler',
    'audio_handler',
    'argv_handler',
    'touch_handler',
]
struct_guac_user._fields_ = [
    ('client', POINTER(guac_client)),
    ('socket', POINTER(guac_socket)),
    ('user_id', String),
    ('owner', c_int),
    ('active', c_int),
    ('__prev', POINTER(guac_user)),
    ('__next', POINTER(guac_user)),
    ('last_received_timestamp', guac_timestamp),
    ('last_frame_duration', c_int),
    ('processing_lag', c_int),
    ('info', guac_user_info),
    ('__stream_pool', POINTER(guac_pool)),
    ('__output_streams', POINTER(guac_stream)),
    ('__input_streams', POINTER(guac_stream)),
    ('__object_pool', POINTER(guac_pool)),
    ('__objects', POINTER(guac_object)),
    ('data', POINTER(None)),
    ('mouse_handler', POINTER(guac_user_mouse_handler)),
    ('key_handler', POINTER(guac_user_key_handler)),
    ('clipboard_handler', POINTER(guac_user_clipboard_handler)),
    ('size_handler', POINTER(guac_user_size_handler)),
    ('file_handler', POINTER(guac_user_file_handler)),
    ('pipe_handler', POINTER(guac_user_pipe_handler)),
    ('ack_handler', POINTER(guac_user_ack_handler)),
    ('blob_handler', POINTER(guac_user_blob_handler)),
    ('end_handler', POINTER(guac_user_end_handler)),
    ('sync_handler', POINTER(guac_user_sync_handler)),
    ('leave_handler', POINTER(guac_user_leave_handler)),
    ('get_handler', POINTER(guac_user_get_handler)),
    ('put_handler', POINTER(guac_user_put_handler)),
    ('audio_handler', POINTER(guac_user_audio_handler)),
    ('argv_handler', POINTER(guac_user_argv_handler)),
    ('touch_handler', POINTER(guac_user_touch_handler)),
]

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 549
if _libs["libguac"].has("guac_user_alloc", "cdecl"):
    guac_user_alloc = _libs["libguac"].get("guac_user_alloc", "cdecl")
    guac_user_alloc.argtypes = []
    guac_user_alloc.restype = POINTER(guac_user)

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 556
if _libs["libguac"].has("guac_user_free", "cdecl"):
    guac_user_free = _libs["libguac"].get("guac_user_free", "cdecl")
    guac_user_free.argtypes = [POINTER(guac_user)]
    guac_user_free.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 580
if _libs["libguac"].has("guac_user_handle_connection", "cdecl"):
    guac_user_handle_connection = _libs["libguac"].get("guac_user_handle_connection", "cdecl")
    guac_user_handle_connection.argtypes = [POINTER(guac_user), c_int]
    guac_user_handle_connection.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 605
if _libs["libguac"].has("guac_user_handle_instruction", "cdecl"):
    guac_user_handle_instruction = _libs["libguac"].get("guac_user_handle_instruction", "cdecl")
    guac_user_handle_instruction.argtypes = [POINTER(guac_user), String, c_int, POINTER(POINTER(c_char))]
    guac_user_handle_instruction.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 619
if _libs["libguac"].has("guac_user_alloc_stream", "cdecl"):
    guac_user_alloc_stream = _libs["libguac"].get("guac_user_alloc_stream", "cdecl")
    guac_user_alloc_stream.argtypes = [POINTER(guac_user)]
    guac_user_alloc_stream.restype = POINTER(guac_stream)

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 628
if _libs["libguac"].has("guac_user_free_stream", "cdecl"):
    guac_user_free_stream = _libs["libguac"].get("guac_user_free_stream", "cdecl")
    guac_user_free_stream.argtypes = [POINTER(guac_user), POINTER(guac_stream)]
    guac_user_free_stream.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 636
if _libs["libguac"].has("guac_user_stop", "cdecl"):
    guac_user_stop = _libs["libguac"].get("guac_user_stop", "cdecl")
    guac_user_stop.argtypes = [POINTER(guac_user)]
    guac_user_stop.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 649
if _libs["libguac"].has("guac_user_abort", "cdecl"):
    _func = _libs["libguac"].get("guac_user_abort", "cdecl")
    _restype = None
    _errcheck = None
    _argtypes = [POINTER(guac_user), guac_protocol_status, String]
    guac_user_abort = _variadic_function(_func,_restype,_argtypes,_errcheck)

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 664
if _libs["libguac"].has("vguac_user_abort", "cdecl"):
    vguac_user_abort = _libs["libguac"].get("vguac_user_abort", "cdecl")
    vguac_user_abort.argtypes = [POINTER(guac_user), guac_protocol_status, String, c_void_p]
    vguac_user_abort.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 677
if _libs["libguac"].has("guac_user_log", "cdecl"):
    _func = _libs["libguac"].get("guac_user_log", "cdecl")
    _restype = None
    _errcheck = None
    _argtypes = [POINTER(guac_user), guac_client_log_level, String]
    guac_user_log = _variadic_function(_func,_restype,_argtypes,_errcheck)

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 691
if _libs["libguac"].has("vguac_user_log", "cdecl"):
    vguac_user_log = _libs["libguac"].get("vguac_user_log", "cdecl")
    vguac_user_log.argtypes = [POINTER(guac_user), guac_client_log_level, String, c_void_p]
    vguac_user_log.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 704
if _libs["libguac"].has("guac_user_alloc_object", "cdecl"):
    guac_user_alloc_object = _libs["libguac"].get("guac_user_alloc_object", "cdecl")
    guac_user_alloc_object.argtypes = [POINTER(guac_user)]
    guac_user_alloc_object.restype = POINTER(guac_object)

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 716
if _libs["libguac"].has("guac_user_free_object", "cdecl"):
    guac_user_free_object = _libs["libguac"].get("guac_user_free_object", "cdecl")
    guac_user_free_object.argtypes = [POINTER(guac_user), POINTER(guac_object)]
    guac_user_free_object.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 741
if _libs["libguac"].has("guac_user_stream_argv", "cdecl"):
    guac_user_stream_argv = _libs["libguac"].get("guac_user_stream_argv", "cdecl")
    guac_user_stream_argv.argtypes = [POINTER(guac_user), POINTER(guac_socket), String, String, String]
    guac_user_stream_argv.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 773
if _libs["libguac"].has("guac_user_stream_png", "cdecl"):
    guac_user_stream_png = _libs["libguac"].get("guac_user_stream_png", "cdecl")
    guac_user_stream_png.argtypes = [POINTER(guac_user), POINTER(guac_socket), guac_composite_mode, POINTER(guac_layer), c_int, c_int, POINTER(cairo_surface_t)]
    guac_user_stream_png.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 811
if _libs["libguac"].has("guac_user_stream_jpeg", "cdecl"):
    guac_user_stream_jpeg = _libs["libguac"].get("guac_user_stream_jpeg", "cdecl")
    guac_user_stream_jpeg.argtypes = [POINTER(guac_user), POINTER(guac_socket), guac_composite_mode, POINTER(guac_layer), c_int, c_int, POINTER(cairo_surface_t), c_int]
    guac_user_stream_jpeg.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 857
if _libs["libguac"].has("guac_user_stream_webp", "cdecl"):
    guac_user_stream_webp = _libs["libguac"].get("guac_user_stream_webp", "cdecl")
    guac_user_stream_webp.argtypes = [POINTER(guac_user), POINTER(guac_socket), guac_composite_mode, POINTER(guac_layer), c_int, c_int, POINTER(cairo_surface_t), c_int, c_int]
    guac_user_stream_webp.restype = None

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 870
if _libs["libguac"].has("guac_user_supports_msg", "cdecl"):
    guac_user_supports_msg = _libs["libguac"].get("guac_user_supports_msg", "cdecl")
    guac_user_supports_msg.argtypes = [POINTER(guac_user)]
    guac_user_supports_msg.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 881
if _libs["libguac"].has("guac_user_supports_required", "cdecl"):
    guac_user_supports_required = _libs["libguac"].get("guac_user_supports_required", "cdecl")
    guac_user_supports_required.argtypes = [POINTER(guac_user)]
    guac_user_supports_required.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 894
if _libs["libguac"].has("guac_user_supports_webp", "cdecl"):
    guac_user_supports_webp = _libs["libguac"].get("guac_user_supports_webp", "cdecl")
    guac_user_supports_webp.argtypes = [POINTER(guac_user)]
    guac_user_supports_webp.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 932
if _libs["libguac"].has("guac_user_parse_args_string", "cdecl"):
    guac_user_parse_args_string = _libs["libguac"].get("guac_user_parse_args_string", "cdecl")
    guac_user_parse_args_string.argtypes = [POINTER(guac_user), POINTER(POINTER(c_char)), POINTER(POINTER(c_char)), c_int, String]
    if sizeof(c_int) == sizeof(c_void_p):
        guac_user_parse_args_string.restype = ReturnString
    else:
        guac_user_parse_args_string.restype = String
        guac_user_parse_args_string.errcheck = ReturnString

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 965
if _libs["libguac"].has("guac_user_parse_args_int", "cdecl"):
    guac_user_parse_args_int = _libs["libguac"].get("guac_user_parse_args_int", "cdecl")
    guac_user_parse_args_int.argtypes = [POINTER(guac_user), POINTER(POINTER(c_char)), POINTER(POINTER(c_char)), c_int, c_int]
    guac_user_parse_args_int.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/user.h: 1001
if _libs["libguac"].has("guac_user_parse_args_boolean", "cdecl"):
    guac_user_parse_args_boolean = _libs["libguac"].get("guac_user_parse_args_boolean", "cdecl")
    guac_user_parse_args_boolean.argtypes = [POINTER(guac_user), POINTER(POINTER(c_char)), POINTER(POINTER(c_char)), c_int, c_int]
    guac_user_parse_args_boolean.restype = c_int

# /tmp/guacamole-server/src/libguac/guacamole/error.h: 51
try:
    guac_error = ((__guac_error ())[0])
except:
    pass

# /tmp/guacamole-server/src/libguac/guacamole/error.h: 64
try:
    guac_error_message = ((__guac_error_message ())[0])
except:
    pass

# /usr/include/sys/socket.h: 79
try:
    SHUT_RD = 0
except:
    pass

# /usr/include/sys/socket.h: 80
try:
    SHUT_WR = 1
except:
    pass

# /usr/include/sys/socket.h: 81
try:
    SHUT_RDWR = 2
except:
    pass

# /usr/include/sys/socket.h: 84
try:
    SOCK_STREAM = 1
except:
    pass

# /usr/include/sys/socket.h: 85
try:
    SOCK_DGRAM = 2
except:
    pass

# /usr/include/sys/socket.h: 88
try:
    SOCK_RAW = 3
except:
    pass

# /usr/include/sys/socket.h: 89
try:
    SOCK_RDM = 4
except:
    pass

# /usr/include/sys/socket.h: 90
try:
    SOCK_SEQPACKET = 5
except:
    pass

# /usr/include/sys/socket.h: 91
try:
    SOCK_DCCP = 6
except:
    pass

# /usr/include/sys/socket.h: 92
try:
    SOCK_PACKET = 10
except:
    pass

# /usr/include/sys/socket.h: 95
try:
    SOCK_CLOEXEC = 0o2000000
except:
    pass

# /usr/include/sys/socket.h: 96
try:
    SOCK_NONBLOCK = 0o4000
except:
    pass

# /usr/include/sys/socket.h: 99
try:
    PF_UNSPEC = 0
except:
    pass

# /usr/include/sys/socket.h: 100
try:
    PF_LOCAL = 1
except:
    pass

# /usr/include/sys/socket.h: 101
try:
    PF_UNIX = PF_LOCAL
except:
    pass

# /usr/include/sys/socket.h: 102
try:
    PF_FILE = PF_LOCAL
except:
    pass

# /usr/include/sys/socket.h: 103
try:
    PF_INET = 2
except:
    pass

# /usr/include/sys/socket.h: 104
try:
    PF_AX25 = 3
except:
    pass

# /usr/include/sys/socket.h: 105
try:
    PF_IPX = 4
except:
    pass

# /usr/include/sys/socket.h: 106
try:
    PF_APPLETALK = 5
except:
    pass

# /usr/include/sys/socket.h: 107
try:
    PF_NETROM = 6
except:
    pass

# /usr/include/sys/socket.h: 108
try:
    PF_BRIDGE = 7
except:
    pass

# /usr/include/sys/socket.h: 109
try:
    PF_ATMPVC = 8
except:
    pass

# /usr/include/sys/socket.h: 110
try:
    PF_X25 = 9
except:
    pass

# /usr/include/sys/socket.h: 111
try:
    PF_INET6 = 10
except:
    pass

# /usr/include/sys/socket.h: 112
try:
    PF_ROSE = 11
except:
    pass

# /usr/include/sys/socket.h: 113
try:
    PF_DECnet = 12
except:
    pass

# /usr/include/sys/socket.h: 114
try:
    PF_NETBEUI = 13
except:
    pass

# /usr/include/sys/socket.h: 115
try:
    PF_SECURITY = 14
except:
    pass

# /usr/include/sys/socket.h: 116
try:
    PF_KEY = 15
except:
    pass

# /usr/include/sys/socket.h: 117
try:
    PF_NETLINK = 16
except:
    pass

# /usr/include/sys/socket.h: 118
try:
    PF_ROUTE = PF_NETLINK
except:
    pass

# /usr/include/sys/socket.h: 119
try:
    PF_PACKET = 17
except:
    pass

# /usr/include/sys/socket.h: 120
try:
    PF_ASH = 18
except:
    pass

# /usr/include/sys/socket.h: 121
try:
    PF_ECONET = 19
except:
    pass

# /usr/include/sys/socket.h: 122
try:
    PF_ATMSVC = 20
except:
    pass

# /usr/include/sys/socket.h: 123
try:
    PF_RDS = 21
except:
    pass

# /usr/include/sys/socket.h: 124
try:
    PF_SNA = 22
except:
    pass

# /usr/include/sys/socket.h: 125
try:
    PF_IRDA = 23
except:
    pass

# /usr/include/sys/socket.h: 126
try:
    PF_PPPOX = 24
except:
    pass

# /usr/include/sys/socket.h: 127
try:
    PF_WANPIPE = 25
except:
    pass

# /usr/include/sys/socket.h: 128
try:
    PF_LLC = 26
except:
    pass

# /usr/include/sys/socket.h: 129
try:
    PF_IB = 27
except:
    pass

# /usr/include/sys/socket.h: 130
try:
    PF_MPLS = 28
except:
    pass

# /usr/include/sys/socket.h: 131
try:
    PF_CAN = 29
except:
    pass

# /usr/include/sys/socket.h: 132
try:
    PF_TIPC = 30
except:
    pass

# /usr/include/sys/socket.h: 133
try:
    PF_BLUETOOTH = 31
except:
    pass

# /usr/include/sys/socket.h: 134
try:
    PF_IUCV = 32
except:
    pass

# /usr/include/sys/socket.h: 135
try:
    PF_RXRPC = 33
except:
    pass

# /usr/include/sys/socket.h: 136
try:
    PF_ISDN = 34
except:
    pass

# /usr/include/sys/socket.h: 137
try:
    PF_PHONET = 35
except:
    pass

# /usr/include/sys/socket.h: 138
try:
    PF_IEEE802154 = 36
except:
    pass

# /usr/include/sys/socket.h: 139
try:
    PF_CAIF = 37
except:
    pass

# /usr/include/sys/socket.h: 140
try:
    PF_ALG = 38
except:
    pass

# /usr/include/sys/socket.h: 141
try:
    PF_NFC = 39
except:
    pass

# /usr/include/sys/socket.h: 142
try:
    PF_VSOCK = 40
except:
    pass

# /usr/include/sys/socket.h: 143
try:
    PF_KCM = 41
except:
    pass

# /usr/include/sys/socket.h: 144
try:
    PF_QIPCRTR = 42
except:
    pass

# /usr/include/sys/socket.h: 145
try:
    PF_SMC = 43
except:
    pass

# /usr/include/sys/socket.h: 146
try:
    PF_XDP = 44
except:
    pass

# /usr/include/sys/socket.h: 147
try:
    PF_MAX = 45
except:
    pass

# /usr/include/sys/socket.h: 149
try:
    AF_UNSPEC = PF_UNSPEC
except:
    pass

# /usr/include/sys/socket.h: 150
try:
    AF_LOCAL = PF_LOCAL
except:
    pass

# /usr/include/sys/socket.h: 151
try:
    AF_UNIX = AF_LOCAL
except:
    pass

# /usr/include/sys/socket.h: 152
try:
    AF_FILE = AF_LOCAL
except:
    pass

# /usr/include/sys/socket.h: 153
try:
    AF_INET = PF_INET
except:
    pass

# /usr/include/sys/socket.h: 154
try:
    AF_AX25 = PF_AX25
except:
    pass

# /usr/include/sys/socket.h: 155
try:
    AF_IPX = PF_IPX
except:
    pass

# /usr/include/sys/socket.h: 156
try:
    AF_APPLETALK = PF_APPLETALK
except:
    pass

# /usr/include/sys/socket.h: 157
try:
    AF_NETROM = PF_NETROM
except:
    pass

# /usr/include/sys/socket.h: 158
try:
    AF_BRIDGE = PF_BRIDGE
except:
    pass

# /usr/include/sys/socket.h: 159
try:
    AF_ATMPVC = PF_ATMPVC
except:
    pass

# /usr/include/sys/socket.h: 160
try:
    AF_X25 = PF_X25
except:
    pass

# /usr/include/sys/socket.h: 161
try:
    AF_INET6 = PF_INET6
except:
    pass

# /usr/include/sys/socket.h: 162
try:
    AF_ROSE = PF_ROSE
except:
    pass

# /usr/include/sys/socket.h: 163
try:
    AF_DECnet = PF_DECnet
except:
    pass

# /usr/include/sys/socket.h: 164
try:
    AF_NETBEUI = PF_NETBEUI
except:
    pass

# /usr/include/sys/socket.h: 165
try:
    AF_SECURITY = PF_SECURITY
except:
    pass

# /usr/include/sys/socket.h: 166
try:
    AF_KEY = PF_KEY
except:
    pass

# /usr/include/sys/socket.h: 167
try:
    AF_NETLINK = PF_NETLINK
except:
    pass

# /usr/include/sys/socket.h: 168
try:
    AF_ROUTE = PF_ROUTE
except:
    pass

# /usr/include/sys/socket.h: 169
try:
    AF_PACKET = PF_PACKET
except:
    pass

# /usr/include/sys/socket.h: 170
try:
    AF_ASH = PF_ASH
except:
    pass

# /usr/include/sys/socket.h: 171
try:
    AF_ECONET = PF_ECONET
except:
    pass

# /usr/include/sys/socket.h: 172
try:
    AF_ATMSVC = PF_ATMSVC
except:
    pass

# /usr/include/sys/socket.h: 173
try:
    AF_RDS = PF_RDS
except:
    pass

# /usr/include/sys/socket.h: 174
try:
    AF_SNA = PF_SNA
except:
    pass

# /usr/include/sys/socket.h: 175
try:
    AF_IRDA = PF_IRDA
except:
    pass

# /usr/include/sys/socket.h: 176
try:
    AF_PPPOX = PF_PPPOX
except:
    pass

# /usr/include/sys/socket.h: 177
try:
    AF_WANPIPE = PF_WANPIPE
except:
    pass

# /usr/include/sys/socket.h: 178
try:
    AF_LLC = PF_LLC
except:
    pass

# /usr/include/sys/socket.h: 179
try:
    AF_IB = PF_IB
except:
    pass

# /usr/include/sys/socket.h: 180
try:
    AF_MPLS = PF_MPLS
except:
    pass

# /usr/include/sys/socket.h: 181
try:
    AF_CAN = PF_CAN
except:
    pass

# /usr/include/sys/socket.h: 182
try:
    AF_TIPC = PF_TIPC
except:
    pass

# /usr/include/sys/socket.h: 183
try:
    AF_BLUETOOTH = PF_BLUETOOTH
except:
    pass

# /usr/include/sys/socket.h: 184
try:
    AF_IUCV = PF_IUCV
except:
    pass

# /usr/include/sys/socket.h: 185
try:
    AF_RXRPC = PF_RXRPC
except:
    pass

# /usr/include/sys/socket.h: 186
try:
    AF_ISDN = PF_ISDN
except:
    pass

# /usr/include/sys/socket.h: 187
try:
    AF_PHONET = PF_PHONET
except:
    pass

# /usr/include/sys/socket.h: 188
try:
    AF_IEEE802154 = PF_IEEE802154
except:
    pass

# /usr/include/sys/socket.h: 189
try:
    AF_CAIF = PF_CAIF
except:
    pass

# /usr/include/sys/socket.h: 190
try:
    AF_ALG = PF_ALG
except:
    pass

# /usr/include/sys/socket.h: 191
try:
    AF_NFC = PF_NFC
except:
    pass

# /usr/include/sys/socket.h: 192
try:
    AF_VSOCK = PF_VSOCK
except:
    pass

# /usr/include/sys/socket.h: 193
try:
    AF_KCM = PF_KCM
except:
    pass

# /usr/include/sys/socket.h: 194
try:
    AF_QIPCRTR = PF_QIPCRTR
except:
    pass

# /usr/include/sys/socket.h: 195
try:
    AF_SMC = PF_SMC
except:
    pass

# /usr/include/sys/socket.h: 196
try:
    AF_XDP = PF_XDP
except:
    pass

# /usr/include/sys/socket.h: 197
try:
    AF_MAX = PF_MAX
except:
    pass

# /usr/include/sys/socket.h: 200
try:
    SO_DEBUG = 1
except:
    pass

# /usr/include/sys/socket.h: 201
try:
    SO_REUSEADDR = 2
except:
    pass

# /usr/include/sys/socket.h: 202
try:
    SO_TYPE = 3
except:
    pass

# /usr/include/sys/socket.h: 203
try:
    SO_ERROR = 4
except:
    pass

# /usr/include/sys/socket.h: 204
try:
    SO_DONTROUTE = 5
except:
    pass

# /usr/include/sys/socket.h: 205
try:
    SO_BROADCAST = 6
except:
    pass

# /usr/include/sys/socket.h: 206
try:
    SO_SNDBUF = 7
except:
    pass

# /usr/include/sys/socket.h: 207
try:
    SO_RCVBUF = 8
except:
    pass

# /usr/include/sys/socket.h: 208
try:
    SO_KEEPALIVE = 9
except:
    pass

# /usr/include/sys/socket.h: 209
try:
    SO_OOBINLINE = 10
except:
    pass

# /usr/include/sys/socket.h: 210
try:
    SO_NO_CHECK = 11
except:
    pass

# /usr/include/sys/socket.h: 211
try:
    SO_PRIORITY = 12
except:
    pass

# /usr/include/sys/socket.h: 212
try:
    SO_LINGER = 13
except:
    pass

# /usr/include/sys/socket.h: 213
try:
    SO_BSDCOMPAT = 14
except:
    pass

# /usr/include/sys/socket.h: 214
try:
    SO_REUSEPORT = 15
except:
    pass

# /usr/include/sys/socket.h: 215
try:
    SO_PASSCRED = 16
except:
    pass

# /usr/include/sys/socket.h: 216
try:
    SO_PEERCRED = 17
except:
    pass

# /usr/include/sys/socket.h: 217
try:
    SO_RCVLOWAT = 18
except:
    pass

# /usr/include/sys/socket.h: 218
try:
    SO_SNDLOWAT = 19
except:
    pass

# /usr/include/sys/socket.h: 219
try:
    SO_ACCEPTCONN = 30
except:
    pass

# /usr/include/sys/socket.h: 220
try:
    SO_PEERSEC = 31
except:
    pass

# /usr/include/sys/socket.h: 221
try:
    SO_SNDBUFFORCE = 32
except:
    pass

# /usr/include/sys/socket.h: 222
try:
    SO_RCVBUFFORCE = 33
except:
    pass

# /usr/include/sys/socket.h: 223
try:
    SO_PROTOCOL = 38
except:
    pass

# /usr/include/sys/socket.h: 224
try:
    SO_DOMAIN = 39
except:
    pass

# /usr/include/sys/socket.h: 232
try:
    SO_RCVTIMEO = 20
except:
    pass

# /usr/include/sys/socket.h: 233
try:
    SO_SNDTIMEO = 21
except:
    pass

# /usr/include/sys/socket.h: 243
try:
    SO_TIMESTAMP = 29
except:
    pass

# /usr/include/sys/socket.h: 244
try:
    SO_TIMESTAMPNS = 35
except:
    pass

# /usr/include/sys/socket.h: 245
try:
    SO_TIMESTAMPING = 37
except:
    pass

# /usr/include/sys/socket.h: 249
try:
    SO_SECURITY_AUTHENTICATION = 22
except:
    pass

# /usr/include/sys/socket.h: 250
try:
    SO_SECURITY_ENCRYPTION_TRANSPORT = 23
except:
    pass

# /usr/include/sys/socket.h: 251
try:
    SO_SECURITY_ENCRYPTION_NETWORK = 24
except:
    pass

# /usr/include/sys/socket.h: 253
try:
    SO_BINDTODEVICE = 25
except:
    pass

# /usr/include/sys/socket.h: 255
try:
    SO_ATTACH_FILTER = 26
except:
    pass

# /usr/include/sys/socket.h: 256
try:
    SO_DETACH_FILTER = 27
except:
    pass

# /usr/include/sys/socket.h: 257
try:
    SO_GET_FILTER = SO_ATTACH_FILTER
except:
    pass

# /usr/include/sys/socket.h: 259
try:
    SO_PEERNAME = 28
except:
    pass

# /usr/include/sys/socket.h: 260
try:
    SCM_TIMESTAMP = SO_TIMESTAMP
except:
    pass

# /usr/include/sys/socket.h: 261
try:
    SO_PASSSEC = 34
except:
    pass

# /usr/include/sys/socket.h: 262
try:
    SCM_TIMESTAMPNS = SO_TIMESTAMPNS
except:
    pass

# /usr/include/sys/socket.h: 263
try:
    SO_MARK = 36
except:
    pass

# /usr/include/sys/socket.h: 264
try:
    SCM_TIMESTAMPING = SO_TIMESTAMPING
except:
    pass

# /usr/include/sys/socket.h: 265
try:
    SO_RXQ_OVFL = 40
except:
    pass

# /usr/include/sys/socket.h: 266
try:
    SO_WIFI_STATUS = 41
except:
    pass

# /usr/include/sys/socket.h: 267
try:
    SCM_WIFI_STATUS = SO_WIFI_STATUS
except:
    pass

# /usr/include/sys/socket.h: 268
try:
    SO_PEEK_OFF = 42
except:
    pass

# /usr/include/sys/socket.h: 269
try:
    SO_NOFCS = 43
except:
    pass

# /usr/include/sys/socket.h: 270
try:
    SO_LOCK_FILTER = 44
except:
    pass

# /usr/include/sys/socket.h: 271
try:
    SO_SELECT_ERR_QUEUE = 45
except:
    pass

# /usr/include/sys/socket.h: 272
try:
    SO_BUSY_POLL = 46
except:
    pass

# /usr/include/sys/socket.h: 273
try:
    SO_MAX_PACING_RATE = 47
except:
    pass

# /usr/include/sys/socket.h: 274
try:
    SO_BPF_EXTENSIONS = 48
except:
    pass

# /usr/include/sys/socket.h: 275
try:
    SO_INCOMING_CPU = 49
except:
    pass

# /usr/include/sys/socket.h: 276
try:
    SO_ATTACH_BPF = 50
except:
    pass

# /usr/include/sys/socket.h: 277
try:
    SO_DETACH_BPF = SO_DETACH_FILTER
except:
    pass

# /usr/include/sys/socket.h: 278
try:
    SO_ATTACH_REUSEPORT_CBPF = 51
except:
    pass

# /usr/include/sys/socket.h: 279
try:
    SO_ATTACH_REUSEPORT_EBPF = 52
except:
    pass

# /usr/include/sys/socket.h: 280
try:
    SO_CNX_ADVICE = 53
except:
    pass

# /usr/include/sys/socket.h: 281
try:
    SCM_TIMESTAMPING_OPT_STATS = 54
except:
    pass

# /usr/include/sys/socket.h: 282
try:
    SO_MEMINFO = 55
except:
    pass

# /usr/include/sys/socket.h: 283
try:
    SO_INCOMING_NAPI_ID = 56
except:
    pass

# /usr/include/sys/socket.h: 284
try:
    SO_COOKIE = 57
except:
    pass

# /usr/include/sys/socket.h: 285
try:
    SCM_TIMESTAMPING_PKTINFO = 58
except:
    pass

# /usr/include/sys/socket.h: 286
try:
    SO_PEERGROUPS = 59
except:
    pass

# /usr/include/sys/socket.h: 287
try:
    SO_ZEROCOPY = 60
except:
    pass

# /usr/include/sys/socket.h: 288
try:
    SO_TXTIME = 61
except:
    pass

# /usr/include/sys/socket.h: 289
try:
    SCM_TXTIME = SO_TXTIME
except:
    pass

# /usr/include/sys/socket.h: 290
try:
    SO_BINDTOIFINDEX = 62
except:
    pass

# /usr/include/sys/socket.h: 291
try:
    SO_DETACH_REUSEPORT_BPF = 68
except:
    pass

# /usr/include/sys/socket.h: 292
try:
    SO_PREFER_BUSY_POLL = 69
except:
    pass

# /usr/include/sys/socket.h: 293
try:
    SO_BUSY_POLL_BUDGET = 70
except:
    pass

# /usr/include/sys/socket.h: 296
try:
    SOL_SOCKET = 1
except:
    pass

# /usr/include/sys/socket.h: 299
try:
    SOL_IP = 0
except:
    pass

# /usr/include/sys/socket.h: 300
try:
    SOL_IPV6 = 41
except:
    pass

# /usr/include/sys/socket.h: 301
try:
    SOL_ICMPV6 = 58
except:
    pass

# /usr/include/sys/socket.h: 303
try:
    SOL_RAW = 255
except:
    pass

# /usr/include/sys/socket.h: 304
try:
    SOL_DECNET = 261
except:
    pass

# /usr/include/sys/socket.h: 305
try:
    SOL_X25 = 262
except:
    pass

# /usr/include/sys/socket.h: 306
try:
    SOL_PACKET = 263
except:
    pass

# /usr/include/sys/socket.h: 307
try:
    SOL_ATM = 264
except:
    pass

# /usr/include/sys/socket.h: 308
try:
    SOL_AAL = 265
except:
    pass

# /usr/include/sys/socket.h: 309
try:
    SOL_IRDA = 266
except:
    pass

# /usr/include/sys/socket.h: 310
try:
    SOL_NETBEUI = 267
except:
    pass

# /usr/include/sys/socket.h: 311
try:
    SOL_LLC = 268
except:
    pass

# /usr/include/sys/socket.h: 312
try:
    SOL_DCCP = 269
except:
    pass

# /usr/include/sys/socket.h: 313
try:
    SOL_NETLINK = 270
except:
    pass

# /usr/include/sys/socket.h: 314
try:
    SOL_TIPC = 271
except:
    pass

# /usr/include/sys/socket.h: 315
try:
    SOL_RXRPC = 272
except:
    pass

# /usr/include/sys/socket.h: 316
try:
    SOL_PPPOL2TP = 273
except:
    pass

# /usr/include/sys/socket.h: 317
try:
    SOL_BLUETOOTH = 274
except:
    pass

# /usr/include/sys/socket.h: 318
try:
    SOL_PNPIPE = 275
except:
    pass

# /usr/include/sys/socket.h: 319
try:
    SOL_RDS = 276
except:
    pass

# /usr/include/sys/socket.h: 320
try:
    SOL_IUCV = 277
except:
    pass

# /usr/include/sys/socket.h: 321
try:
    SOL_CAIF = 278
except:
    pass

# /usr/include/sys/socket.h: 322
try:
    SOL_ALG = 279
except:
    pass

# /usr/include/sys/socket.h: 323
try:
    SOL_NFC = 280
except:
    pass

# /usr/include/sys/socket.h: 324
try:
    SOL_KCM = 281
except:
    pass

# /usr/include/sys/socket.h: 325
try:
    SOL_TLS = 282
except:
    pass

# /usr/include/sys/socket.h: 326
try:
    SOL_XDP = 283
except:
    pass

# /usr/include/sys/socket.h: 328
try:
    SOMAXCONN = 128
except:
    pass

# /usr/include/sys/socket.h: 330
try:
    MSG_OOB = 0x0001
except:
    pass

# /usr/include/sys/socket.h: 331
try:
    MSG_PEEK = 0x0002
except:
    pass

# /usr/include/sys/socket.h: 332
try:
    MSG_DONTROUTE = 0x0004
except:
    pass

# /usr/include/sys/socket.h: 333
try:
    MSG_CTRUNC = 0x0008
except:
    pass

# /usr/include/sys/socket.h: 334
try:
    MSG_PROXY = 0x0010
except:
    pass

# /usr/include/sys/socket.h: 335
try:
    MSG_TRUNC = 0x0020
except:
    pass

# /usr/include/sys/socket.h: 336
try:
    MSG_DONTWAIT = 0x0040
except:
    pass

# /usr/include/sys/socket.h: 337
try:
    MSG_EOR = 0x0080
except:
    pass

# /usr/include/sys/socket.h: 338
try:
    MSG_WAITALL = 0x0100
except:
    pass

# /usr/include/sys/socket.h: 339
try:
    MSG_FIN = 0x0200
except:
    pass

# /usr/include/sys/socket.h: 340
try:
    MSG_SYN = 0x0400
except:
    pass

# /usr/include/sys/socket.h: 341
try:
    MSG_CONFIRM = 0x0800
except:
    pass

# /usr/include/sys/socket.h: 342
try:
    MSG_RST = 0x1000
except:
    pass

# /usr/include/sys/socket.h: 343
try:
    MSG_ERRQUEUE = 0x2000
except:
    pass

# /usr/include/sys/socket.h: 344
try:
    MSG_NOSIGNAL = 0x4000
except:
    pass

# /usr/include/sys/socket.h: 345
try:
    MSG_MORE = 0x8000
except:
    pass

# /usr/include/sys/socket.h: 346
try:
    MSG_WAITFORONE = 0x10000
except:
    pass

# /usr/include/sys/socket.h: 347
try:
    MSG_BATCH = 0x40000
except:
    pass

# /usr/include/sys/socket.h: 348
try:
    MSG_ZEROCOPY = 0x4000000
except:
    pass

# /usr/include/sys/socket.h: 349
try:
    MSG_FASTOPEN = 0x20000000
except:
    pass

# /usr/include/sys/socket.h: 350
try:
    MSG_CMSG_CLOEXEC = 0x40000000
except:
    pass

# /usr/include/sys/socket.h: 352
def __CMSG_LEN(cmsg):
    return (((((cmsg.contents.cmsg_len).value) + sizeof(c_long)) - 1) & (~(c_long (ord_if_char((sizeof(c_long) - 1)))).value))

# /usr/include/sys/socket.h: 353
def __CMSG_NEXT(cmsg):
    return (cast(cmsg, POINTER(c_ubyte)) + (__CMSG_LEN (cmsg)))

# /usr/include/sys/socket.h: 354
def __MHDR_END(mhdr):
    return (cast((mhdr.contents.msg_control), POINTER(c_ubyte)) + ((mhdr.contents.msg_controllen).value))

# /usr/include/sys/socket.h: 356
def CMSG_DATA(cmsg):
    return cast((cast(cmsg, POINTER(struct_cmsghdr)) + 1), POINTER(c_ubyte))

# /usr/include/sys/socket.h: 357
def CMSG_NXTHDR(mhdr, cmsg):
    return ((((cmsg.contents.cmsg_len).value) < sizeof(struct_cmsghdr)) or (((__CMSG_LEN (cmsg)) + sizeof(struct_cmsghdr)) >= ((__MHDR_END (mhdr)) - cast(cmsg, POINTER(c_ubyte))))) and 0 or cast((__CMSG_NEXT (cmsg)), POINTER(struct_cmsghdr))

# /usr/include/sys/socket.h: 360
def CMSG_FIRSTHDR(mhdr):
    return ((c_size_t (ord_if_char(((mhdr.contents.msg_controllen).value)))).value >= sizeof(struct_cmsghdr)) and cast((mhdr.contents.msg_control), POINTER(struct_cmsghdr)) or cast(0, POINTER(struct_cmsghdr))

# /usr/include/sys/socket.h: 362
def CMSG_ALIGN(len):
    return (((len + sizeof(c_size_t)) - 1) & (c_size_t (ord_if_char((~(sizeof(c_size_t) - 1))))).value)

# /usr/include/sys/socket.h: 363
def CMSG_SPACE(len):
    return ((CMSG_ALIGN (len)) + (CMSG_ALIGN (sizeof(struct_cmsghdr))))

# /usr/include/sys/socket.h: 364
def CMSG_LEN(len):
    return ((CMSG_ALIGN (sizeof(struct_cmsghdr))) + len)

# /usr/include/sys/socket.h: 366
try:
    SCM_RIGHTS = 0x01
except:
    pass

# /usr/include/sys/socket.h: 367
try:
    SCM_CREDENTIALS = 0x02
except:
    pass

guac_client = struct_guac_client# /tmp/guacamole-server/src/libguac/guacamole/client.h: 59

guac_socket = struct_guac_socket# /tmp/guacamole-server/src/libguac/guacamole/socket.h: 39

guac_user = struct_guac_user# /tmp/guacamole-server/src/libguac/guacamole/user.h: 115

guac_user_info = struct_guac_user_info# /tmp/guacamole-server/src/libguac/guacamole/user.h: 46

guac_client_internal = struct_guac_client_internal# /tmp/guacamole-server/src/libguac/client-internal.h: 44

__guac_instruction_handler_mapping = struct___guac_instruction_handler_mapping# /tmp/guacamole-server/src/libguac/user-handlers.h: 72

guac_parser = struct_guac_parser# /tmp/guacamole-server/src/libguac/guacamole/parser.h: 34

msghdr = struct_msghdr# /usr/include/sys/socket.h: 22

cmsghdr = struct_cmsghdr# /usr/include/sys/socket.h: 44

linger = struct_linger# /usr/include/sys/socket.h: 74

sockaddr = struct_sockaddr# /usr/include/sys/socket.h: 369

sockaddr_storage = struct_sockaddr_storage# /usr/include/sys/socket.h: 374

# No inserted files

# No prefix-stripping

