import os

import pytest

from shellingham import posix
from shellingham.posix._core import Process


class EnvironManager(object):

    def __init__(self):
        self.backup = {}
        self.changed = set()

    def patch(self, **kwargs):
        self.backup.update({
            k: os.environ[k] for k in kwargs if k in os.environ
        })
        self.changed.update(kwargs.keys())
        os.environ.update(kwargs)

    def unpatch(self):
        for k in self.changed:
            try:
                v = self.backup[k]
            except KeyError:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


@pytest.fixture()
def environ(request):
    """Provide environment variable override, and restore on finalize.
    """
    manager = EnvironManager()
    request.addfinalizer(manager.unpatch)
    return manager


MAPPING_EXAMPLE_KEEGANCSMITH = {
    '1480': Process(pid='1480', ppid='1477', args=(
        '/Applications/iTerm.app/Contents/MacOS/iTerm2',
        '--server', 'login', '-fp', 'keegan',
    )),
    '1482': Process(pid='1482', ppid='1481', args=(
        '-bash',
    )),
    '1556': Process(pid='1556', ppid='1482', args=(
        'screen',
    )),
    '1558': Process(pid='1558', ppid='1557', args=(
        '-/usr/local/bin/bash',
    )),
    '1706': Process(pid='1706', ppid='1558', args=(
        '/Applications/Emacs.app/Contents/MacOS/Emacs-x86_64-10_10', '-nw',
    )),
    '77061': Process(pid='77061', ppid='1706', args=(
        '/usr/local/bin/aspell', '-a', '-m', '-B', '--encoding=utf-8',
    )),
    '1562': Process(pid='1562', ppid='1557', args=(
        '-/usr/local/bin/bash',
    )),
    '87033': Process(pid='87033', ppid='1557', args=(
        '-/usr/local/bin/bash',
    )),
    '84732': Process(pid='84732', ppid='1557', args=(
        '-/usr/local/bin/bash',
    )),
    '89065': Process(pid='89065', ppid='1557', args=(
        '-/usr/local/bin/bash',
    )),
    '80216': Process(pid='80216', ppid='1557', args=(
        '-/usr/local/bin/bash',
    )),
}


@pytest.mark.parametrize('mapping, result', [
    (   # Based on pypa/pipenv#2496, provided by @keegancsmith.
        MAPPING_EXAMPLE_KEEGANCSMITH, ('bash', '==MOCKED=LOGIN=SHELL==/bash'),
    ),
])
def test_get_shell(mocker, environ, mapping, result):
    environ.patch(SHELL='==MOCKED=LOGIN=SHELL==/bash')
    mocker.patch.object(posix, '_get_process_mapping', return_value=mapping)
    assert posix.get_shell(pid=77061) == result
