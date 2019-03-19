import pytest

from shellingham.posix._core import Process
from shellingham.posix.ps import _parse_ps_header, _parse_ps_output


def test_parse_ps_header():
    header = '   UID   PID  PPID CPU PRI NI      VSZ    TIME COMMAND'
    parsed = dict(_parse_ps_header(header))
    assert parsed == {
        'UID': slice(0, 6),
        'PID': slice(6, 12),
        'PPID': slice(12, 18),
        'CPU': slice(18, 22),
        'PRI': slice(22, 26),
        'NI': slice(26, 29),
        'VSZ': slice(29, 38),
        'TIME': slice(38, 46),
        'COMMAND': slice(46, None),
    }


PS_OUTPUTS = [
    """\
 UID   PID  PPID CPU PRI NI      VSZ    RSS WCHAN  STAT   TT       TIME COMMAND
 501 90585 90584   0  31  0  4296844   2896 -      S    s000    0:00.19 -bash
 501 96095 90585   0  31  0  4258724    180 -      S+   s000    0:00.01 pbcopy
 501 82490 82489   0  31  0  4296844    496 -      S+   s001    0:00.11 -bash
 501 82557 82556   0  31  0  4296844   1260 -      S+   s002    0:00.43 -bash
    """,    # noqa
    """\
     F S      UID    PID   PPID   C PRI NI ADDR  SZ  RSS   WCHAN    TTY   TIME CMD
240000 A      105 897903 897902   0  20 20    0 7124    0          pts/0  0:00 -bash
200000 A      105 897904 897903   0  20 20    0 6792    0          pts/0  0:00 ps wwl
    """,    # noqa
]

PS_EXPECTED = [
    {
        '90585': Process(pid='90585', ppid='90584', args=('-bash',)),
        '96095': Process(pid='96095', ppid='90585', args=('pbcopy',)),
        '82490': Process(pid='82490', ppid='82489', args=('-bash',)),
        '82557': Process(pid='82557', ppid='82556', args=('-bash',)),
    },
    {
        '897903': Process(pid='897903', ppid='897902', args=('-bash',)),
        '897904': Process(pid='897904', ppid='897903', args=('ps', 'wwl')),
    },
]


@pytest.mark.parametrize(
    'output, expected',
    zip(PS_OUTPUTS, PS_EXPECTED),
    ids=['BSD', 'IBM'],
)
def test_parse_ps_output(output, expected):
    parsed = dict(_parse_ps_output(output))
    assert parsed == expected
