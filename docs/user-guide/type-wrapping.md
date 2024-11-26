# Type Wrapping

Type wrapping is a fundamental concept in python-newtype that allows you to create enhanced versions of existing types with additional functionality.

## Basic Type Wrapping

The most basic form of type wrapping involves creating a new type that inherits from an existing type:

```python
from newtype import NewType

# Create a wrapped string type
EnhancedStr = NewType(str)

# Create an instance
enhanced_text = EnhancedStr("Hello, World!")
```

## Adding Custom Functionality

You can add custom methods and properties to your wrapped types:

```python
class ValidatedString(NewType(str)):
    def is_email(self):
        return '@' in self and '.' in self.split('@')[1]

    def is_url(self):
        return self.startswith(('http://', 'https://'))

# Usage
email = ValidatedString("user@example.com")
assert email.is_email()
```

## Type Preservation

NewType preserves the original type's behavior while allowing extensions:

```python
class UpperStr(NewType(str)):
    def __str__(self):
        return super().__str__().upper()

text = UpperStr("hello")
assert str(text) == "HELLO"
assert text.lower() == "hello"  # Original string methods still work
```

## Working with Collections

You can wrap collection types like lists and dictionaries:

```python
class UniqueList(NewType(list)):
    def append(self, item):
        if item not in self:
            super().append(item)

unique = UniqueList([1, 2])
unique.append(2)  # Won't add duplicate
assert list(unique) == [1, 2]
```

## Type Checking

Wrapped types maintain proper type checking relationships:

```python
class IntList(NewType(list)):
    def append(self, item):
        if not isinstance(item, int):
            raise TypeError("Only integers allowed")
        super().append(item)

numbers = IntList()
numbers.append(42)  # OK
numbers.append("not a number")  # Raises TypeError
```

## Best Practices

1. **Keep It Simple**
   - Only add functionality that makes sense for the wrapped type
   - Avoid overcomplicating the interface

2. **Preserve Original Behavior**
   - Don't change the fundamental behavior of the wrapped type
   - Make sure all original methods still work as expected

3. **Document Extensions**
   - Clearly document any added functionality
   - Explain any changes to original behavior

4. **Use Type Hints**
   - Take advantage of Python's type hinting system
   - Help IDEs and type checkers understand your wrapped types

## Common Use Cases

### Validation
```python
class NonEmptyStr(NewType(str)):
    def __new__(cls, value):
        if not value:
            raise ValueError("String cannot be empty")
        return super().__new__(cls, value)
```

### Logging
```python
class LoggedList(NewType(list)):
    def append(self, item):
        print(f"Adding {item}")
        super().append(item)

    def remove(self, item):
        print(f"Removing {item}")
        super().remove(item)
```

### Default Values
```python
class DefaultDict(NewType(dict)):
    def __init__(self, default_value=None):
        super().__init__()
        self.default_value = default_value

    def __missing__(self, key):
        self[key] = self.default_value
        return self.default_value
```

## Advanced Topics

### Multiple Inheritance
```python
class Base:
    def extra_method(self):
        return "Extra functionality"

class EnhancedDict(NewType(dict), Base):
    pass

# Now has both dict methods and extra_method
```

### Generic Types
```python
from typing import TypeVar, Generic

T = TypeVar('T')

class TypedList(NewType(list), Generic[T]):
    def append(self, item: T):
        if not isinstance(item, T.__constraints__):
            raise TypeError(f"Expected {T}, got {type(item)}")
        super().append(item)
```

## Performance Considerations

1. **Wrapper Overhead**
   - Type wrapping adds a small performance overhead
   - Consider the impact in performance-critical code

2. **Memory Usage**
   - Wrapped types may use slightly more memory
   - Be mindful when working with large collections

3. **Method Call Overhead**
   - Each wrapped method call includes an extra lookup
   - Cache frequently accessed values when needed

## Debugging Tips

1. Use `dir()` to inspect wrapped types:
```python
wrapped = EnhancedStr("test")
print(dir(wrapped))  # Shows all available methods
```

2. Check type relationships:
```python
assert isinstance(wrapped, str)  # Original type
assert isinstance(wrapped, EnhancedStr)  # Wrapped type
```

3. Examine the method resolution order:
```python
print(EnhancedStr.__mro__)  # Shows inheritance chain
```
