import pytest
from conftest import limit_leaks, LEAK_LIMIT

from newtype import NewTypeInit, NewTypeMethod


@limit_leaks(LEAK_LIMIT)
def free_standing_print(*args, **kwargs):
    print(*args, **kwargs)
    return args[0]


@limit_leaks(LEAK_LIMIT)
def test_freestanding_print():
    newtype_method_freestanding = NewTypeMethod(free_standing_print, str)
    assert newtype_method_freestanding("Hello", "World") == "Hello"


@limit_leaks(LEAK_LIMIT)
def test_freestanding_print_two():
    newtype_method_freestanding = NewTypeInit(free_standing_print)
    with pytest.raises(TypeError):
        assert newtype_method_freestanding("Hello", "Hello", "World") == "Hello"
