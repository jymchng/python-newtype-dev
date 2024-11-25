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
