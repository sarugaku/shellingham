import ast
import pathlib

import invoke
import parver


DEV_VARS = ['dev']
PRE_VARS = ['alpha', 'beta']
REL_VARS = ['major', 'minor', 'patch']

ALL_VARS = DEV_VARS + PRE_VARS + REL_VARS

ROOT = pathlib.Path(__file__).resolve().parent.parent

INIT_PY = ROOT.join('src', 'shellingham', '__init__.py')


def read_version():
    with INIT_PY.open() as f:
        for line in f:
            if line.startswith('__version__ = '):
                return ast.literal_eval(line[len('__version__ = '):]).strip()


def write_version(v):
    lines = []
    with INIT_PY.open() as f:
        for line in f:
            if line.startswith('__version__ = '):
                line = f'__version__ = {str(v)!r}\n'
            lines.append(line)
    with INIT_PY.open('w') as f:
        f.writelines(lines)


@invoke.task()
def bump(ctx, type_):
    if type_.isdigit():
        type_ = 'release'
        index = int(type_)
    elif type_ in REL_VARS:
        type_ = 'release'
        index = REL_VARS.index(type_)
    elif type_ in PRE_VARS:
        type_ = 'pre'
        tag = type_
    elif type_ not in PRE_VARS:
        variant_list = ', '.join(repr(v) for v in ALL_VARS)
        print(f"[vers.bump] Invalid type. "
              f"Should be an index or one of {variant_list!r}")
        return

    curver = parver.Version.parse(read_version()).normalize()

    if type_ == 'release':
        newver = curver.bump_release(index)
    else:
        newver = getattr(curver, f'bump_{type_}')()
    print(f'[vers.bump] Bumping {curver} -> {newver}')
    write_version(newver)
