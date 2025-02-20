from enum import Enum
from weakref import WeakValueDictionary

import pytest
from newtype import NewType


class ENV(NewType(str), Enum):  # type: ignore[misc]

    LOCAL = "LOCAL"
    DEV = "DEV"
    SIT = "SIT"
    UAT = "UAT"
    PREPROD = "PREPROD"
    PROD = "PROD"


# mypy doesn't raise errors here
def test_nt_env_replace() -> None:

    env = ENV.LOCAL

    assert env is ENV.LOCAL
    assert env is not ENV.DEV
    assert isinstance(env, ENV)

    # let's say now we want to replace the environment
    # nevermind about the reason why we want to do so
    env = env.replace(ENV.LOCAL, ENV.DEV)
    # reveal_type(env) # Revealed type is "newtype_enums.ENV"

    # replacement is successful
    assert env is ENV.DEV
    assert env is not ENV.LOCAL

    # still an `ENV`
    assert isinstance(env, ENV)
    assert isinstance(env, str)

    with pytest.raises(ValueError):
        # cannot replace with something that is not a `ENV`
        env = env.replace(ENV.DEV, "NotAnEnv")

    # reveal_type(env) # Revealed type is "newtype_enums.ENV"

    with pytest.raises(ValueError):
        # cannot even make 'DEV' -> 'dev'
        env = env.lower()


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
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


def test_severity():
    assert Severity.DEBUG == 0
    assert Severity.INFO == 1
    assert Severity.WARNING == 2
    assert Severity.ERROR == 3
    assert Severity.CRITICAL == 4

    with pytest.raises(AttributeError, match=r"[c|C]annot\s+reassign\s+\w+"):
        Severity.ERROR += 1

    severity = Severity.ERROR
    assert severity == 3

    severity += 1
    assert severity == 4
    assert severity != 3
    assert isinstance(severity, int)
    assert isinstance(severity, Severity)
    assert severity is not Severity.ERROR
    assert severity is Severity.CRITICAL

    severity -= 1
    assert severity == 3
    assert severity != 4
    assert isinstance(severity, int)
    assert isinstance(severity, Severity)
    assert severity is Severity.ERROR
    assert severity is not Severity.CRITICAL

    severity = Severity.DEBUG
    assert severity == 0
    assert str(severity.value) == "0"
    with pytest.raises(ValueError, match=r"\d+ is not a valid Severity"):
        severity -= 1

    severity = Severity.CRITICAL
    assert severity == 4
    assert str(severity.value) == "4"
    with pytest.raises(ValueError, match=r"\d+ is not a valid Severity"):
        severity += 1
