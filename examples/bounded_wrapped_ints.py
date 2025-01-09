from weakref import WeakValueDictionary

import pytest

from newtype import NewType


class GenericWrappedBoundedInt_WithNewType(NewType(int)):  # never mind about the '_'
    MAX_VALUE: int = 0

    __CONCRETE_BOUNDED_INTS__ = WeakValueDictionary()

    def __new__(cls, value: int):
        inst = super().__new__(cls, value % cls.MAX_VALUE)
        return inst

    def __repr__(self) -> str:
        return f"<BoundedInt[MAX_VALUE={self.MAX_VALUE}]: {super().__repr__()}>"

    def __str__(self) -> str:
        return repr(self)

    def __class_getitem__(cls, idx=MAX_VALUE):
        if not isinstance(idx, int):
            raise TypeError(f"cannot make `BoundedInt[{idx}]`")

        if idx not in cls.__CONCRETE_BOUNDED_INTS__:

            class ConcreteBoundedInt(cls):
                MAX_VALUE = idx

            cls.__CONCRETE_BOUNDED_INTS__[idx] = ConcreteBoundedInt

        return cls.__CONCRETE_BOUNDED_INTS__[idx]

    # here you have NO need to write many operator overrides: +, -, etc.


class GenericWrappedBoundedInt_WithoutNewType(int):  # never mind about the '_'
    MAX_VALUE: int = 0

    __CONCRETE_BOUNDED_INTS__ = WeakValueDictionary()

    def __new__(self, value: int):
        inst = super().__new__(self, value % self.MAX_VALUE)
        return inst

    def __repr__(self) -> str:
        return f"<BoundedInt[MAX_VALUE={self.MAX_VALUE}]: {super().__repr__()}>"

    def __str__(self) -> str:
        return repr(self)

    def __class_getitem__(cls, idx=MAX_VALUE):
        if not isinstance(idx, int):
            raise TypeError(f"cannot make `BoundedInt[{idx}]`")

        if idx not in cls.__CONCRETE_BOUNDED_INTS__:

            class ConcreteBoundedInt(cls):
                MAX_VALUE = idx

            cls.__CONCRETE_BOUNDED_INTS__[idx] = ConcreteBoundedInt

        return cls.__CONCRETE_BOUNDED_INTS__[idx]

    def __mul__(
        self, other: "GenericWrappedBoundedInt_WithoutNewType"
    ) -> "GenericWrappedBoundedInt_WithoutNewType":
        # handwritten `__mul__`
        return self.__class__(int(self) * int(other))

    # here you got to write many operator overrides: +, -, etc.


def test_bounded_int_without_newtype():
    # pytest examples/bounded_wrapped_ints.py -s -vv
    bounded_twenty_int_value = GenericWrappedBoundedInt_WithoutNewType[20](11)

    bounded_twenty_int_value += 10  # return type here is int
    with pytest.raises(AssertionError):
        # (11 + 10 = 21) % 20 = 1
        assert bounded_twenty_int_value == (11 + 10) % 20
    # but no: `bounded_twenty_int_value` = 11 + 10 = 21
    assert bounded_twenty_int_value == 21  #
    assert isinstance(bounded_twenty_int_value, int)
    assert not isinstance(bounded_twenty_int_value, GenericWrappedBoundedInt_WithoutNewType[20])

    bounded_twenty_int_value -= 22
    with pytest.raises(AssertionError):
        # (21 - 22 = -1) % 20 = 19
        assert bounded_twenty_int_value == (21 - 22) % 20
    # but no: `bounded_twenty_int_value` = 21 - 22 = -1
    assert bounded_twenty_int_value == -1
    assert isinstance(bounded_twenty_int_value, int)
    assert not isinstance(bounded_twenty_int_value, GenericWrappedBoundedInt_WithoutNewType[20])


def test_bounded_int_with_newtype():
    # pytest examples/bounded_wrapped_ints.py -s -vv
    bounded_twenty_int_value = GenericWrappedBoundedInt_WithNewType[20](11)

    bounded_twenty_int_value += 10
    assert bounded_twenty_int_value == (11 + 10) % 20  # (11 + 10 = 21) % 20 = 1
    assert isinstance(bounded_twenty_int_value, GenericWrappedBoundedInt_WithNewType[20])

    another_bounded_twenty_int_value = GenericWrappedBoundedInt_WithNewType[20](11)
    yet_another_bounded_twenty_int_value = another_bounded_twenty_int_value + 10
    assert yet_another_bounded_twenty_int_value == (11 + 10) % 20  # (11 + 10 = 21) % 20 = 1
    assert isinstance(
        yet_another_bounded_twenty_int_value, GenericWrappedBoundedInt_WithNewType[20]
    )

    bounded_twenty_int_value -= 21
    assert bounded_twenty_int_value == (1 - 21) % 20  # (1 - 21 = -20) % 20 = 0
    assert isinstance(bounded_twenty_int_value, GenericWrappedBoundedInt_WithNewType[20])


def benchmark():
    # python -m examples.bounded_wrapped_ints
    import time

    bounded_twenty_int_value_wo_newtype = GenericWrappedBoundedInt_WithoutNewType[20](11)
    bounded_twenty_int_value_w_newtype = GenericWrappedBoundedInt_WithNewType[20](11)

    start_time = time.time()
    for _ in range(100_000):
        bounded_twenty_int_value_wo_newtype *= 10
    end_time = time.time()
    print(f"Benchmark completed in {end_time - start_time:.10f} seconds")
    print(f"Final value: {bounded_twenty_int_value_wo_newtype}")
    assert bounded_twenty_int_value_wo_newtype == (11 * 10 * 100_000) % 20

    start_time = time.time()
    for _ in range(100_000):
        bounded_twenty_int_value_w_newtype *= 10
    end_time = time.time()
    print(f"Benchmark completed in {end_time - start_time:.10f} seconds")
    print(f"Final value: {bounded_twenty_int_value_w_newtype}")
    assert bounded_twenty_int_value_w_newtype == (11 * 10 * 100_000) % 20

    # `bounded_twenty_int_value_wo_newtype`
    # Benchmark completed in 0.1382505894 seconds
    # Final value: <BoundedInt[MAX_VALUE=20]: 0>

    # `bounded_twenty_int_value_w_newtype`
    # Benchmark completed in 0.5179963112 seconds
    # Final value: <BoundedInt[MAX_VALUE=20]: 0>


if __name__ == "__main__":
    benchmark()
