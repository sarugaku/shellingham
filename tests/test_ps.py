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


PS_OUTPUT = (
"""\
  UID   PID  PPID CPU PRI NI      VSZ    RSS WCHAN  STAT   TT       TIME COMMAND
  501 90585 90584   0  31  0  4296844   2896 -      S    s000    0:00.19 -bash
  501 96095 90585   0  31  0  4258724    180 -      S+   s000    0:00.01 pbcopy
  501 82490 82489   0  31  0  4296844    496 -      S+   s001    0:00.11 -bash
  501 82557 82556   0  31  0  4296844   1260 -      S+   s002    0:00.43 -bash
""")    # noqa


def test_parse_ps_output():
    parsed = dict(_parse_ps_output(iter(PS_OUTPUT.split('\n'))))
    assert parsed == {
        '90585': Process(pid='90585', ppid='90584', args='-bash'),
        '96095': Process(pid='96095', ppid='90585', args='pbcopy'),
        '82490': Process(pid='82490', ppid='82489', args='-bash'),
        '82557': Process(pid='82557', ppid='82556', args='-bash'),
    }
