# Custom Initialization

This guide covers advanced techniques for customizing the initialization of wrapped types in python-newtype.

## Basic Initialization

The most basic form of initialization involves calling the parent class's `__init__`:

```python
from newtype import NewType

class ConfigDict(NewType(dict)):
    def __init__(self):
        super().__init__()
        self.modified = False
```

## Constructor Arguments

You can add custom arguments to your wrapped type's constructor:

```python
class ValidatedDict(NewType(dict)):
    def __init__(self, validator=None, *, strict=True):
        super().__init__()
        self.validator = validator or (lambda k, v: True)
        self.strict = strict

    def __setitem__(self, key, value):
        if not self.validator(key, value):
            if self.strict:
                raise ValueError(f"Invalid key-value pair: {key}={value}")
            return
        super().__setitem__(key, value)
```

## Factory Methods

Create alternative constructors using class methods:

```python
class EnhancedList(NewType(list)):
    @classmethod
    def from_file(cls, filename):
        with open(filename) as f:
            items = [line.strip() for line in f]
        return cls(items)

    @classmethod
    def range(cls, *args):
        return cls(range(*args))

# Usage
numbers = EnhancedList.range(1, 5)
lines = EnhancedList.from_file("data.txt")
```

## Special Method Initialization

### Using __new__
```python
class NonEmptyList(NewType(list)):
    def __new__(cls, items=None):
        if items is not None and len(items) == 0:
            raise ValueError("List cannot be empty")
        return super().__new__(cls)

    def __init__(self, items=None):
        super().__init__(items or [])
```

### Using __init_subclass__
```python
class TypedDict(NewType(dict)):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._validators = {}

    @classmethod
    def register_validator(cls, key_type, value_type):
        def decorator(func):
            cls._validators[(key_type, value_type)] = func
            return func
        return decorator
```

## Advanced Initialization

### Lazy Initialization
```python
class LazyList(NewType(list)):
    def __init__(self):
        self._initialized = False
        self._pending_items = []

    def _initialize(self):
        if not self._initialized:
            super().__init__()
            self.extend(self._pending_items)
            self._initialized = True
            del self._pending_items

    def append(self, item):
        if not self._initialized:
            self._pending_items.append(item)
        else:
            super().append(item)
```

### Dependency Injection
```python
class LoggedDict(NewType(dict)):
    def __init__(self, logger=None):
        super().__init__()
        if logger is None:
            import logging
            logger = logging.getLogger(__name__)
        self.logger = logger

    def __setitem__(self, key, value):
        self.logger.info(f"Setting {key}={value}")
        super().__setitem__(key, value)
```

## Configuration Management

### From Environment Variables
```python
import os

class EnvDict(NewType(dict)):
    def __init__(self, prefix='APP_'):
        super().__init__()
        self.prefix = prefix
        self._load_from_env()

    def _load_from_env(self):
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                config_key = key[len(self.prefix):].lower()
                self[config_key] = value
```

### From Configuration Files
```python
import json

class ConfigDict(NewType(dict)):
    @classmethod
    def from_json(cls, filename):
        instance = cls()
        with open(filename) as f:
            instance.update(json.load(f))
        return instance

    @classmethod
    def from_env_file(cls, filename):
        instance = cls()
        with open(filename) as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    instance[key] = value
        return instance
```

## Best Practices

1. **Clear Default Values**
   - Provide sensible defaults for optional parameters
   - Document default behaviors clearly

2. **Validate Early**
   - Check parameters during initialization
   - Fail fast if requirements aren't met

3. **Flexible Construction**
   - Support multiple initialization methods
   - Use factory methods for complex construction

4. **Resource Management**
   - Clean up resources in `__del__` if needed
   - Use context managers for complex resources

## Common Patterns

### Builder Pattern
```python
class ListBuilder:
    def __init__(self):
        self.items = []
        self.validators = []

    def add_validator(self, validator):
        self.validators.append(validator)
        return self

    def add_items(self, items):
        self.items.extend(items)
        return self

    def build(self):
        return ValidatedList(self.items, validators=self.validators)

class ValidatedList(NewType(list)):
    def __init__(self, items=None, validators=None):
        super().__init__(items or [])
        self.validators = validators or []
```

### Singleton Pattern
```python
class SingletonDict(NewType(dict)):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._initialized = True
```

### Pool Pattern
```python
class ListPool(NewType(list)):
    _pool = {}

    @classmethod
    def get_instance(cls, name):
        if name not in cls._pool:
            cls._pool[name] = cls()
        return cls._pool[name]

    @classmethod
    def clear_pool(cls):
        cls._pool.clear()
```

## Testing

### Basic Initialization Tests
```python
def test_validated_dict():
    def validator(k, v):
        return isinstance(k, str) and isinstance(v, int)

    d = ValidatedDict(validator)
    d["age"] = 25  # OK
    with pytest.raises(ValueError):
        d["name"] = "John"  # Fails validation
```

### Factory Method Tests
```python
def test_enhanced_list_factories():
    numbers = EnhancedList.range(1, 4)
    assert list(numbers) == [1, 2, 3]

    with open("test.txt", "w") as f:
        f.write("a\nb\nc")

    letters = EnhancedList.from_file("test.txt")
    assert list(letters) == ["a", "b", "c"]
```

### Resource Cleanup Tests
```python
def test_cleanup():
    with LoggedDict() as d:
        d["key"] = "value"
    # Logger should be closed after context exit
```
