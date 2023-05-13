import errno
import subprocess
import sys

from ._core import Process


class PsNotAvailable(EnvironmentError):
    pass

def _get_stats(pid):
    try:
        cmd = ["ps", "wwl", "-P", pid]
        output = subprocess.check_output(cmd)
    except OSError as e:  # Python 2-compatible FileNotFoundError.
        if e.errno != errno.ENOENT:
            raise
        raise PsNotAvailable("ps not found")
    except subprocess.CalledProcessError as e:
        # `ps` can return 1 if the process list is completely empty.
        # (sarugaku/shellingham#15)
        if not e.output.strip():
            return {}
        raise
    if not isinstance(output, str):
        encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
        output = output.decode(encoding)

    print(output)

    header, row = output.split("\n")[:2]
    header = header.split()
    row = row.split()

    pid_index = header.index("PID")
    ppid_index = header.index("PPID")

    try:
        cmd_index = header.index("COMMAND")
    except ValueError:
        # https://github.com/sarugaku/shellingham/pull/23#issuecomment-474005491
        cmd_index = header.index("CMD")


    return row[cmd_index:], row[pid_index], row[ppid_index]




def get_process_parents(pid, max_depth=10):
    """Try to look up the process tree via the output of `ps`."""
    processes = []

    depth = 0
    while pid != "0" and depth < max_depth:
        depth += 1
        cmd, pid, ppid = _get_stats(pid)
        processes.append(Process(args=cmd, pid=pid, ppid=ppid))

        pid = ppid

    return processes
