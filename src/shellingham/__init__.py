import importlib
import logging
import os

from ._core import ShellDetectionFailure


__version__ = '1.3.3dev0'

logger = logging.getLogger(__name__)


def detect_shell(pid=None, max_depth=6):
    name = os.name
    try:
        impl = importlib.import_module('.' + name, __name__)
    except ImportError as e:
        logger.debug('OS detection failed', exc_info=e)
        raise RuntimeError(
            'Shell detection not implemented for {0!r}'.format(name),
        )
    try:
        get_shell = impl.get_shell
    except AttributeError:
        raise RuntimeError('get_shell not implemented for {0!r}'.format(name))
    logger.info('Using OS backend %r', name)
    shell = get_shell(pid, max_depth=max_depth)
    if shell:
        return shell
    raise ShellDetectionFailure()
