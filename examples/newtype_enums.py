from enum import Enum

import pytest

from newtype import NewType, newtype_exclude


class ENV(NewType(str), Enum):

    LOCAL = "LOCAL"
    DEV = "DEV"
    SIT = "SIT"
    UAT = "UAT"
    PREPROD = "PREPROD"
    PROD = "PROD"

class RegularENV(str, Enum):

    LOCAL = "LOCAL"
    DEV = "DEV"
    SIT = "SIT"
    UAT = "UAT"
    PREPROD = "PREPROD"
    PROD = "PROD"

class ENVVariant(str):

    __VALID_MEMBERS__ = ["LOCAL", "DEV", "SIT", "UAT", "PREPROD", "PROD"]

    def __new__(cls, value: str):
        members = ENVVariant.__VALID_MEMBERS__
        # if isinstance(value, RollYourOwnNewTypeEnum):
        #     value_as_str = str(value.value)
        # else:
        value_as_str = str(value)
        if value_as_str not in members:
            raise ValueError(f"`value` = {value} must be one of `{members}`; `value_as_str` = {value_as_str}")
        return super().__new__(cls, value_as_str)

    # why not i write my own `.replace(..)`
    # yes, you can but how?
    def my_replace(self, old: "ENVVariant", new: "ENVVariant", count: int=-1):
        return ENVVariant(str(self).replace(str(old), str(new), count))

class RollYourOwnNewTypeEnum(ENVVariant, Enum):

    LOCAL = "LOCAL"
    DEV = "DEV"
    SIT = "SIT"
    UAT = "UAT"
    PREPROD = "PREPROD"
    PROD = "PROD"


def test_nt_env_replace():

    env = ENV.LOCAL

    assert env is ENV.LOCAL
    assert env is not ENV.DEV
    assert isinstance(env, ENV)

    # let's say now we want to replace the environment
    # nevermind about the reason why we want to do so
    env = env.replace(ENV.LOCAL, ENV.DEV)

    # replacement is successful
    assert env is ENV.DEV
    assert env is not ENV.LOCAL

    # still an `ENV`
    assert isinstance(env, ENV)
    assert isinstance(env, str)

    with pytest.raises(ValueError):
        # cannot replace with something that is not a `ENV`
        env = env.replace(ENV.DEV, "NotAnEnv")

    with pytest.raises(ValueError):
        # cannot even make 'DEV' -> 'dev'
        env = env.lower()

def test_reg_env_replace():

    env = RegularENV.LOCAL

    # expected outcomes
    assert env is RegularENV.LOCAL # pass
    assert env is not RegularENV.DEV # pass
    assert isinstance(env, RegularENV) # pass

    # now we try to replace
    env = env.replace(RegularENV.LOCAL, RegularENV.DEV)

    # we are hoping that it will continue to be a `RegularENV.DEV` but it is not
    assert env is not RegularENV.DEV # pass, no longer a `RegularENV`
    assert env is not RegularENV.LOCAL # pass, no longer a `RegularENV`
    assert not isinstance(env, RegularENV)
    assert isinstance(env, str) # 'downcast' (?) to `str`

def test_ryont_env_replace():

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

    # env = env.my_replace(RollYourOwnNewTypeEnum.LOCAL, RollYourOwnNewTypeEnum.PREPROD)

    assert isinstance(env, str)
    assert env is not RollYourOwnNewTypeEnum.PREPROD
    assert isinstance(env, RollYourOwnNewTypeEnum)
