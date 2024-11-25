# Method Interception and Customization

This guide covers advanced techniques for intercepting and customizing method behavior in Python NewType.

## Basic Method Interception

The most straightforward way to intercept methods is by overriding them:

```python
from newtype import NewType

class TrackedList(NewType(list)):
    def __init__(self):
        super().__init__()
        self.operation_count = 0

    def append(self, item):
        self.operation_count += 1
        super().append(item)

    def extend(self, items):
        self.operation_count += 1
        super().extend(items)
```

## Advanced Method Interception

### Pre and Post Processing
```python
class ProcessedDict(NewType(dict)):
    def __setitem__(self, key, value):
        # Pre-processing
        processed_value = self._pre_process(value)

        # Call original method
        super().__setitem__(key, processed_value)

        # Post-processing
        self._post_process(key, processed_value)

    def _pre_process(self, value):
        if isinstance(value, str):
            return value.strip()
        return value

    def _post_process(self, key, value):
        print(f"Stored {key}={value}")
```

### Method Chaining
```python
class ChainableList(NewType(list)):
    def append(self, item):
        super().append(item)
        return self

    def extend(self, items):
        super().extend(items)
        return self

    def sort(self, *args, **kwargs):
        super().sort(*args, **kwargs)
        return self

# Usage
result = ChainableList().append(1).extend([2, 3]).sort()
```

## Special Method Interception

### Context Manager Methods
```python
class ManagedDict(NewType(dict)):
    def __enter__(self):
        print("Starting transaction")
        self._backup = dict(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print("Rolling back transaction")
            self.clear()
            self.update(self._backup)
        else:
            print("Committing transaction")
        del self._backup
        return False  # Don't suppress exceptions
```

### Iterator Methods
```python
class FilteredDict(NewType(dict)):
    def __iter__(self):
        return (k for k in super().__iter__() if not k.startswith('_'))

    def items(self):
        return ((k, v) for k, v in super().items() if not k.startswith('_'))

    def values(self):
        return (v for k, v in super().items() if not k.startswith('_'))
```

## Advanced Techniques

### Method Registration
```python
class InterceptedDict(NewType(dict)):
    _intercepted_methods = set()

    @classmethod
    def intercept(cls, method_name):
        cls._intercepted_methods.add(method_name)

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if name in self._intercepted_methods and callable(attr):
            def wrapper(*args, **kwargs):
                print(f"Calling {name}")
                return attr(*args, **kwargs)
            return wrapper
        return attr

# Usage
InterceptedDict.intercept('update')
InterceptedDict.intercept('clear')
```

### Dynamic Method Generation
```python
class DynamicDict(NewType(dict)):
    def __init__(self):
        super().__init__()
        self._create_convenience_methods()

    def _create_convenience_methods(self):
        for key in self:
            if isinstance(key, str) and key.isidentifier():
                setattr(self, f"get_{key}", lambda k=key: self[k])

# Usage
d = DynamicDict()
d["count"] = 42
print(d.get_count())  # 42
```

## Performance Considerations

### Method Caching
```python
from functools import lru_cache

class CachedDict(NewType(dict)):
    @lru_cache(maxsize=100)
    def get_or_default(self, key, default=None):
        return self.get(key, default)
```

### Lazy Evaluation
```python
class LazyDict(NewType(dict)):
    def __init__(self):
        super().__init__()
        self._computed_values = {}

    def __getitem__(self, key):
        if key in self._computed_values and callable(self._computed_values[key]):
            self[key] = self._computed_values[key]()
            del self._computed_values[key]
        return super().__getitem__(key)

    def set_lazy(self, key, compute_func):
        self._computed_values[key] = compute_func
```

## Best Practices

1. **Minimize Overhead**
   - Keep interception logic lightweight
   - Use `@newtype_exclude` for methods that don't need interception

2. **Preserve Method Signatures**
   - Maintain the same parameter signatures as the original methods
   - Use `*args, **kwargs` when necessary for flexibility

3. **Handle Exceptions Properly**
   - Decide whether to catch, transform, or propagate exceptions
   - Document exception handling behavior

4. **Document Intercepted Behavior**
   - Clearly document what methods are intercepted
   - Explain any side effects or changes in behavior

## Common Use Cases

### Validation
```python
class ValidatedList(NewType(list)):
    def __init__(self, validator=None):
        super().__init__()
        self.validator = validator or (lambda x: True)

    def append(self, item):
        if not self.validator(item):
            raise ValueError(f"Invalid item: {item}")
        super().append(item)

    def extend(self, items):
        if not all(self.validator(item) for item in items):
            raise ValueError("Invalid items in sequence")
        super().extend(items)
```

### Logging
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
```

### Metrics Collection
```python
from time import time

class MetricsDict(NewType(dict)):
    def __init__(self):
        super().__init__()
        self.metrics = {
            'get_count': 0,
            'set_count': 0,
            'total_get_time': 0,
            'total_set_time': 0
        }

    def __getitem__(self, key):
        start = time()
        result = super().__getitem__(key)
        self.metrics['get_count'] += 1
        self.metrics['total_get_time'] += time() - start
        return result

    def __setitem__(self, key, value):
        start = time()
        super().__setitem__(key, value)
        self.metrics['set_count'] += 1
        self.metrics['total_set_time'] += time() - start
```
