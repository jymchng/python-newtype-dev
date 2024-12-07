# python-newtype Documentation

Welcome to the python-newtype documentation! This library implements a powerful type system feature from type theory, allowing you to create true subtypes that maintain type consistency throughout method calls.

## Overview

python-newtype is unique in its implementation of the "new type" concept from type theory. The key feature is its ability to maintain subtype relationships through method calls and provide robust type validation. Here's a comprehensive example that showcases its main features:

```python
from functools import cached_property
from typing import Optional
from newtype import NewType

class EmailStr(NewType(str)):
    def __init__(self, value: str, strict: bool = True):
        if strict and "@" not in value:
            raise ValueError("Invalid email format")
        super().__init__(value)

    @property
    def domain(self) -> Optional[str]:
        if "@" in self:
            return self.split("@")[1]
        return None

    @cached_property
    def name(self) -> Optional[str]:
        if "@" in self:
            return self.split("@")[0]
        return None

    @staticmethod
    def from_str(s: str) -> "EmailStr":
        return EmailStr(s)

# Create a more specific email type
class Gmail(EmailStr):
    def __init__(self, value: str, strict: bool = True):
        if strict and "@gmail.com" not in value:
            raise ValueError("Invalid email format")
        super().__init__(value, strict)

# Usage examples
email = EmailStr("user@example.com")
assert email.domain == "example.com"  # Property access
assert email.name == "user"  # Cached property
assert isinstance(email, str)  # True - maintains str inheritance
assert isinstance(email, EmailStr)  # True - proper type checking

# Method chaining with type preservation
new_email = email.replace("user@example.com", "user1@example.com")
assert isinstance(new_email, EmailStr)  # Still an EmailStr!
assert new_email.name == "user1"

# Validation and inheritance
gmail = Gmail("hello@gmail.com")
assert gmail.domain == "gmail.com"
assert isinstance(gmail, EmailStr) # Although `from_str` returns `EmailStr`, which is the supertype, the subtype is not constructed

# Invalid inputs raise errors
try:
    EmailStr("invalid")  # Raises ValueError - missing @
except ValueError:
    pass

try:
    Gmail("user@example.com")  # Raises ValueError - not gmail.com
except ValueError:
    pass
```

## Key Features

### 1. True Subtype Preservation
- When a supertype method returns a value, python-newtype automatically instantiates a value of the subtype
- Type consistency is maintained throughout the entire chain of method calls
- All inherited methods maintain proper return types

### 2. Robust Type Validation
- Custom initialization with validation logic
- Support for strict and non-strict validation modes
- Proper inheritance of validation rules

### 3. Property and Method Support
- Full support for Python's property decorators
- Cached properties work seamlessly
- Static methods and class methods are preserved and are not modified

### 4. Type Safety and Inheritance
- Operations on subtypes never "leak" back to supertypes
- Behavioral subtyping with invariant maintenance
- Liskov Substitution Principle compliance

## More Examples

### Method Exclusion
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
assert isinstance(text.unsafe_operation(), str)      # Regular str
assert isinstance(text.safe_operation(), SafeStr)    # SafeStr
```

### Advanced Validation
```python
from typing import Union, Optional

class IntegerStr(NewType(str)):
    def __init__(self, value: Union[str, int], base: int = 10):
        if isinstance(value, int):
            value = str(value)
        try:
            int(value, base)
        except ValueError:
            raise ValueError(f"Value must be a valid integer in base {base}")
        super().__init__(value)

    def to_int(self, base: Optional[int] = None) -> int:
        return int(self, base or 10)

# Handle different number bases
num = IntegerStr("42")           # Decimal
hex_num = IntegerStr("2A", 16)   # Hexadecimal
print(hex_num.to_int(16))        # 42
```

## Getting Started

Check out our [Quick Start Guide](getting-started/quickstart.md) to begin using python-newtype in your projects.

## Installation

See the [Installation Guide](getting-started/installation.md) for detailed installation instructions.

## Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details on how to get involved.

## References

1. [Python Documentation on Subclassing](https://docs.python.org/3/extending/newtypes_tutorial.html#subclassing-other-types)
2. [MIT OpenCourseware 6.170 Lecture 14: Subtypes and Subclasses](https://ocw.mit.edu/courses/6-170-laboratory-in-software-engineering-fall-2005/9ed2c853eea2311adeadfcc0de284114_lec14.pdf)
3. [Nutype; Rust Crate](https://crates.io/crates/nutype)
