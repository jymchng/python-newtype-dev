import pytest

from conftest import LEAK_LIMIT, limit_leaks
from newtype import NewType


class Super:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    # If a class method is called for a derived class, the derived class
    # object is passed as the implied first argument.

    async def get_a(self):
        return self.a

    async def get_b(self):
        return self.b

    async def return_self(self):
        self.a = 99
        return Super(99, self.b)


class Derived(NewType(Super)):
    def __init__(self, super_inst, c, d):
        super().__init__(super_inst)
        self.c = c
        self.d = d


@limit_leaks(LEAK_LIMIT)
@pytest.mark.asyncio
async def test_async():
    super_one = Super(1, 2)
    derived_one = Derived(super_one, 3, 4)
    assert (await derived_one.get_a()) == 1
    assert (await derived_one.get_b()) == 2
    assert (await derived_one.return_self()).a == 99
    assert (await derived_one.return_self()).b == 2
    with pytest.raises(AttributeError):
        assert (await derived_one.return_self()).c == 3
    with pytest.raises(AttributeError):
        assert (await derived_one.return_self()).d == 4
    # TODO change this to `assert type(await derived_one.return_self()) is Derived`
    assert type(await derived_one.return_self()) is Super
