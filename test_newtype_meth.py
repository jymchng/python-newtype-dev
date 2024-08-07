import pytest

from newtypemethod import NewTypeMethod

from conftest import limit_leaks, LEAK_LIMIT


class G:
    def __init__(self, val):
        self.val = val

    def add_one(self):
        self.val += 1

    add_one = NewTypeMethod(add_one, int)


@limit_leaks(LEAK_LIMIT)
def test_new_type_method():
    g = G(5)

    assert g.add_one() is None

    assert g.val == 6
