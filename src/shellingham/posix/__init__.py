import os
import platform

from .._consts import SHELL_NAMES


def _get_process_mapping():
    system = platform.system()
    if system == 'Linux':
        from . import linux as impl
    else:
        from . import _default as impl
    return impl.get_process_mapping()


def _get_shell_name(path):
    """Parse shell name from given path to executable.

    PATHEXT is used to try to strip executable extension from the basename.
    This could be useful on fake POSIX environments such as Cygwin and Msys.
    """
    base = os.path.basename(path).lower()
    try:
        exts = os.environ['PATHEXT'].lower().split(';')
    except KeyError:
        return base
    for ext in exts:
        if not ext:
            continue
        if base.endswith(ext):
            return base[:-len(ext)]
    return base


def get_shell(pid=None, max_depth=6):
    """Get the shell that the supplied pid or os.getpid() is running in.
    """
    pid = str(pid or os.getpid())
    mapping = _get_process_mapping()
    login_shell = os.environ.get('SHELL', '')
    for _ in range(max_depth):
        try:
            proc = mapping[pid]
        except KeyError:
            break
        name = _get_shell_name(proc.args[0])
        if name in SHELL_NAMES:
            return (name, proc.args[0])
        elif proc.args[0].startswith('-'):
            # This is the login shell. Use the SHELL environ if possible
            # because it provides better information.
            if login_shell:
                path = login_shell.lower()
            else:
                path = proc.args[0][1:].lower()
            return (_get_shell_name(path), name)
        pid = proc.ppid     # Go up one level.
    return None
