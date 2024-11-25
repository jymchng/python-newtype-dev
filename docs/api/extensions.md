# API Extensions

This guide covers the extension points and APIs available in Python NewType for customizing type behavior.

## Core Extensions

### Type Decorators

```python
from newtype import NewType, newtype_exclude

class EnhancedDict(NewType(dict)):
    @newtype_exclude
    def special_method(self):
        """This method won't be wrapped by NewType"""
        pass
```

### Method Interceptors

```python
from newtype import method_interceptor

class LoggedDict(NewType(dict)):
    @method_interceptor
    def __setitem__(self, key, value):
        print(f"Setting {key}={value}")
        return super().__setitem__(key, value)
```

### Type Validators

```python
from newtype import type_validator

@type_validator
def validate_string(value):
    return isinstance(value, str)

class StringDict(NewType(dict)):
    __value_validator__ = validate_string
```

## Advanced Features

### Custom Type Creation

```python
from newtype import create_type

def custom_type_factory(base_type):
    def wrapper(cls):
        return create_type(base_type, cls)
    return wrapper

@custom_type_factory(dict)
class CustomDict:
    def custom_method(self):
        pass
```

### Method Registration

```python
from newtype import register_method

class ExtensibleDict(NewType(dict)):
    @register_method('get_or_create')
    def get_or_create(self, key, factory):
        if key not in self:
            self[key] = factory()
        return self[key]
```

### Type Composition

```python
from newtype import compose_types

# Combine multiple type behaviors
ValidatedLogged = compose_types([ValidatedDict, LoggedDict])
```

## Hook Points

### Initialization Hooks

```python
class HookedDict(NewType(dict)):
    def __pre_init__(self):
        """Called before initialization"""
        self.initialized = False

    def __post_init__(self):
        """Called after initialization"""
        self.initialized = True
```

### Method Hooks

```python
class MonitoredDict(NewType(dict)):
    def __pre_method__(self, name, args, kwargs):
        """Called before any method"""
        print(f"Calling {name}")

    def __post_method__(self, name, result):
        """Called after any method"""
        print(f"{name} returned {result}")
```

## Type System Integration

### Type Hints

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class TypedDict(NewType(dict), Generic[T]):
    def __setitem__(self, key, value: T):
        if not isinstance(value, T.__constraints__):
            raise TypeError(f"Expected {T}")
        super().__setitem__(key, value)
```

### Protocol Support

```python
from typing import Protocol

class Validatable(Protocol):
    def validate(self) -> bool:
        ...

class ValidatedDict(NewType(dict)):
    def validate(self) -> bool:
        return all(
            isinstance(v, Validatable) and v.validate()
            for v in self.values()
        )
```

## Performance Optimizations

### Method Caching

```python
from newtype import cached_method

class CachedDict(NewType(dict)):
    @cached_method
    def expensive_operation(self, key):
        # Expensive computation here
        return self.get(key)
```

### Lazy Evaluation

```python
from newtype import lazy_property

class LazyDict(NewType(dict)):
    @lazy_property
    def computed_values(self):
        return {k: complex_computation(v) for k, v in self.items()}
```

## Error Handling

### Custom Exceptions

```python
class ValidationError(Exception):
    pass

class StrictDict(NewType(dict)):
    def __setitem__(self, key, value):
        if not self._validate(key, value):
            raise ValidationError(f"Invalid: {key}={value}")
        super().__setitem__(key, value)
```

### Error Transformations

```python
from newtype import transform_error

class SafeDict(NewType(dict)):
    @transform_error(KeyError, default=None)
    def get_safe(self, key):
        return self[key]
```

## Debugging Support

### Inspection Tools

```python
from newtype import inspect_type

class DebugDict(NewType(dict)):
    def debug_info(self):
        return inspect_type(self)
```

### Logging Integration

```python
from newtype import log_operations

@log_operations(level='DEBUG')
class LoggedDict(NewType(dict)):
    pass
```

## Extension Examples

### Configuration Management

```python
class ConfigDict(NewType(dict)):
    @classmethod
    def from_env(cls, prefix=''):
        instance = cls()
        for key, value in os.environ.items():
            if key.startswith(prefix):
                instance[key[len(prefix):].lower()] = value
        return instance

    def to_env(self, prefix=''):
        for key, value in self.items():
            os.environ[f"{prefix}{key.upper()}"] = str(value)
```

### Data Validation

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
```

### Monitoring and Metrics

```python
class MetricsDict(NewType(dict)):
    def __init__(self):
        super().__init__()
        self.metrics = {
            'gets': 0,
            'sets': 0,
            'deletes': 0
        }

    def __getitem__(self, key):
        self.metrics['gets'] += 1
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        self.metrics['sets'] += 1
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self.metrics['deletes'] += 1
        super().__delitem__(key)
```

## Best Practices

1. **Extension Design**
   - Keep extensions focused and single-purpose
   - Document extension points clearly
   - Provide sensible defaults

2. **Performance Considerations**
   - Minimize overhead in critical paths
   - Use caching when appropriate
   - Profile extension impact

3. **Error Handling**
   - Use appropriate exception types
   - Provide clear error messages
   - Consider recovery strategies

4. **Testing Extensions**
   - Test extension points thoroughly
   - Verify behavior combinations
   - Check error conditions
