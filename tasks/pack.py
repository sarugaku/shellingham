import pathlib
import shutil

import invoke


ROOT = pathlib.Path(__file__).resolve().parent.parent


@invoke.task()
def build(ctx):
    """Build the package into distributables.
    This will create two distributables: source and wheel.
    """
    ctx.run(f'python setup.py sdist bdist_wheel')


@invoke.task()
def clean(ctx):
    """Clean previously built package artifacts.
    """
    ctx.run(f'python setup.py clean')
    dist = ROOT.joinpath('dist')
    print(f'[pack:clean] Removing {dist}')
    shutil.rmtree(str(dist))


@invoke.task(pre=[clean, build])
def upload(ctx, repo):
    """Upload the package to an index server.
    This implies cleaning and re-building the package.
    :param repo: Required. Name of the index server to upload to, as specifies
        in your .pypirc configuration file.
    """
    artifacts = ' '.join(
        f'"{n}"' for n in ROOT.joinpath('dist').glob('shellingham-*')
    )
    ctx.run(f'twine upload --repository="{repo}" {artifacts}')
