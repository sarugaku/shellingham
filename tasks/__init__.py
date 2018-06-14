import invoke

from . import news, pack

ns = invoke.Collection(news, pack)
