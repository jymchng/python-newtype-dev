# Basic Examples

## String Enhancement
```python
from newtype import NewType

class EnhancedStr(NewType(str)):
    def reverse(self):
        return self[::-1]

    def duplicate(self):
        return self + self

text = EnhancedStr("Hello")
print(text.reverse())     # olleH
print(text.duplicate())   # HelloHello
print(text.upper())       # HELLO (original str methods work)
```

## List with Validation
```python
from newtype import NewType

class TypedList(NewType(list)):
    def __init__(self, type_check=None):
        super().__init__()
        self.type_check = type_check

    def append(self, item):
        if self.type_check and not isinstance(item, self.type_check):
            raise TypeError(f"Item must be of type {self.type_check}")
        super().append(item)

# Usage
numbers = TypedList(type_check=int)
numbers.append(42)        # Works
numbers.append("string")  # Raises TypeError
```

## Dictionary with Default Values
```python
from newtype import NewType

class DefaultDict(NewType(dict)):
    def __init__(self, default_value=None):
        super().__init__()
        self.default_value = default_value

    def __getitem__(self, key):
        if key not in self:
            return self.default_value
        return super().__getitem__(key)

# Usage
d = DefaultDict(default_value=0)
print(d["non_existent"])  # 0
d["exists"] = 42
print(d["exists"])       # 42
```

## Method Exclusion with @newtype_exclude
```python
from newtype import NewType, newtype_exclude

class SafeStr(NewType(str)):
    def __init__(self, value: str):
        if "<script>" in value.lower():
            raise ValueError("XSS attempt detected")
        super().__init__()

    # This method will return a regular str, not a SafeStr
    @newtype_exclude
    def unsafe_operation(self):
        return str(self)

    # This method will return a SafeStr
    def safe_operation(self):
        return self.lower()

# Usage
text = SafeStr("Hello")
print(type(text.unsafe_operation()))  # <class 'str'>
print(type(text.safe_operation()))    # <class '__main__.SafeStr'>
```

## Performance Optimization with __slots__
```python
from newtype import NewType

class MemoryEfficientStr(NewType(str)):
    __slots__ = ['_cached_value']

    def __init__(self, value: str):
        super().__init__()
        self._cached_value = None

    def compute_expensive(self):
        if self._cached_value is None:
            # Simulate expensive computation
            self._cached_value = self.upper() + self.lower()
        return self._cached_value

# Usage
text = MemoryEfficientStr("Hello")
print(text.compute_expensive())  # HELLOhello
print(text.compute_expensive())  # Uses cached value
```

## Custom Initialization with Validation
```python
from newtype import NewType
from typing import Union, Optional

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

# Usage
num = IntegerStr("42")
print(num.to_int())      # 42
hex_num = IntegerStr("2A", base=16)
print(hex_num.to_int(16))  # 42
try:
    IntegerStr("not a number")  # Raises ValueError
except ValueError as e:
    print(e)
