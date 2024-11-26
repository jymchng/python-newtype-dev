# Quick Start Guide

This guide will help you get started with python-newtype quickly. We'll cover basic usage and common patterns.

## Basic Usage

### Simple Type Extension

```python
from newtype import NewType

# Create an enhanced string type
class EnhancedStr(NewType(str)):
    def reverse(self):
        return self[::-1]

    def count_words(self):
        return len(self.split())

# Use the enhanced type
text = EnhancedStr("Hello World")
print(text.reverse())        # "dlroW olleH"
print(text.count_words())    # 2
print(text.upper())         # "HELLO WORLD" (original methods work)
```

### Method Interception

```python
class LoggedList(NewType(list)):
    def append(self, item):
        print(f"Adding item: {item}")
        super().append(item)

    def pop(self, index=-1):
        item = super().pop(index)
        print(f"Removed item: {item}")
        return item

# Use the logged list
logged = LoggedList([1, 2, 3])
logged.append(4)    # Prints: Adding item: 4
logged.pop()        # Prints: Removed item: 4
```

### Custom Initialization

```python
class TypedList(NewType(list)):
    def __init__(self, item_type, items=None):
        super().__init__()
        self.item_type = item_type
        if items:
            for item in items:
                self.append(item)

    def append(self, item):
        if not isinstance(item, self.item_type):
            raise TypeError(f"Expected {self.item_type}, got {type(item)}")
        super().append(item)

# Use the typed list
numbers = TypedList(int, [1, 2, 3])
numbers.append(4)       # OK
numbers.append("5")     # Raises TypeError
```

### Async Support

```python
import asyncio
from newtype import NewType

class AsyncList(NewType(list)):
    async def async_append(self, item):
        await asyncio.sleep(0.1)  # Simulate async operation
        self.append(item)

    async def async_pop(self):
        await asyncio.sleep(0.1)  # Simulate async operation
        return self.pop()

# Use async methods
async def main():
    async_list = AsyncList()
    await async_list.async_append(1)
    item = await async_list.async_pop()
    print(item)  # 1

asyncio.run(main())
```

### Excluding Methods from Wrapping

```python
from newtype import NewType, newtype_exclude

class CustomDict(NewType(dict)):
    @newtype_exclude
    def clear(self):
        print("Clear operation not allowed")
        return None

d = CustomDict({'a': 1})
d.clear()  # Prints: Clear operation not allowed
```

## Advanced Features

### Using with Slots

```python
class Point(NewType(object)):
    __slots__ = ('x', 'y')

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

p = Point(3, 4)
print(p.distance())  # 5.0
```

### Debug Support

```python
# Enable debug printing during development
import logging
logging.basicConfig(level=logging.DEBUG)

class DebugDict(NewType(dict)):
    def __setitem__(self, key, value):
        # Debug messages will be printed
        super().__setitem__(key, value)

d = DebugDict()
d['key'] = 'value'
```

## Next Steps

- Read the [User Guide](../user-guide/basic-usage.md) for more detailed information
- Check the [API Reference](../api/newtype.md) for complete API documentation
- See [Examples](../user-guide/examples.md) for more usage patterns
