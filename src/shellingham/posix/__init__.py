import os

from .._consts import SHELL_NAMES


def _get_process_mapping():
    """Select a way to obtain process information from the system.

    * `/proc` is used if supported.
    * The system `ps` utility is used as a fallback option.
    """
    if os.path.isdir('/proc') and os.listdir('/proc'):
        # Need to check if /proc contains stuff. It might not be mounted.
        from . import _proc as impl
    else:
        from . import _ps as impl
    return impl.get_process_mapping()


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
        name = os.path.basename(proc.args[0]).lower()
        if name in SHELL_NAMES:
            return (name, proc.args[0])
        elif proc.args[0].startswith('-'):
            # This is the login shell. Use the SHELL environ if possible
            # because it provides better information.
            if login_shell:
                name = login_shell.lower()
            else:
                name = proc.args[0][1:].lower()
            return (os.path.basename(name), name)
        pid = proc.ppid     # Go up one level.
    return None
