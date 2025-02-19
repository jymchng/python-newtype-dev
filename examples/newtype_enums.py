from enum import Enum
from typing import Optional, Type

import pytest
from newtype import NewType


class ENV(NewType(str), Enum): # type: ignore[misc]

    LOCAL = "LOCAL"
    DEV = "DEV"
    SIT = "SIT"
    UAT = "UAT"
    PREPROD = "PREPROD"
    PROD = "PROD"

print(type(ENV.LOCAL))
print(type(ENV.LOCAL).__mro__)
print(super(ENV, ENV.LOCAL).__self_class__)
print(super(ENV, ENV.LOCAL).__thisclass__)
print(super(super(ENV, ENV.LOCAL).__self_class__))
print(super(ENV))
print(str.__str__(ENV.LOCAL))

class RegularENV(str, Enum):

    LOCAL = "LOCAL"
    DEV = "DEV"
    SIT = "SIT"
    UAT = "UAT"
    PREPROD = "PREPROD"
    PROD = "PROD"

RollYourOwnNewTypeEnum: "Optional[Type[RollYourOwnNewTypeEnum]]" = None

class ENVVariant(str):

    __VALID_MEMBERS__ = ["LOCAL", "DEV", "SIT", "UAT", "PREPROD", "PROD"]

    def __new__(cls, value: str) -> "ENVVariant":
        members = ENVVariant.__VALID_MEMBERS__
        value_as_str = str(value.value if hasattr(value, "value") else value)
        if value_as_str not in members:
            raise ValueError(f"`value` = {value} must be one of `{members}`; `value_as_str` = {value_as_str}")
        return super().__new__(cls, value_as_str)

    def my_replace(self, old: "ENVVariant", new: "ENVVariant", count: int=-1) -> "ENVVariant":
        # Convert both old and new to their string values
        old_str = str(old.value if hasattr(old, "value") else old)
        new_str = str(new.value if hasattr(new, "value") else new)
        # Do the replacement on string values
        result = str(self.value if hasattr(self, "value") else self).replace(old_str, new_str, count)
        # For enums, we need to look up the enum member by value
        if issubclass(type(self), Enum):
            return type(self)(result)  # This will find the enum member

        # For non-enum types, create new instance directly
        return type(self)(result)

class RollYourOwnNewTypeEnum(ENVVariant, Enum): # type: ignore[no-redef]

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
    print(f"`env`: {env}; type: {type(env)}")

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

def test_reg_env_replace() -> None:

    env = RegularENV.LOCAL

    # expected outcomes
    assert env is RegularENV.LOCAL # pass
    assert env is not RegularENV.DEV # pass
    assert isinstance(env, RegularENV) # pass

    # now we try to replace
    env = env.replace("LOCAL", "DEV")

    # we are hoping that it will continue to be a `RegularENV.DEV` but it is not
    assert env is not RegularENV.DEV # pass, no longer a `RegularENV`
    assert env is not RegularENV.LOCAL # pass, no longer a `RegularENV`
    assert not isinstance(env, RegularENV)
    assert isinstance(env, str) # 'downcast' (?) to `str`

def test_ryont_env_replace() -> None:

    assert RollYourOwnNewTypeEnum is not None

    env = RollYourOwnNewTypeEnum.LOCAL

    # expected outcomes
    assert env is RollYourOwnNewTypeEnum.LOCAL # pass
    assert env is not RollYourOwnNewTypeEnum.DEV # pass
    assert isinstance(env, RollYourOwnNewTypeEnum) # pass

    # now we try to replace
    env = env.replace(RollYourOwnNewTypeEnum.LOCAL, RollYourOwnNewTypeEnum.DEV)

    # we are hoping that it will continue to be a `RollYourOwnNewTypeEnum.DEV` but it is not
    assert env is not RollYourOwnNewTypeEnum.DEV # pass, no longer a `RollYourOwnNewTypeEnum`
    assert env is not RollYourOwnNewTypeEnum.LOCAL # pass, no longer a `RollYourOwnNewTypeEnum`
    assert not isinstance(env, RollYourOwnNewTypeEnum)
    assert isinstance(env, str) # 'downcast' (?) to `str`

    with pytest.raises(AssertionError):
        assert env is RollYourOwnNewTypeEnum.DEV

    with pytest.raises(AssertionError):
        assert env is RollYourOwnNewTypeEnum.DEV

    with pytest.raises(AssertionError):
        assert isinstance(env, RollYourOwnNewTypeEnum)

    env = env.replace("DEV", "NotAnEnv")
    assert env == "NotAnEnv" # this 'shouldn't' pass but it does

    env = RollYourOwnNewTypeEnum.LOCAL

    env = env.my_replace(RollYourOwnNewTypeEnum.LOCAL, RollYourOwnNewTypeEnum.PREPROD)

    assert isinstance(env, str)
    assert env is RollYourOwnNewTypeEnum.PREPROD
    assert isinstance(env, RollYourOwnNewTypeEnum)
