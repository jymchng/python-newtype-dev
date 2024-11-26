# Examples

This guide provides practical examples of using python-newtype in various scenarios.

## Basic Examples

### Enhanced String Type

```python
from newtype import NewType

class EnhancedStr(NewType(str)):
    def reverse(self):
        return self[::-1]

    def count_words(self):
        return len(self.split())

    def is_palindrome(self):
        s = ''.join(c.lower() for c in self if c.isalnum())
        return s == s[::-1]

# Usage
text = EnhancedStr("A man a plan a canal Panama")
print(text.is_palindrome())  # True
print(text.count_words())    # 6
print(text.reverse())        # "amanaP lanac a nalp a nam A"
```

### Validated List

```python
class IntList(NewType(list)):
    def append(self, item):
        if not isinstance(item, int):
            raise TypeError("Only integers allowed")
        super().append(item)

    def extend(self, items):
        if not all(isinstance(x, int) for x in items):
            raise TypeError("All items must be integers")
        super().extend(items)

# Usage
numbers = IntList([1, 2, 3])
numbers.append(4)           # OK
numbers.extend([5, 6, 7])  # OK
try:
    numbers.append("8")     # Raises TypeError
except TypeError:
    print("String not allowed")
```

### Cached Dictionary

```python
from functools import lru_cache

class CachedDict(NewType(dict)):
    @lru_cache(maxsize=100)
    def get_or_default(self, key, default=None):
        return self.get(key, default)

# Usage
cache = CachedDict({'a': 1, 'b': 2})
result1 = cache.get_or_default('a', 0)  # Cache miss
result2 = cache.get_or_default('a', 0)  # Cache hit
```

## Advanced Examples

### Context Manager Support

```python
class TransactionalDict(NewType(dict)):
    def __enter__(self):
        self._backup = dict(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.clear()
            self.update(self._backup)
        return False

# Usage
d = TransactionalDict({'key': 'value'})
try:
    with d:
        d['key'] = 'new_value'
        raise ValueError("Something went wrong")
except ValueError:
    print(d['key'])  # Prints: value (rolled back)
```

### Custom Iteration

```python
class FilteredDict(NewType(dict)):
    def __iter__(self):
        return (k for k in super().__iter__() if not k.startswith('_'))

    def items(self):
        return ((k, v) for k, v in super().items() if not k.startswith('_'))

    def values(self):
        return (v for k, v in super().items() if not k.startswith('_'))

# Usage
d = FilteredDict({'a': 1, '_b': 2, 'c': 3})
print(list(d))  # ['a', 'c']
```

### Logging Support

```python
import logging

class LoggedDict(NewType(dict)):
    def __init__(self, logger=None):
        super().__init__()
        self.logger = logger or logging.getLogger(__name__)

    def __setitem__(self, key, value):
        self.logger.info(f"Setting {key}={value}")
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self.logger.info(f"Deleting {key}")
        super().__delitem__(key)

# Usage
logging.basicConfig(level=logging.INFO)
d = LoggedDict()
d['key'] = 'value'  # Logs: Setting key=value
del d['key']        # Logs: Deleting key
```

### Type Validation

```python
class SchemaDict(NewType(dict)):
    def __init__(self, schema=None):
        super().__init__()
        self.schema = schema or {}

    def __setitem__(self, key, value):
        if key in self.schema:
            expected_type = self.schema[key]
            if not isinstance(value, expected_type):
                raise TypeError(f"Expected {expected_type}")
        super().__setitem__(key, value)

# Usage
schema = {'name': str, 'age': int}
d = SchemaDict(schema)
d['name'] = "John"    # OK
d['age'] = 30        # OK
try:
    d['age'] = "30"  # Raises TypeError
except TypeError:
    print("Invalid type")
```

### Performance Monitoring

```python
from time import time

class MetricsDict(NewType(dict)):
    def __init__(self):
        super().__init__()
        self.metrics = {
            'gets': 0,
            'sets': 0,
            'get_time': 0,
            'set_time': 0
        }

    def __getitem__(self, key):
        start = time()
        result = super().__getitem__(key)
        self.metrics['get_time'] += time() - start
        self.metrics['gets'] += 1
        return result

    def __setitem__(self, key, value):
        start = time()
        super().__setitem__(key, value)
        self.metrics['set_time'] += time() - start
        self.metrics['sets'] += 1

# Usage
d = MetricsDict()
for i in range(1000):
    d[i] = i
    _ = d[i]
print(f"Average get time: {d.metrics['get_time'] / d.metrics['gets']:.6f}s")
print(f"Average set time: {d.metrics['set_time'] / d.metrics['sets']:.6f}s")
```

## Real-World Examples

### Configuration Management

```python
import os
import json

class ConfigDict(NewType(dict)):
    @classmethod
    def from_env(cls, prefix='APP_'):
        instance = cls()
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                instance[config_key] = value
        return instance

    @classmethod
    def from_json(cls, filename):
        with open(filename) as f:
            return cls(json.load(f))

    def to_env(self, prefix='APP_'):
        for key, value in self.items():
            os.environ[f"{prefix}{key.upper()}"] = str(value)

# Usage
config = ConfigDict.from_json('config.json')
config.to_env('MY_APP_')
```

### Data Validation

```python
import re

class ValidatedDict(NewType(dict)):
    def __init__(self, schema):
        super().__init__()
        self.schema = schema

    def __setitem__(self, key, value):
        if key in self.schema:
            rules = self.schema[key]
            if not isinstance(value, rules['type']):
                raise TypeError(f"Expected {rules['type']}")
            if 'pattern' in rules and isinstance(value, str):
                if not re.match(rules['pattern'], value):
                    raise ValueError(f"Invalid format for {key}")
        super().__setitem__(key, value)

# Usage
schema = {
    'email': {'type': str, 'pattern': r'^[\w\.-]+@[\w\.-]+\.\w+$'},
    'age': {'type': int},
}
data = ValidatedDict(schema)
data['email'] = 'user@example.com'  # OK
data['age'] = 25                    # OK
```

These examples demonstrate various ways to extend built-in Python types using NewType. Each example includes practical use cases and common patterns you might encounter in real-world applications.
