from ctypes import *
from functools import wraps
from typing import Callable

# Event constants
IN_MODIFY       = 0x00000002
IN_MOVED_FROM   = 0x00000040
IN_MOVED_TO     = 0x00000080
IN_CREATE       = 0x00000080
IN_DELETE       = 0x00000200

# Convenience constants
IN_MOVE  = IN_MOVED_FROM | IN_MOVED_TO
IN_EVENT = IN_MODIFY | IN_MOVE | IN_DELETE | IN_CREATE

# struct inotify_event
class inotify_event(Structure):
    _fields_ = [
        ('wd', c_int32),
        ('mask', c_uint32),
        ('cookie', c_uint32),
        ('len', c_uint32),
        ('name', c_char_p)
    ]

EVENT_SIZE = sizeof(inotify_event)
BUF_LEN    = 1024 + EVENT_SIZE + 16

libc = cdll.LoadLibrary('libc.so.6')

def safe_call(fn):
    @wraps(fn)
    def f(*args, **kwargs):
        res = fn(*args, **kwargs)
        if res < 0:
            raise Exception(fn.__name__ + ' failed')
        return res
    return f

get_fd: Callable[[], int] = safe_call(libc.inotify_init)
add_watch: Callable[[int, bytes], None] = lambda fd, _path: safe_call(libc.inotify_add_watch)(fd, c_char_p(_path), IN_EVENT)

def handle_events(fd: int):
    buf = pointer((c_char * BUF_LEN)())
    count = safe_call(libc.read)(fd, buf, BUF_LEN)
    i = 0
    while i < count:
        event = cast(pointer(buf[i]), POINTER(inotify_event)).contents
        if event.mask & IN_CREATE:
            print('Create')
        if event.mask & IN_MODIFY:
            print('Modify')
        if event.mask & IN_DELETE:
            print('Delete')
        i += EVENT_SIZE + event.len

fd = get_fd()
add_watch(fd, b"testdirec")
while True:
    handle_events(fd)
