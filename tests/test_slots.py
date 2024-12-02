import pytest
from conftest import LEAK_LIMIT, limit_leaks

from newtype import NewType


class Base:
    __slots__ = ["name"]

    def __init__(self, name):
        self.name = name


class Derived(NewType(Base)):
    __slots__ = ["age"]

    def __init__(self, base, age):
        super().__init__(base)
        self.age = age


@limit_leaks(LEAK_LIMIT)
def test_base_slots():
    base = Base("TestName")
    assert base.name == "TestName"

    with pytest.raises(AttributeError):
        base.age = 30  # Should raise an error since 'age' is not a defined slot


@limit_leaks(LEAK_LIMIT)
def test_derived_slots():
    derived = Derived(Base("TestName"), 25)
    assert derived.name == "TestName"
    assert derived.age == 25

    with pytest.raises(AttributeError):
        derived.address = (
            "123 Street"  # Should raise an error since 'address' is not a defined slot
        )


@limit_leaks(LEAK_LIMIT)
def test_slots_inheritance():
    base = Base("BaseName")
    derived = Derived(base, 30)

    assert isinstance(derived, Base)
    assert derived.name == "BaseName"
    assert derived.age == 30

    # Check that base instance cannot access derived slots
    with pytest.raises(AttributeError):
        _ = base.age  # Should raise an error since 'age' is not a defined slot in Base


@limit_leaks(LEAK_LIMIT)
def test_supertype_subtype_both_have___slots__():
    class B:
        __slots__ = ('hi',)

    class A(NewType(B)):
        __slots__ = ('bye')

    a = A()
    a.hi = 1
    a.bye = 2
    with pytest.raises(AttributeError):
        a.hello = 3
        assert a.hello == 3

    assert a.hi == 1
    assert a.bye == 2
