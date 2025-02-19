from enum import Enum

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
