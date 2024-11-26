# Basic Usage Guide

This guide covers the fundamental concepts and patterns for using `python-newtype` effectively.

## Core Concepts

### Type Wrapping

`python-newtype` allows you to extend existing Python types while preserving their original behavior. When you wrap a type:

1. All original methods are preserved and whenever it returns a value of the supertype, python-newtype will attempt to construct it as a value of the subtype
2. New methods can be added
3. Existing methods can be modified

```python
from newtype import NewType

class EnhancedStr(NewType(str)):
    def reverse(self):
        return self[::-1]

text = EnhancedStr("Hello")
print(text.reverse())    # "olleH"
print(text.upper())      # "HELLO" (original method)
print(len(text))         # 5 (original behavior)
```

### Method Inheritance

When you wrap a type, all methods from the original type are automatically available:

```python
class NumberList(NewType(list)):
    def sum(self):
        return sum(self)

numbers = NumberList([1, 2, 3])
print(numbers.sum())      # 6 (new method)
numbers.append(4)         # Original method works
print(numbers[0])        # 1 (original indexing works)
```

### Method Modification

You can modify existing methods by overriding them:

```python
class SafeDict(NewType(dict)):
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return None

d = SafeDict({'a': 1})
print(d['a'])    # 1
print(d['b'])    # None (instead of KeyError)
```

## Working with Special Methods

### Initialization

The `__init__` method can be customized while preserving the original type's initialization:

```python
class ValidatedList(NewType(list)):
    def __init__(self, *args, validator=None):
        super().__init__(*args)
        self.validator = validator or (lambda x: True)

    def append(self, item):
        if not self.validator(item):
            raise ValueError("Invalid item")
        super().append(item)

# Only allow numbers
numbers = ValidatedList(validator=lambda x: isinstance(x, (int, float)))
numbers.append(42)     # OK
numbers.append("42")   # Raises ValueError
```

### String Representation

You can customize how objects are displayed:

```python
class Person(NewType(object)):
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.name} ({self.age} years old)"

    def __repr__(self):
        return f"Person(name='{self.name}', age={self.age})"

person = Person("Alice", 30)
print(person)          # Alice (30 years old)
print(repr(person))    # Person(name='Alice', age=30)
```

## Attribute Handling

### Using __slots__

`python-newtype` properly handles classes with `__slots__`:

```python
class Point(NewType(object)):
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

point = Point(1, 2)
point.x = 3           # OK
point.z = 4           # Raises AttributeError
```

### Property Decorators

Properties work as expected:

```python
class Circle(NewType(object)):
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self):
        return 3.14159 * self._radius ** 2

circle = Circle(5)
print(circle.area)     # ~78.54
circle.radius = 10     # OK
circle.radius = -1     # Raises ValueError
```

## Best Practices

1. **Keep It Simple**
   - Only add methods that make sense for the type
   - Preserve the original type's behavior when possible

2. **Use Clear Names**
   - Class names should indicate the enhanced functionality
   - Method names should be descriptive

3. **Handle Errors Gracefully**
   - Use try/except when overriding methods
   - Provide meaningful error messages

4. **Document Your Changes**
   - Document new methods and modified behavior
   - Include examples in docstrings

5. **Test Thoroughly**
   - Test both new and inherited functionality
   - Test edge cases and error conditions
