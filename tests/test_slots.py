import pytest
from conftest import LEAK_LIMIT, limit_leaks
import re

from newtype import NewType, newtype_exclude


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
        base.__dict__

    with pytest.raises(AttributeError):
        base.age = 30  # Should raise an error since 'age' is not a defined slot


@limit_leaks(LEAK_LIMIT)
def test_derived_slots():
    derived = Derived(Base("TestName"), 25)
    assert derived.name == "TestName"
    assert derived.age == 25

    with pytest.raises(AttributeError):
        derived.__dict__

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


class EmailStr(NewType(str)):
    __slots__ = (
        '_local_part',
        '_domain_part',
    )

    def __init__(self, value: str):
        super().__init__(value)
        if "@" not in value:
            raise TypeError("`EmailStr` requires a '@' symbol within")
        self._local_part, self._domain_part = value.split("@")

    @newtype_exclude
    def __str__(self):
        return f"<Email - Local Part: {self.local_part}; Domain Part: {self.domain_part}>"

    @property
    def local_part(self):
        """Return the local part of the email address."""
        return self._local_part

    @property
    def domain_part(self):
        """Return the domain part of the email address."""
        return self._domain_part

    @property
    def full_email(self):
        """Return the full email address."""
        return str(self)

    @classmethod
    def from_string(cls, email: str):
        """Create an EmailStr instance from a string."""
        return cls(email)

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if the provided string is a valid email format."""
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_regex, email) is not None


class OEmailStr(str):
    __slots__ = (
        '_local_part',
        '_domain_part',
    )

    def __new__(cls, value: str):
        return super().__new__(cls, value)


def test_oemail_str__slots__():
    # subclass of `str` with defined `__slots__`
    # is expected to NOT have attributes NOT defined within `__slots__`
    oemail = OEmailStr("test@example.com")

    with pytest.raises(AttributeError):
        oemail.hi = "bye"
        assert oemail.hi == "bye"


def test_regular_classes_without_base_class__slots__():

    class Base:
        __slots__ = ()

    class Derived(Base):
        __slots__ = (
            'attr1',
            'attr2',
        )

        def __init__(self):
            super().__init__()
            self.attr1 = None
            self.attr2 = None

    with pytest.raises(AttributeError):
        d = Derived()
        d.attr3 = "hey"
        assert d.attr3 == "hey"


class SlottedBase:
    __slots__ = ['inner']

    def __init__(self, inner: int):
        self.inner = inner

    def copy(self):
        return SlottedBase(self.inner)


class SlottedSubType(NewType(SlottedBase)):
    __slots__ = ['inner2']

    def __init__(self, base: SlottedBase, inner2: int):
        self.inner2 = inner2


def test_slotted_types():
    # Create instances
    slotted_sub = SlottedSubType(SlottedBase(1), 2)
    assert slotted_sub.inner == 1
    assert slotted_sub.inner2 == 2

    # Modify and copy
    slotted_sub.inner2 = 3
    slotted_copy = slotted_sub.copy()
    assert slotted_sub.inner == 1
    assert slotted_sub.inner2 == 3

    # Verify copy has correct values
    assert slotted_copy.inner == 1
    assert slotted_copy.inner2 == 3

    # Verify modifications don't affect original
    slotted_copy.inner2 = 4
    assert slotted_sub.inner2 == 3
    assert slotted_copy.inner2 == 4

    # Verify __slots__ are working
    try:
        slotted_sub.new_attr = 5  # Should raise AttributeError
        assert False, "Should not be able to add new attributes"
    except AttributeError:
        pass
