# Python NewType Documentation

Welcome to the Python NewType documentation! This library provides a powerful mechanism for extending existing Python types with additional functionality while preserving their original behavior.

## Overview

Python NewType allows you to create enhanced versions of existing Python types by wrapping them with additional functionality. This is particularly useful when you need to:

- Add new methods to existing types
- Modify or intercept existing method calls
- Control object initialization
- Preserve both `__dict__` and `__slots__` attributes
- Handle method calls with special processing requirements

## Key Features

### Type Wrapping
```python
from newtype import NewType

class EnhancedStr(NewType(str)):
    def reverse(self):
        return self[::-1]

text = EnhancedStr("Hello")
print(text.reverse())  # "olleH"
print(text.upper())    # "HELLO" (original str methods still work)
```

### Method Interception
```python
class LoggedDict(NewType(dict)):
    def __setitem__(self, key, value):
        print(f"Setting {key} = {value}")
        return super().__setitem__(key, value)

d = LoggedDict()
d["key"] = "value"  # Prints: Setting key = value
```

### Custom Initialization
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

numbers = ValidatedList(validator=lambda x: isinstance(x, int))
numbers.append(42)      # OK
numbers.append("text")  # Raises ValueError
```

## Getting Started

Check out our [Quick Start Guide](getting-started/quickstart.md) to begin using Python NewType in your projects.

## Installation

See the [Installation Guide](getting-started/installation.md) for detailed installation instructions.

## Contributing

We welcome contributions! See our [Contributing Guide](development/contributing.md) for details on how to get involved.