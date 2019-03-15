import errno
import inspect
import subprocess
import sys

from ._core import Process


class PsNotAvailable(EnvironmentError):
    pass


try:
    getargspec = inspect.getfullargspec
except AttributeError:  # Old.
    getargspec = inspect.getargspec

if len(getargspec(subprocess.CalledProcessError.__init__).args) >= 4:
    CalledProcessError = subprocess.CalledProcessError
else:   # Old Python versions don't support the stderr argument.
    def CalledProcessError(returncode, cmd, output, stderr):
        error = subprocess.CalledProcessError(returncode, cmd, output)
        error.stderr = stderr
        return error


def _get_ps_output():
    """Call `ps` and returns its output as text.

    Raises `subprocess.CalledProcessError` or `FileNotFoundError` if the `ps`
    call fails. The output is decoded by the most reasonable system encoding
    available.
    """
    cmd = ['ps', 'wwl']
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    except OSError as e:    # Python 2-compatible FileNotFoundError.
        if e.errno != errno.ENOENT:
            raise
        raise PsNotAvailable('ps not found')

    out, err = proc.communicate()

    if isinstance(out, str):
        result = out
    else:
        encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
        result = out.decode(encoding)

    if proc.returncode == 1:
        # `ps` can return 1 if the process list is completely empty.
        # In this case the output would only contain the header row.
        # (sarugaku/shellingham#15, sarugaku/shellingham#22)
        if err.strip() or len(result.split('\n', 1)) != 1:
            raise CalledProcessError(proc.returncode, cmd, out, err)
    elif proc.returncode:
        raise CalledProcessError(proc.returncode, cmd, out, err)

    return result


def _parse_ps_header(header):
    """Parse the header row of the `ps` output and yield column information.

    Each yield sends a 2-tuple `(name, slice)`. `name` is the name of the
    column (generally in ALLCAPS); `slice` is a slice object that can be used
    to slice the given column out of a row (spaces included).
    """
    start = 0
    colchs = []
    for i, c in enumerate(header):
        if c != ' ':
            colchs.append(c)
            continue
        if colchs:
            yield (''.join(colchs), slice(start, i))
            start = i
        colchs = []
    yield (''.join(colchs), slice(start, None))


def _parse_ps_output(output):
    """Parse the `ps` output and yield information from each row.

    The header row is first parsed for column information, and each subsequent
    row parsed to get information we want. Each yields sends a 2-tuple
    `(pid, process)`.
    """
    lines_iter = iter(output.split('\n'))
    try:
        header = next(lines_iter)
    except StopIteration:
        return
    columns = {k.lower(): v for k, v in _parse_ps_header(header)}
    for line in lines_iter:
        pid, ppid, args = (
            line[columns[k]].strip()
            for k in ('pid', 'ppid', 'command')
        )
        # XXX: This is not right, but we are really out of options.
        # ps does not offer a sane way to decode the argument display,
        # and this is "Good Enough" for obtaining shell names. Hopefully
        # people don't name their shell with a space, or have something
        # like "/usr/bin/xonsh is uber". (sarugaku/shellingham#14)
        args = tuple(a.strip() for a in args.split(' '))
        yield pid, Process(args=args, pid=pid, ppid=ppid)


def get_process_mapping():
    """Try to look up the process tree via the output of `ps`.
    """
    output = _get_ps_output()
    return dict(_parse_ps_output(output))
