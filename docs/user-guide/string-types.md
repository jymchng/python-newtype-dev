# String Type Extensions

This guide demonstrates how to extend Python's built-in string type using NewType to create specialized string classes with validation and additional functionality.

## Basic String Extension

The simplest way to extend the string type is to add custom methods while maintaining all the original string functionality:

```python
from newtype import NewType

class EnhancedString(NewType(str)):
    def reverse(self):
        return self[::-1]

    def word_count(self):
        return len(self.split())

    def is_palindrome(self):
        s = ''.join(c.lower() for c in self if c.isalnum())
        return s == s[::-1]

# Usage
text = EnhancedString("A man a plan a canal Panama")
print(text.is_palindrome())  # True
print(text.word_count())     # 6
print(text.reverse())        # "amanaP lanac a nalp a nam A"
```

## Validated String Types

### National ID (NRIC)

Here's an example of creating a validated National Registration Identity Card (NRIC) type:

```python
class NRIC(NewType(str)):
    country = "SG"  # Class attribute for country code

    def __init__(self, val: str, metadata: any):
        super().__init__(val)
        self.__validate__(val)  # Validate on initialization
        self._prefix = val[0]
        self._suffix = val[-1]
        self._digits = val[1:-1]
        self.metadata = metadata

    @staticmethod
    def __validate__(nric: str):
        # Validation rules for Singapore NRIC
        assert len(nric) == 9, f"NRIC length must be 9, got {len(nric)}"
        assert nric[0] in ["S", "T", "G", "F", "M"], f"Invalid prefix: {nric[0]}"
        # Additional checksum validation can be implemented here

    def __str__(self):
        return f"NRIC(Prefix:{self._prefix}, Suffix:{self._suffix}, Digits:{self._digits})"

# Usage
nric = NRIC("S1234567D", metadata={"issued_date": "2023-01-01"})
print(nric)  # NRIC(Prefix:S, Suffix:D, Digits:1234567)
print(nric.metadata)  # {'issued_date': '2023-01-01'}
```

### Email Address

A validated email address type with format checking:

```python
import re

class Email(NewType(str)):
    def __init__(self, val: str):
        super().__init__(val)
        self.__validate__(val)

    @staticmethod
    def __validate__(val: str):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(pattern, val):
            raise ValueError(f"Invalid email format: {val}")

# Usage
email = Email("user@example.com")  # Valid
try:
    invalid_email = Email("not.an.email")  # Raises ValueError
except ValueError as e:
    print(e)  # Invalid email format: not.an.email
```

### Phone Number

A phone number type with formatting and validation:

```python
class PhoneNumber(NewType(str)):
    def __init__(self, val: str):
        # Remove any spaces or dashes
        val = ''.join(c for c in val if c.isdigit())
        super().__init__(val)
        self.__validate__(val)

    @staticmethod
    def __validate__(val: str):
        # Basic validation for length
        if not (8 <= len(val) <= 15):
            raise ValueError("Phone number must be between 8 and 15 digits")
        if not val.isdigit():
            raise ValueError("Phone number must contain only digits")

    def format(self, country_code=None):
        num = self
        if country_code:
            num = f"+{country_code}{self}"
        return '-'.join([num[:3], num[3:6], num[6:]])

# Usage
phone = PhoneNumber("1234567890")
print(phone.format())          # 123-456-7890
print(phone.format(1))         # +1-123-456-7890
```

### Social Security Number (SSN)

A US Social Security Number type with proper formatting and validation:

```python
class SSN(NewType(str)):
    def __init__(self, val: str):
        # Remove any dashes or spaces
        val = ''.join(c for c in val if c.isdigit())
        super().__init__(val)
        self.__validate__(val)

    @staticmethod
    def __validate__(val: str):
        if len(val) != 9:
            raise ValueError("SSN must be 9 digits")
        if not val.isdigit():
            raise ValueError("SSN must contain only digits")
        if val.startswith('000'):
            raise ValueError("SSN cannot start with 000")

    def format(self):
        return f"{self[:3]}-{self[3:5]}-{self[5:]}"

    def mask(self):
        return f"XXX-XX-{self[5:]}"

# Usage
ssn = SSN("123456789")
print(ssn.format())  # 123-45-6789
print(ssn.mask())    # XXX-XX-6789
```

## Blockchain Addresses

Example of a specialized string type for blockchain addresses:

```python
class BlockchainAddress(NewType(str)):
    is_blockchain_address = True

    @classmethod
    def __newtype__(cls, val: str):
        cls._validate_address(val)
        return val

    @staticmethod
    def _validate_address(val: str):
        if not val.startswith('0x'):
            raise ValueError("Address must start with '0x'")
        if len(val) != 42:  # 0x + 40 hex chars
            raise ValueError("Address must be 42 characters long")
        if not all(c in '0123456789abcdefABCDEF' for c in val[2:]):
            raise ValueError("Address must be hexadecimal")

class EthereumAddress(BlockchainAddress):
    def __init__(self, val: str, is_checksum: bool = False):
        super().__init__(val)
        self._is_checksum = is_checksum

    @property
    def is_checksum(self):
        return self._is_checksum

# Usage
addr = EthereumAddress("0x742d35Cc6634C0532925a3b844Bc454e4438f44e", is_checksum=True)
print(addr.is_blockchain_address)  # True
print(addr.is_checksum)           # True
```

## Custom String with Additional Attributes

Example of a string type that can hold additional attributes:

```python
class CustomString(NewType(str)):
    def __init__(self, val: str, *args, **kwargs):
        super().__init__(val)
        self.args = args
        self.kwargs = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def custom_method(self):
        return f"String value: {self}, Args: {self.args}, Kwargs: {self.kwargs}"

# Example subclasses
class SerialNumber(CustomString):
    pass

class PassportNumber(CustomString):
    pass

class LicensePlate(CustomString):
    pass

# Usage
serial = SerialNumber("ABC123", manufacturer="ACME", year=2023)
print(serial.manufacturer)  # "ACME"
print(serial.year)         # 2023
print(serial.custom_method())  
# "String value: ABC123, Args: (), Kwargs: {'manufacturer': 'ACME', 'year': 2023}"
```

## Best Practices

When extending string types with NewType:

1. Always validate input in `__init__` or `__newtype__` methods
2. Use properties instead of direct attribute access when appropriate
3. Implement `__str__` and `__repr__` for better debugging
4. Keep validation logic in separate methods for better organization
5. Use static methods for validation when the logic doesn't need instance access
6. Consider implementing custom formatting methods for different display needs
7. Add type hints for better IDE support and code clarity

## Common Patterns

1. **Validation on Initialization**: Validate the string format when the object is created
2. **Custom Formatting**: Add methods to format the string in different ways
3. **Metadata Storage**: Store additional information along with the string value
4. **Type-Specific Operations**: Add methods that make sense for the specific type
5. **Immutability**: Ensure that the string value cannot be modified after creation
6. **String Operations**: Override string operations when needed (e.g., upper(), lower())
7. **Format Cleaning**: Remove unwanted characters or normalize format on initialization
