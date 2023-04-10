"""Simple file-system watcher.

Public API:
    make_event_handler(*, on_create, on_modify, etc.) -> Callable
    surveil(directoryname: str, event_handler: Callable)

Usage:
    event_handler = make_event_handler(
        on_create=lambda: print('file created')
        on_delete=lambda: print('file deleted')
    )
    surveil("testdirec", event_handler)

The best way to learn about anything (even life) is to read the source, 
so be sure to do that!
"""

__version__ = '1.0.0'

from ctypes import *
from functools import wraps
from itertools import compress, repeat
from operator import and_

# Utility

call = lambda f: f()

def safe_call(fn):
    @wraps(fn)
    def f(*args, **kwargs):
        res = fn(*args, **kwargs)
        if res < 0:
            raise Exception(fn.__name__ + ' failed')
        return res
    return f

# Event constants
IN_MODIFY       = 0x00000002
IN_MOVED_FROM   = 0x00000040
IN_MOVED_TO     = 0x00000080
IN_CREATE       = 0x00000100
IN_DELETE       = 0x00000200

# Convenience constants
IN_MOVE  = IN_MOVED_FROM | IN_MOVED_TO
IN_EVENT = IN_MODIFY | IN_MOVE | IN_DELETE | IN_CREATE

IN_CONSTANTS = {x: y for x, y in globals().items() if x.startswith('IN_')}
_constants = {'on_' + x[3:].lower(): y for x, y in IN_CONSTANTS.items()}

# struct inotify_event
class inotify_event(Structure):
    _fields_ = [
        ('wd', c_int32),
        ('mask', c_uint32),
        ('cookie', c_uint32),
        ('len', c_uint32),
        ('name', c_char_p)
    ]

BUF_LEN = 1024 + sizeof(inotify_event) + 16

libc = cdll.LoadLibrary('libc.so.6')

get_fd = safe_call(libc.inotify_init)
add_watch = lambda fd, _path: safe_call(libc.inotify_add_watch)(fd, c_char_p(_path), IN_EVENT)
make_event_handler =\
    lambda **kw: lambda mask: \
        list(map(call, compress(kw.values(), map(and_, map(_constants.get, kw.keys()), repeat(mask)))))

def surveil(directory, fn):
    fd = get_fd()
    add_watch(fd, bytes(directory, 'utf-8'))
    while True:
        buf = pointer((c_char * BUF_LEN)())
        count = safe_call(libc.read)(fd, buf, BUF_LEN)
        fn(cast(pointer(buf[0]), POINTER(inotify_event)).contents.mask)
