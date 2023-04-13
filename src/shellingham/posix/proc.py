import io
import os
import re
import sys

from ._core import Process

# FreeBSD: https://www.freebsd.org/cgi/man.cgi?query=procfs
# NetBSD: https://man.netbsd.org/NetBSD-9.3-STABLE/mount_procfs.8
# DragonFlyBSD: https://www.dragonflybsd.org/cgi/web-man?command=procfs
BSD_STAT_PPID = 2
BSD_STAT_TTY = 5

# See https://docs.kernel.org/filesystems/proc.html
LINUX_STAT_PPID = 3
LINUX_STAT_TTY = 6

STAT_PATTERN = re.compile(r"\(.+\)|\S+")


def detect_proc():
    """Detect /proc filesystem style.

    This checks the /proc/{pid} directory for possible formats. Returns one of
    the following as str:

    * `stat`: Linux-style, i.e. ``/proc/{pid}/stat``.
    * `status`: BSD-style, i.e. ``/proc/{pid}/status``.
    """
    pid = os.getpid()
    for name in ("stat", "status"):
        if os.path.exists(os.path.join("/proc", str(pid), name)):
            return name
    raise ProcFormatError("unsupported proc format")


def _use_bsd_stat_format():
    try:
        return os.uname().sysname.lower() in ('freebsd', 'netbsd', 'dragonfly')
    except Exception:
        return False


def _get_stat(pid, name):
    path = os.path.join("/proc", str(pid), name)
    with io.open(path, encoding="ascii", errors="replace") as f:
        parts = STAT_PATTERN.findall(f.read())
    # We only care about TTY and PPID -- both are numbers.
    if _use_bsd_stat_format():
        return parts[BSD_STAT_TTY], parts[BSD_STAT_PPID]
    return parts[LINUX_STAT_TTY], parts[LINUX_STAT_PPID]


def _get_cmdline(pid):
    path = os.path.join("/proc", str(pid), "cmdline")
    encoding = sys.getfilesystemencoding() or "utf-8"
    with io.open(path, encoding=encoding, errors="replace") as f:
        # XXX: Command line arguments can be arbitrary byte sequences, not
        # necessarily decodable. For Shellingham's purpose, however, we don't
        # care. (pypa/pipenv#2820)
        # cmdline appends an extra NULL at the end, hence the [:-1].
        return tuple(f.read().split("\0")[:-1])


class ProcFormatError(EnvironmentError):
    pass


def get_process_mapping():
    """Try to look up the process tree via the /proc interface."""
    stat_name = detect_proc()
    self_tty = _get_stat(os.getpid(), stat_name)[0]
    processes = {}
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            tty, ppid = _get_stat(pid, stat_name)
            if tty != self_tty:
                continue
            args = _get_cmdline(pid)
            processes[pid] = Process(args=args, pid=pid, ppid=ppid)
        except IOError:
            # Process has disappeared - just ignore it.
            continue
    return processes
