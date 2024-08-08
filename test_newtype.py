from typing import TYPE_CHECKING

import pandas as pd
import pytest

from conftest import LEAK_LIMIT, limit_leaks
from newtype import NewType

if TYPE_CHECKING:
    pass


class PositiveInt(NewType(int)):
    is_positive = True

    def __init__(self, val: "int", **kwargs):
        super().__init__(val)
        self.__newtype__(val)

        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def __newtype__(cls, positive_int: int):
        assert (
            positive_int > 0
        ), f"`PositiveInt` object must be positive, but the passed in value is {positive_int}"
        return positive_int

    @classmethod
    def __get_validators__(cls):
        yield cls.__newtype__


@limit_leaks(LEAK_LIMIT)
def test_positive_int():
    five = PositiveInt(5, hello=3, bye=2, hey=1, you=29)
    assert five == 5
    assert five.you == 29
    assert five.hey == 1
    assert five.bye == 2
    assert five.hello == 3

    five += 20

    assert five == 25
    assert five.you == 29
    assert five.hey == 1
    assert five.bye == 2
    assert five.hello == 3


class BoundedPositiveInt(PositiveInt):
    def __init__(self, val: "int", upper: "int", lower: "int", *args, **kwargs):
        super().__init__(val, **kwargs)
        self.args = args
        self.upper = upper
        self.lower = lower
        assert self.lower < self < self.upper

    def middle(self):
        return (self.upper + self.lower) / 2


@limit_leaks(LEAK_LIMIT)
def test_bounded_positive_int():
    ten = BoundedPositiveInt(10, 20, 2, 1, 2, 3, hello=3, bye=4)

    assert ten == 10
    assert ten.upper == 20
    assert ten.lower == 2
    assert ten.args == (1, 2, 3)
    assert ten.middle() == 11

    with pytest.raises(AssertionError):
        ten += 20

    with pytest.raises(AssertionError):
        ten -= 30

    assert ten == 10
    ten += 5

    assert ten == 15
    assert ten.upper == 20
    assert ten.lower == 2
    assert ten.args == (1, 2, 3)
    assert ten.middle() == 11

    ten -= 9
    assert ten == 6
    assert ten.upper == 20
    assert ten.lower == 2
    assert ten.middle() == 11
    assert ten.args == (1, 2, 3)


class MyDataFrame(NewType(pd.DataFrame)):
    def __init__(self, df: pd.DataFrame, a, b, c):
        super().__init__(df)
        self.a = a
        self.b = b
        self.c = c

        assert df.shape == (2, 2)


@limit_leaks(LEAK_LIMIT)
def test_my_dataframe():
    df = pd.DataFrame({"A": [1, 2], "B": [4, 5]})
    my_df = MyDataFrame(df, 1, 2, 3)

    assert my_df.a == 1
    assert my_df.b == 2
    assert my_df.c == 3

    my_df = my_df.T

    assert my_df.a == 1
    assert my_df.b == 2
    assert my_df.c == 3

    assert my_df.at["A", 0] == 1
    assert my_df.at["A", 1] == 2
    assert my_df.at["B", 0] == 4
    assert my_df.at["B", 1] == 5

    my_df.at["A", 1] = 69
    assert my_df.at["A", 1] == 69

    my_df = my_df.T
    with pytest.raises(AssertionError):
        my_df.drop("A", axis=1)
