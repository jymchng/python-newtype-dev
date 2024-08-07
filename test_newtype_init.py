import pytest

from newtypeinit import NEWTYPE_INIT_ARGS_STR, NEWTYPE_INIT_KWARGS_STR, NewInit
from newtype import NewType

from conftest import limit_leaks, LEAK_LIMIT


class G(NewType(str)):
    def __init__(self, val, a, b, c):
        self.val = val

    def add_one(self):
        self.val += 1

    __init__ = NewInit(__init__)


@limit_leaks(LEAK_LIMIT)
def test_new_init_method():
    g = G(5, 1, 2, 3)

    assert getattr(g, NEWTYPE_INIT_ARGS_STR) == (1, 2, 3)
    assert getattr(g, NEWTYPE_INIT_KWARGS_STR) == {}
