"""
Get name and full path of most recent ancestor process that is a shell.
Credits: https://stackoverflow.com/a/65955496/33264
"""
import contextlib
import ctypes
import ctypes.wintypes

k32 = ctypes.windll.kernel32

INVALID_HANDLE_VALUE = ctypes.wintypes.HANDLE(-1).value
ERROR_NO_MORE_FILES = 18
ERROR_INSUFFICIENT_BUFFER = 122
TH32CS_SNAPPROCESS = 2
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def _check_handle(error_val=0):
    def check(ret, func, args):
        if ret == error_val:
            raise ctypes.WinError()
        return ret

    return check


def _check_expected(expected):
    def check(ret, func, args):
        if ret:
            return True
        code = ctypes.GetLastError()
        if code == expected:
            return False
        raise ctypes.WinError(code)

    return check


# ref: https://stackoverflow.com/questions/32807560/how-do-i-get-in-python-the-maximum-filesystem-path-length-in-unix

class ProcessEntry32(ctypes.Structure):
    _fields_ = (
        ('dwSize', ctypes.wintypes.DWORD),
        ('cntUsage', ctypes.wintypes.DWORD),
        ('th32ProcessID', ctypes.wintypes.DWORD),
        ('th32DefaultHeapID', ctypes.POINTER(ctypes.wintypes.ULONG)),
        ('th32ModuleID', ctypes.wintypes.DWORD),
        ('cntThreads', ctypes.wintypes.DWORD),
        ('th32ParentProcessID', ctypes.wintypes.DWORD),
        ('pcPriClassBase', ctypes.wintypes.LONG),
        ('dwFlags', ctypes.wintypes.DWORD),
        ('szExeFile', ctypes.wintypes.CHAR * ctypes.wintypes.MAX_PATH),
    )


k32.CloseHandle.argtypes = \
    (ctypes.wintypes.HANDLE,)
k32.CloseHandle.restype = ctypes.wintypes.BOOL

k32.CreateToolhelp32Snapshot.argtypes = \
    (ctypes.wintypes.DWORD, ctypes.wintypes.DWORD)
k32.CreateToolhelp32Snapshot.restype = ctypes.wintypes.HANDLE
k32.CreateToolhelp32Snapshot.errcheck = _check_handle(INVALID_HANDLE_VALUE)

k32.Process32First.argtypes = \
    (ctypes.wintypes.HANDLE, ctypes.POINTER(ProcessEntry32))
k32.Process32First.restype = ctypes.wintypes.BOOL
k32.Process32First.errcheck = _check_expected(ERROR_NO_MORE_FILES)

k32.Process32Next.argtypes = \
    (ctypes.wintypes.HANDLE, ctypes.POINTER(ProcessEntry32))
k32.Process32Next.restype = ctypes.wintypes.BOOL
k32.Process32Next.errcheck = _check_expected(ERROR_NO_MORE_FILES)

k32.GetCurrentProcessId.argtypes = ()
k32.GetCurrentProcessId.restype = ctypes.wintypes.DWORD

k32.OpenProcess.argtypes = \
    (ctypes.wintypes.DWORD, ctypes.wintypes.BOOL, ctypes.wintypes.DWORD)
k32.OpenProcess.restype = ctypes.wintypes.HANDLE
k32.OpenProcess.errcheck = _check_handle(INVALID_HANDLE_VALUE)

k32.QueryFullProcessImageNameW.argtypes = \
    (ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD, ctypes.wintypes.LPWSTR,
     ctypes.wintypes.PDWORD)
k32.QueryFullProcessImageNameW.restype = ctypes.wintypes.BOOL
k32.QueryFullProcessImageNameW.errcheck = _check_expected(ERROR_INSUFFICIENT_BUFFER)


@contextlib.contextmanager
def Win32Handle(handle):
    try:
        yield handle
    finally:
        k32.CloseHandle(handle)


def enum_processes():
    with Win32Handle(k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)) as snap:
        entry = ProcessEntry32()
        entry.dwSize = ctypes.sizeof(entry)
        ret = k32.Process32First(snap, entry)
        while ret:
            yield entry
            ret = k32.Process32Next(snap, entry)


def get_full_path(proch):
    size = ctypes.wintypes.DWORD(ctypes.wintypes.MAX_PATH)
    while True:
        path_buff = ctypes.create_unicode_buffer('', size.value)
        if k32.QueryFullProcessImageNameW(proch, 0, path_buff, size):
            return path_buff.value
        size.value *= 2


SHELLS = frozenset((
    b'sh.exe', b'bash.exe', b'dash.exe', b'ash.exe',
    b'csh.exe', b'tcsh.exe',
    b'ksh.exe', b'zsh.exe', b'fish.exe',
    b'cmd.exe', b'powershell.exe', b'pwsh.exe',
    b'elvish.exe', b'xonsh.exe',
))


def get_shell(pid=None, max_depth=6):
    proc_map = {
        proc.th32ProcessID: (proc.th32ParentProcessID, proc.szExeFile)
        for proc in enum_processes()
    }
    if not pid:
        pid = proc_map[k32.GetCurrentProcessId()][0]
    proc = proc_map[pid]
    depth = 0
    while proc:
        depth += 1

        ppid, name = proc

        if name in SHELLS:
            with Win32Handle(k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, 0,
                                             pid)) as proch:
                return (name.decode(), get_full_path(proch))
        pid, proc = ppid, proc_map.get(ppid)
        if depth > max_depth:
            return None
