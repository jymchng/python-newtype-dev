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

## Getting Started

Check out our [Quick Start Guide](getting-started/quickstart.md) to begin using python-newtype in your projects.

## Installation

See the [Installation Guide](getting-started/installation.md) for detailed installation instructions.

## Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details on how to get involved.
