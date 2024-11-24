# Python NewType

[![PyPI version](https://badge.fury.io/py/python-newtype.svg)](https://badge.fury.io/py/python-newtype)
[![Python Versions](https://img.shields.io/pypi/pyversions/python-newtype.svg)](https://pypi.org/project/python-newtype/)
[![Documentation Status](https://readthedocs.org/projects/python-newtype/badge/?version=latest)](https://python-newtype.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python library for extending existing types with additional functionality while preserving their original behavior.

## Features

- **Type Wrapping**: Seamlessly wrap existing Python types with new functionality
- **Method Interception**: Intercept and modify method calls with custom processing
- **Custom Initialization**: Control object initialization with special handling
- **Attribute Preservation**: Maintains both `__dict__` and `__slots__` attributes
- **Memory Efficient**: Uses weak references for caching to prevent memory leaks
- **Debug Support**: Built-in debug printing capabilities for development
- **Async Support**: Full support for asynchronous methods and operations

## Quick Start

### Installation

```bash
pip install python-newtype
```

### Basic Usage

```python
from newtype import NewType

# Create a wrapped string type with additional functionality
class EnhancedStr(NewType(str)):
    def reverse(self):
        return self[::-1]
    
    def count_words(self):
        return len(self.split())

# Use the enhanced type
text = EnhancedStr("Hello World")
print(text.reverse())        # "dlroW olleH"
print(text.count_words())    # 2

# Original string methods still work
print(text.upper())         # "HELLO WORLD"
print(text.split())         # ["Hello", "World"]
```

## Documentation

For detailed documentation, visit [python-newtype.readthedocs.io](https://python-newtype.readthedocs.io/).

### Key Topics:
- [Installation Guide](https://python-newtype.readthedocs.io/en/latest/getting-started/installation/)
- [Quick Start Guide](https://python-newtype.readthedocs.io/en/latest/getting-started/quickstart/)
- [User Guide](https://python-newtype.readthedocs.io/en/latest/user-guide/basic-usage/)
- [API Reference](https://python-newtype.readthedocs.io/en/latest/api/newtype/)

## Development

### Prerequisites

- Python 3.8 or higher
- C compiler (for building extensions)
- Development packages:
  ```bash
  pip install -e ".[dev]"
  ```

### Building from Source

```bash
git clone https://github.com/jymchng/python-newtype-dev.git
cd python-newtype-dev
make build
```

### Running Tests

```bash
# Run all tests
make test

# Run with debug output
make test-debug

# Run specific test suite
make test-custom
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](https://python-newtype.readthedocs.io/en/latest/development/contributing/) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Special thanks to all contributors who have helped shape this project.