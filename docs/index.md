# python-newtype Documentation

Welcome to the python-newtype documentation! This library implements a powerful type system feature from type theory, allowing you to create true subtypes that maintain type consistency throughout method calls.

## Overview

python-newtype is unique in its implementation of the "new type" concept from type theory. The key feature is its ability to maintain subtype relationships through method calls and provide robust type validation. Here's a comprehensive example that showcases its main features:

```python
from newtype import NewType, newtype_exclude
import pytest
import re

class EmailStr(NewType(str)):

    def __init__(self, value: str):
        super().__init__(value)
        if '@' not in value:
            raise TypeError("`EmailStr` requires a '@' symbol within")
        self._local_part, self._domain_part = value.split('@')

    @newtype_exclude
    def __str__(self):
        return f"<Email - Local Part: {self.local_part}; Domain Part: {self.domain_part}>"

    @property
    def local_part(self):
        """Return the local part of the email address."""
        return self._local_part

    @property
    def domain_part(self):
        """Return the domain part of the email address."""
        return self._domain_part

    @property
    def full_email(self):
        """Return the full email address."""
        return str(self)

    @classmethod
    def from_string(cls, email: str):
        """Create an EmailStr instance from a string."""
        return cls(email)

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if the provided string is a valid email format."""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_regex, email) is not None

def test_emailstr_replace():
    """`EmailStr` uses `str.replace(..)` as its own method, returning an instance of `EmailStr`
    if the resultant `str` instance is a value `EmailStr`."""

    peter_email = EmailStr("peter@gmail.com")
    smith_email = EmailStr("smith@gmail.com")

    with pytest.raises(Exception):
        # this raises because `peter_email` is no longer an instance of `EmailStr`
        peter_email = peter_email.replace("peter@gmail.com", "petergmail.com")

    # this works because the entire email can be 'replaced'
    james_email = smith_email.replace("smith@gmail.com", "james@gmail.com")

    # comparison with `str` is built-in
    assert james_email == "james@gmail.com"

    # `james_email` is still an `EmailStr`
    assert isinstance(james_email, EmailStr)

    # this works because the local part can be 'replaced'
    jane_email = james_email.replace("james", "jane")

    # `jane_email` is still an `EmailStr`
    assert isinstance(jane_email, EmailStr)
    assert jane_email == "jane@gmail.com"

def test_emailstr_properties_methods():
    """Test the property, class method, and static method of EmailStr."""

    # Test property
    email = EmailStr("test@example.com")
    # `property` is not coerced to `EmailStr`
    assert email.full_email == "<Email - Local Part: test; Domain Part: example.com>"
    assert isinstance(email.full_email, str)
    # `property` is not coerced to `EmailStr`
    assert not isinstance(email.full_email, EmailStr)
    assert email.local_part == "test"
    assert email.domain_part == "example.com"

    # Test class method
    email_from_string = EmailStr.from_string("classmethod@example.com")
    # `property` is not coerced to `EmailStr`
    assert email_from_string.full_email == "<Email - Local Part: classmethod; Domain Part: example.com>"
    assert email_from_string.local_part == "classmethod"
    assert email_from_string.domain_part == "example.com"

    # Test static method
    assert EmailStr.is_valid_email("valid.email@example.com") is True
    assert EmailStr.is_valid_email("invalid-email.com") is False
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
