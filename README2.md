# Python NewType

A Python library that provides a powerful type wrapping mechanism for extending existing Python types with additional functionality while preserving their original behavior.

## Overview

Python NewType is a library that allows you to create enhanced versions of existing Python types by wrapping them with additional functionality. It's particularly useful when you need to:

- Add new methods or modify existing ones while maintaining the original type's behavior
- Intercept and modify object initialization
- Preserve both `__dict__` and `__slots__` attributes during type wrapping
- Handle method calls with special processing requirements

## Features

- **Type Wrapping**: Easily wrap existing Python types with new functionality
- **Method Interception**: Intercept and modify method calls using `NewTypeMethod`
- **Initialization Control**: Custom initialization handling through `NewTypeInit`
- **Attribute Preservation**: Maintains both `__dict__` and `__slots__` attributes
- **Caching Support**: Includes caching mechanism for wrapped types
- **Method Exclusion**: Ability to exclude specific methods from wrapping using `@newtype_exclude`
- **Debug Support**: Built-in debug printing capabilities for development

## Installation

```bash
pip install -r requirements.txt
```

### Requirements

- Python 3.x
- pandas >= 2
- pytest >= 3.2
- setuptools >= 72.1.0
- pytest-asyncio
- pytest-memray
- typing_extensions

## Usage

### Basic Example

```python
from newtype import NewType

# Create a wrapped version of an existing type
class MyStr(NewType(str)):
    def custom_method(self):
        return f"Custom processing of: {self}"

# Use the wrapped type
my_string = MyStr("Hello World")
result = my_string.custom_method()  # "Custom processing of: Hello World"
```

### Excluding Methods from Wrapping

```python
from newtype import NewType, newtype_exclude

class MyCustomType(NewType(str)):
    @newtype_exclude
    def excluded_method(self):
        # This method won't be wrapped
        pass
```

## Development

### Building from Source

```bash
python -m setup clean --all
python -m setup build_ext --inplace
```

### Running Tests

```bash
# Run all tests
python -m pytest . -s -vv

# Run specific test file
python -m pytest test_custom_type.py -s -vv
```

### Debug Mode

To enable debug printing during development:

```bash
python -m setup build_ext --inplace -D__DEBUG_PRINT__
```

## Project Structure

- `newtype.py`: Core implementation of the NewType functionality
- `newtype_meth.c`: C extension for method wrapping
- `newtype_init.c`: C extension for initialization handling
- `test_*.py`: Comprehensive test suite
- `setup.py`: Build configuration for C extensions

## Testing

The project includes a comprehensive test suite covering:

- Custom type wrapping
- Async functionality
- Method exclusion
- Initialization handling
- String type operations
- Slots support
- Memory leak tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the test suite
5. Submit a pull request

## License

[License information to be added]

## Notes

- The library uses weak references for caching to prevent memory leaks
- Debug logging can be configured through standard Python logging mechanisms
- C extensions are used for performance-critical operations