import pytest

from newtype import NewInit, NewTypeMethod


def free_standing_print(*args, **kwargs):
    print(*args, **kwargs)
    return args[0]


def test_freestanding_print():
    newtype_method_freestanding = NewTypeMethod(free_standing_print, str)
    assert newtype_method_freestanding("Hello", "World") == "Hello"


def test_freestanding_print_two():
    newtype_method_freestanding = NewInit(free_standing_print)
    with pytest.raises(TypeError):
        assert newtype_method_freestanding("Hello", "Hello", "World") == "Hello"
