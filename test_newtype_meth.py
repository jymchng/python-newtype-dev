import pytest
from newtypemethod import (
    NewTypeMethod,
)


class G:
    def __init__(self, val):
        self.val = val

    def add_one(self):
        self.val += 1

    add_one = NewTypeMethod(add_one, int)


def test_new_type_method():
    g = G(5)
    # assert g.add_one.obj == g
    # assert g.add_one.cls == G

    assert g.add_one() is None

    assert g.val == 6
