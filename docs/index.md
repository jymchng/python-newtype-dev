# python-newtype Documentation

Welcome to the python-newtype documentation! This library implements a powerful type system feature from type theory, allowing you to create true subtypes that maintain type consistency throughout method calls.

## Overview

python-newtype is unique in its implementation of the "new type" concept from type theory. The key feature is its ability to maintain subtype relationships through method calls:

- When a supertype method returns a value of the supertype, python-newtype automatically instantiates a value of the subtype
- This ensures that operations on subtypes always return values of the subtype, not the supertype
- The type consistency is maintained throughout the entire chain of method calls

Here's a simple example to illustrate this behavior:

```python
from newtype import NewType

class PositiveInt(NewType(int)):
    def __init__(self, val):
        super().__init__()
        if val <= 0:
            raise ValueError("Value must be positive")

# Regular method calls maintain the subtype
x = PositiveInt(5)
y = x + 3  # y is automatically a PositiveInt(8), not just an int

# Even built-in methods return the subtype
z = x.bit_length()  # Returns PositiveInt, not int
```

## Key Features

### Automatic Subtype Preservation
```python
class SafeStr(NewType(str)):
    def __init__(self, val):
        super().__init__()
        if '<script>' in val.lower():
            raise ValueError("XSS attempt detected")

text = SafeStr("Hello, World!")
upper = text.upper()      # Returns SafeStr, not str
sliced = text[0:5]        # Returns SafeStr, not str
joined = " ".join([text]) # Returns SafeStr, not str
```

### Method Interception with Type Preservation
```python
class LoggedDict(NewType(dict)):
    def __setitem__(self, key, value):
        print(f"Setting {key} = {value}")
        result = super().__setitem__(key, value)
        # Any dict methods that return dict will return LoggedDict
        return result

d = LoggedDict({'a': 1})
d2 = d.copy()  # Returns LoggedDict, not dict
```

### Custom Initialization with Type Safety
```python
class ValidatedList(NewType(list)):
    def __init__(self, iterable=None, *, validator=None):
        super().__init__()
        self.validator = validator or (lambda x: True)
        if iterable:
            for item in iterable:
                self.append(item)

    def append(self, item):
        if not self.validator(item):
            raise ValueError(f"Invalid item: {item}")
        super().append(item)

    # Methods like extend, copy, etc. will return ValidatedList

numbers = ValidatedList(validator=lambda x: isinstance(x, int))
numbers.append(42)      # OK
filtered = filter(lambda x: x > 20, numbers)  # Result maintains ValidatedList type
```

## Type Theory Implementation

python-newtype implements the theoretical concept that if `S` is a subtype of `T`, then any operation that returns a value of type `T` should return a value of type `S` when applied to values of type `S`. This ensures:

1. **Type Safety**: Operations on subtypes never "leak" back to supertypes
2. **Behavioral Subtyping**: Subtypes maintain their invariants through all operations
3. **Liskov Substitution**: Subtypes can be used anywhere their supertypes are expected
4. **Method Consistency**: All inherited methods maintain proper return types

## Getting Started

Check out our [Quick Start Guide](getting-started/quickstart.md) to begin using python-newtype in your projects.

## Installation

See the [Installation Guide](getting-started/installation.md) for detailed installation instructions.

## Contributing

We welcome contributions! See our [Contributing Guide](development/contributing.md) for details on how to get involved.
