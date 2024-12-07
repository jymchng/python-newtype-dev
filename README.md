<div align="center">

# python-newtype

## Documentation
<a href="https://spyt.asyncmove.com">
  <img src="https://img.shields.io/badge/docs-passing-brightgreen.svg" width="100" alt="docs passing">
</a>

### Compatibility and Version
<img src="https://img.shields.io/badge/%3E=python-3.8-blue.svg" alt="Python compat">
<a href="https://pypi.python.org/pypi/python-newtype-dev"><img src="https://img.shields.io/pypi/v/python-newtype-dev.svg" alt="PyPi"></a>

### CI/CD
<a href="https://github.com/jymchng/python-newtype-dev/actions?query=workflow%3Atests"><img src="https://github.com/jymchng/python-newtype-dev/actions/workflows/tests.yaml/badge.svg?branch=main" alt="GHA Status"></a>
<a href="https://codecov.io/github/jymchng/python-newtype-dev?branch=main"><img src="https://codecov.io/github/jymchng/python-newtype-dev/coverage.svg?branch=main" alt="Coverage"></a>

### License and Issues
<a href="https://github.com/jymchng/python-newtype-dev/blob/main/LICENSE"><img src="https://img.shields.io/github/license/jymchng/python-newtype-dev" alt="License"></a>
<a href="https://github.com/jymchng/python-newtype-dev/issues"><img src="https://img.shields.io/github/issues/jymchng/python-newtype-dev" alt="Issues"></a>
<a href="https://github.com/jymchng/python-newtype-dev/issues?q=is%3Aissue+is%3Aclosed"><img src="https://img.shields.io/github/issues-closed/jymchng/python-newtype-dev" alt="Closed Issues"></a>
<a href="https://github.com/jymchng/python-newtype-dev/issues?q=is%3Aissue+is%3Aopen"><img src="https://img.shields.io/github/issues-raw/jymchng/python-newtype-dev" alt="Open Issues"></a>

### Development and Quality
<a href="https://github.com/jymchng/python-newtype-dev/network/members"><img src="https://img.shields.io/github/forks/jymchng/python-newtype-dev" alt="Forks"></a>
<a href="https://github.com/jymchng/python-newtype-dev/stargazers"><img src="https://img.shields.io/github/stars/jymchng/python-newtype-dev" alt="Stars"></a>
<a href="https://pypi.python.org/pypi/python-newtype-dev"><img src="https://img.shields.io/pypi/dm/python-newtype-dev" alt="Downloads"></a>
<a href="https://github.com/jymchng/python-newtype-dev/graphs/contributors"><img src="https://img.shields.io/github/contributors/jymchng/python-newtype-dev" alt="Contributors"></a>
<a href="https://github.com/jymchng/python-newtype-dev/commits/main"><img src="https://img.shields.io/github/commit-activity/m/jymchng/python-newtype-dev" alt="Commits"></a>
<a href="https://github.com/jymchng/python-newtype-dev/commits/main"><img src="https://img.shields.io/github/last-commit/jymchng/python-newtype-dev" alt="Last Commit"></a>
<a href="https://github.com/jymchng/python-newtype-dev"><img src="https://img.shields.io/github/languages/code-size/jymchng/python-newtype-dev" alt="Code Size"></a>
<a href="https://github.com/jymchng/python-newtype-dev"><img src="https://img.shields.io/github/repo-size/jymchng/python-newtype-dev" alt="Repo Size"></a>
<a href="https://github.com/jymchng/python-newtype-dev/watchers"><img src="https://img.shields.io/github/watchers/jymchng/python-newtype-dev" alt="Watchers"></a>
<a href="https://github.com/jymchng/python-newtype-dev"><img src="https://img.shields.io/github/commit-activity/y/jymchng/python-newtype-dev" alt="Activity"></a>
<a href="https://github.com/jymchng/python-newtype-dev/pulls"><img src="https://img.shields.io/github/issues-pr/jymchng/python-newtype-dev" alt="PRs"></a>
<a href="https://github.com/jymchng/python-newtype-dev/pulls?q=is%3Apr+is%3Aclosed"><img src="https://img.shields.io/github/issues-pr-closed/jymchng/python-newtype-dev" alt="Merged PRs"></a>
<a href="https://github.com/jymchng/python-newtype-dev/pulls?q=is%3Apr+is%3Aopen"><img src="https://img.shields.io/github/issues-pr/open/jymchng/python-newtype-dev" alt="Open PRs"></a>

</div>

A powerful Python library for extending existing types with additional functionality while preserving their original behavior, type information and subtype invariances.

## Features

- **Type Wrapping**: Seamlessly wrap existing Python types with new functionality and preservation of subtype invariances when using methods of supertype
- **Custom Initialization**: Control object initialization with special handling
- **Attribute Preservation**: Maintains both `__dict__` and `__slots__` attributes
- **Memory Efficient**: Uses weak references for caching
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

For detailed documentation, visit [py-nt.asyncmove.com](https://py-nt.asyncmove.com/).

### Key Topics:
- [Installation Guide](https://py-nt.asyncmove.com/getting-started/installation/)
- [Quick Start Guide](https://py-nt.asyncmove.com/getting-started/quickstart/)
- [User Guide](https://py-nt.asyncmove.com/user-guide/basic-usage/)
- [API Reference](https://py-nt.asyncmove.com/api/newtype/)

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

### Install from Source

```bash
git clone https://github.com/jymchng/python-newtype-dev.git
cd python-newtype-dev
make install
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

We welcome contributions! Please see our [Contributing Guide](https://py-nt.asyncmove.com/development/contributing/) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Special thanks to all contributors who have helped shape this project.
