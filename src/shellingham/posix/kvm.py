import contextlib
import ctypes
import ctypes.util
import os


# Opaque types.
kvm_t_p = ctypes.c_void_p       # kvm_t *
kinfo_proc_p = ctypes.c_void_p  # kinfo_proc *

_POSIX2_LINE_MAX = 2048     # Seems to be a thing.

# System-defined.
KERN_PROC_PID = 1


class KVMNotAvailableError(EnvironmentError):
    pass


def _get_kvm():
    kvm = ctypes.util.find_library('kvm')
    if not kvm:
        raise KVMNotAvailableError('libkvm not found')

    kvm.kvm_openfiles.restype = kvm_t_p
    kvm.kvm_openfiles.argtypes = [
        ctypes.c_char_p,    # execfile
        ctypes.c_char_p,    # corefile
        ctypes.c_char_p,    # swapfile
        ctypes.c_int,       # flags
        ctypes.c_char_p,    # errbuf
    ]

    kvm.kvm_getprocs.restype = kinfo_proc_p
    kvm.kvm_getprocs.argtypes = [
        kvm_t_p,        # kd
        ctypes.c_int,   # op
        ctypes.c_int,   # arg
        ctypes.POINTER(ctypes.c_int),   # cnt
    ]

    kvm.kvm_geterr.restype = ctypes.c_char_p
    kvm.kvm_geterr.argtypes = [
        kvm_t_p,    # kd
    ]

    return kvm


class KernelVirtualMemory(object):
    """Abstraction of the Kernel Virtual Memory interface (libkvm).
    """
    def __init__(self, lib):
        self._c = lib
        self._errbuf = ctypes.create_string_buffer(_POSIX2_LINE_MAX)

    @classmethod
    def find(cls):
        return cls(_get_kvm())

    @property
    def _error(self):
        return self._errbuf.decode('ascii')

    @contextlib.contextmanager
    def open_descriptor(self):
        kd = self._c.kvm_openfiles(
            None, b'/dev/null', None, os.O_RDONLY, self._errbuf,
        )
        if not kd:
            raise KVMNotAvailableError(self._error)
        yield kd
        self._c.kvm_close(kd)

    def iter_processes(self, kd, pid):
        count = ctypes.c_int()
        kp = self._c.kvm_getprocs(kd, KERN_PROC_PID, pid, ctypes.byref(count))
        if not kp:
            raise KVMNotAvailableError('failed to get processes')
        if count < 0:
            raise KVMNotAvailableError(self._c.kvm_geterr(kd))

        for _ in range(count):
            # Stuck. kp is a contagious array of kinfo_proc instances, so in C
            # we just +1 on the pointer to get to the next location. That is
            # not possible in ctypes unless we have the struct definition.
            # Unfortunately the definition is quite complex, and seems to be
            # platform-dependant.
            pass


def get_process_mapping():
    """Try to look up process tree via libkvm, available on BSD deritives.
    """
    kvm = KernelVirtualMemory.find()
    descriptor = kvm.openfiles()
    if not descriptor:
        raise KVMNotAvailableError('failed to open')
