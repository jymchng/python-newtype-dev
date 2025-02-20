from enum import Enum
from weakref import WeakValueDictionary

import pytest

from newtype import NewType


class GenericWrappedBoundedInt(NewType(int)):
    MAX_VALUE: int = 0

    __CONCRETE_BOUNDED_INTS__ = WeakValueDictionary()

    def __new__(cls, value: int):
        inst = super().__new__(cls, value % cls.MAX_VALUE)
        return inst

    def __repr__(self) -> str:
        return f"<BoundedInt[MAX_VALUE={self.MAX_VALUE}]: {super().__repr__()}>"

    def __str__(self) -> str:
        return str(int(self))

    def __class_getitem__(cls, idx=MAX_VALUE):
        if not isinstance(idx, int):
            raise TypeError(f"cannot make `BoundedInt[{idx}]`")

        if idx not in cls.__CONCRETE_BOUNDED_INTS__:

            class ConcreteBoundedInt(cls):
                MAX_VALUE = idx

            cls.__CONCRETE_BOUNDED_INTS__[idx] = ConcreteBoundedInt

        return cls.__CONCRETE_BOUNDED_INTS__[idx]


class Severity(GenericWrappedBoundedInt[5], Enum):
    # `GenericWrappedBoundedInt` is a `NewType` that wraps an `int` and
    # ensures that the value is within the bounds of the enum.
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


# IntSeverity demonstrates a basic integer-based enum implementation
# This shows the limitations compared to the NewType-based Severity enum above
class IntSeverity(int, Enum):
    # Standard severity levels mapped to integers 0-4
    DEBUG = 0      # Lowest severity - debug messages
    INFO = 1       # Informational messages
    WARNING = 2    # Warning conditions
    ERROR = 3      # Error conditions
    CRITICAL = 4   # Critical conditions requiring immediate attention


def test_int_severity():
    # Basic enum value tests - similar to Severity
    assert IntSeverity.DEBUG == 0
    assert IntSeverity.INFO == 1
    assert IntSeverity.WARNING == 2
    assert IntSeverity.ERROR == 3
    assert IntSeverity.CRITICAL == 4

    # Initial enum value assignment works like Severity
    int_severity = IntSeverity.ERROR
    assert int_severity == 3
    assert int_severity != 4
    assert isinstance(int_severity, int)
    assert isinstance(int_severity, IntSeverity)
    assert int_severity is not IntSeverity.CRITICAL
    assert int_severity is IntSeverity.ERROR

    # DISADVANTAGE 1: Arithmetic operations break enum type safety
    # Unlike Severity which maintains its type after arithmetic,
    # IntSeverity degrades to a plain int
    int_severity -= 1
    assert int_severity == 2
    assert int_severity != 3
    assert isinstance(int_severity, int)
    with pytest.raises(AssertionError):
        # DISADVANTAGE 2: Lost enum type after arithmetic
        assert isinstance(int_severity, IntSeverity)

    # DISADVANTAGE 3: Lost enum identity after arithmetic
    assert int_severity is not IntSeverity.ERROR
    with pytest.raises(AssertionError):
        # Even though value matches WARNING (2), it's not the same object
        assert int_severity is IntSeverity.WARNING

    # Overall, IntSeverity provides less type safety and consistency
    # compared to Severity which maintains its type and identity
    # through arithmetic operations


def test_severity():
    # Test that enum values map to expected integers
    assert Severity.DEBUG == 0
    assert Severity.INFO == 1
    assert Severity.WARNING == 2
    assert Severity.ERROR == 3
    assert Severity.CRITICAL == 4

    # Test that enum values themselves are immutable
    # Should raise AttributeError when trying to modify the enum value directly
    with pytest.raises(AttributeError, match=r"[c|C]annot\s+reassign\s+\w+"):
        Severity.ERROR += 1

    # Test working with enum values as variables
    severity = Severity.ERROR
    assert severity == 3

    # Test incrementing severity level
    # When incrementing, should get next enum value
    severity += 1
    assert severity == 4  # New value should be 4
    assert severity != 3  # Old value should no longer match
    assert isinstance(severity, int)  # Should still be an int
    assert isinstance(severity, Severity)  # Should still be a Severity
    assert severity is not Severity.ERROR  # Should no longer be ERROR
    assert severity is Severity.CRITICAL  # Should now be CRITICAL

    # Test decrementing severity level
    # When decrementing, should get previous enum value
    severity -= 1
    assert severity == 3  # New value should be 3
    assert severity != 4  # Old value should no longer match
    assert isinstance(severity, int)  # Should still be an int
    assert isinstance(severity, Severity)  # Should still be a Severity
    assert severity is Severity.ERROR  # Should now be ERROR
    assert severity is not Severity.CRITICAL  # Should no longer be CRITICAL

    # Test lower bound handling
    severity = Severity.DEBUG
    assert severity == 0  # DEBUG is lowest severity
    assert str(severity.value) == "0"
    # Should raise ValueError when trying to go below DEBUG (0)
    with pytest.raises(ValueError, match=r"\d+ is not a valid Severity"):
        severity -= 1

    # Test upper bound handling
    severity = Severity.CRITICAL
    assert severity == 4  # CRITICAL is highest severity
    assert str(severity.value) == "4"
    # Should raise ValueError when trying to go above CRITICAL (4)
    with pytest.raises(ValueError, match=r"\d+ is not a valid Severity"):
        severity += 1
