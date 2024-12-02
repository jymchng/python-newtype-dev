import pytest
from newtype import NewType, newtype_exclude
from typing import Union, Optional


def test_enhanced_str():
    class EnhancedStr(NewType(str)):
        def reverse(self):
            return self[::-1]

        def duplicate(self):
            return self + self

    text = EnhancedStr("Hello")
    assert text.reverse() == "olleH"
    assert text.duplicate() == "HelloHello"
    assert text.upper() == "HELLO"

    # Test that it still behaves like a string
    assert isinstance(text, str)
    assert len(text) == 5
    assert text[0] == "H"


def test_typed_list():
    class TypedList(NewType(list)):
        def __init__(self, type_check=None):
            super().__init__()
            self.type_check = type_check

        def append(self, item):
            if self.type_check and not isinstance(item, self.type_check):
                raise TypeError(f"Item must be of type {self.type_check}")
            super().append(item)

    numbers = TypedList(type_check=int)
    numbers.append(42)
    assert len(numbers) == 1
    assert numbers[0] == 42

    with pytest.raises(TypeError):
        numbers.append("string")

    # Test that it works without type checking
    flexible_list = TypedList()
    flexible_list.append(42)
    flexible_list.append("string")
    assert len(flexible_list) == 2


def test_default_dict():
    class DefaultDict(NewType(dict)):
        def __init__(self, default_value=None):
            super().__init__()
            self.default_value = default_value

        def __getitem__(self, key):
            if key not in self:
                return self.default_value
            return super().__getitem__(key)

    d = DefaultDict(default_value=0)
    assert d["non_existent"] == 0

    d["exists"] = 42
    assert d["exists"] == 42

    # Test with different default values
    d_none = DefaultDict()
    assert d_none["any_key"] is None

    d_list = DefaultDict(default_value=[])
    assert d_list["any_key"] == []

    # Test that it still behaves like a dict
    assert len(d) == 1
    assert "exists" in d
    assert "non_existent" not in d


def test_inheritance_chain():
    class BaseDict(NewType(dict)):
        def get_keys_sorted(self):
            return sorted(self.keys())

    class ExtendedDict(BaseDict):
        def get_values_sorted(self):
            return sorted(self.values())

    d = ExtendedDict()
    d.update({"c": 3, "a": 1, "b": 2})

    assert d.get_keys_sorted() == ["a", "b", "c"]
    assert d.get_values_sorted() == [1, 2, 3]
    assert isinstance(d, dict)
    assert isinstance(d, BaseDict)
    assert isinstance(d, ExtendedDict)


def test_safe_str():
    class SafeStr(NewType(str)):
        def __init__(self, value: str):
            if "<script>" in value.lower():
                raise ValueError("XSS attempt detected")
            super().__init__()

        @newtype_exclude
        def unsafe_operation(self):
            return str(self)

        def safe_operation(self):
            return self.lower()

    # Test initialization
    text = SafeStr("Hello")
    assert isinstance(text, SafeStr)
    assert isinstance(text, str)

    # Test XSS detection
    with pytest.raises(ValueError, match="XSS attempt detected"):
        SafeStr("<script>alert('xss')</script>")

    # Test method type preservation
    assert isinstance(text.safe_operation(), SafeStr)
    assert not isinstance(text.unsafe_operation(), SafeStr)
    assert isinstance(text.unsafe_operation(), str)


def test_memory_efficient_str():
    class MemoryEfficientStr(NewType(str)):
        __slots__ = ['_cached_value']

        def __init__(self, value: str):
            super().__init__(value)
            self._cached_value = None

        def compute_expensive(self):
            if self._cached_value is None:
                self._cached_value = self.upper() + self.lower()
            return self._cached_value

    # Test initialization and basic string operations
    text = MemoryEfficientStr("Hello")
    assert isinstance(text, MemoryEfficientStr)
    assert isinstance(text, str)
    assert text == "Hello"

    # Test caching behavior
    expected = "HELLOhello"
    result1 = text.compute_expensive()
    assert result1 == expected
    assert text._cached_value == expected

    # Test that cached value is reused
    result2 = text.compute_expensive()
    assert result2 == expected
    assert result1 is result2  # Should be the same object due to caching

    assert hasattr(text, '__slots__')

    # Test slots (no need to test this because inherited
    # class with `__slots__` but super class as no `__slots__` will get a `__dict__`)
    # with pytest.raises(AttributeError):
    # text.new_attribute = "test"  # Should fail due to __slots__


def test_integer_str():
    class IntegerStr(NewType(str)):
        def __init__(self, value: Union[str, int], base: int = 10):
            if isinstance(value, int):
                value = str(value)
            try:
                int(value, base)
            except ValueError:
                raise ValueError(f"Value must be a valid integer in base {base}")
            super().__init__()

        def to_int(self, base: Optional[int] = None) -> int:
            return int(self, base or 10)

    # Test initialization with string
    num1 = IntegerStr("42")
    assert isinstance(num1, IntegerStr)
    assert isinstance(num1, str)
    assert num1 == "42"

    # Test initialization with integer
    num2 = IntegerStr(42)
    assert num2 == "42"
    assert num2.to_int() == 42

    # Test hexadecimal
    hex_num = IntegerStr("2A", base=16)
    assert hex_num == "2A"
    assert hex_num.to_int(16) == 42

    # Test invalid input
    with pytest.raises(ValueError):
        IntegerStr("not a number")

    with pytest.raises(ValueError):
        IntegerStr("GG", base=16)  # Invalid hex number
