<div align="center">

# python-newtype

## Documentation
<a href="https://py-nt.asyncmove.com">
  <img src="https://img.shields.io/badge/docs-passing-brightgreen.svg" width="100" alt="docs passing">
</a>

### Compatibility and Version
<img src="https://img.shields.io/badge/%3E=python-3.8-blue.svg" alt="Python compat">
<a href="https://pypi.python.org/pypi/python-newtype"><img src="https://img.shields.io/pypi/v/python-newtype.svg" alt="PyPi"></a>

### CI/CD
<a href="https://codecov.io/github/jymchng/python-newtype-dev?branch=main"><img src="https://codecov.io/github/jymchng/python-newtype-dev/coverage.svg?branch=main" alt="Coverage"></a>

### License and Issues
<a href="https://github.com/jymchng/python-newtype-dev/blob/main/LICENSE"><img src="https://img.shields.io/github/license/jymchng/python-newtype-dev" alt="License"></a>
<a href="https://github.com/jymchng/python-newtype-dev/issues"><img src="https://img.shields.io/github/issues/jymchng/python-newtype-dev" alt="Issues"></a>
<a href="https://github.com/jymchng/python-newtype-dev/issues?q=is%3Aissue+is%3Aclosed"><img src="https://img.shields.io/github/issues-closed/jymchng/python-newtype-dev" alt="Closed Issues"></a>
<a href="https://github.com/jymchng/python-newtype-dev/issues?q=is%3Aissue+is%3Aopen"><img src="https://img.shields.io/github/issues-raw/jymchng/python-newtype-dev" alt="Open Issues"></a>

### Development and Quality
<a href="https://github.com/jymchng/python-newtype-dev/network/members"><img src="https://img.shields.io/github/forks/jymchng/python-newtype-dev" alt="Forks"></a>
<a href="https://github.com/jymchng/python-newtype-dev/stargazers"><img src="https://img.shields.io/github/stars/jymchng/python-newtype-dev" alt="Stars"></a>
<a href="https://pypi.python.org/pypi/python-newtype"><img src="https://img.shields.io/pypi/dm/python-newtype" alt="Downloads"></a>
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
import pytest
import re
from newtype import NewType, newtype_exclude


class EmailStr(NewType(str)):
    # you can define `__slots__` to save space
    __slots__ = (
        '_local_part',
        '_domain_part',
    )

    def __init__(self, value: str):
        super().__init__()
        if "@" not in value:
            raise TypeError("`EmailStr` requires a '@' symbol within")
        self._local_part, self._domain_part = value.split("@")

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
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_regex, email) is not None


def test_emailstr_replace():
    """`EmailStr` uses `str.replace(..)` as its own method, returning an instance of `EmailStr`
    if the resultant `str` instance is a value `EmailStr`.
    """
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
    assert (
        email_from_string.full_email
        == "<Email - Local Part: classmethod; Domain Part: example.com>"
    )
    assert email_from_string.local_part == "classmethod"
    assert email_from_string.domain_part == "example.com"

    # Test static method
    assert EmailStr.is_valid_email("valid.email@example.com") is True
    assert EmailStr.is_valid_email("invalid-email.com") is False


def test_email_str__slots__():
    email = EmailStr("test@example.com")

    with pytest.raises(AttributeError):
        email.hi = "bye"
        assert email.hi == "bye"
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
  make install-dev-deps
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
