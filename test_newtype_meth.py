import pytest

from newtypemethod import NewTypeMethod
from newtype import NewType

from conftest import limit_leaks, LEAK_LIMIT


class G(NewType(str)):
    def __init__(self, val, a, b, c):
        self.val = val

    def add_one(self):
        self.val += 1


@limit_leaks(LEAK_LIMIT)
def test_new_type_method():
    g = G(5, 1, 2, 3)

    assert g.add_one() is None

    assert g.val == 6
