# Type Inheritance and Composition

This guide covers advanced topics related to type inheritance and composition using Python NewType.

## Multiple Inheritance

Python NewType supports multiple inheritance, allowing you to combine functionality from multiple base types:

```python
from newtype import NewType

class Printable:
    def print_info(self):
        print(f"Object state: {self.__dict__}")

class EnhancedDict(NewType(dict), Printable):
    def __init__(self):
        super().__init__()
        self.access_count = 0

    def __getitem__(self, key):
        self.access_count += 1
        return super().__getitem__(key)

d = EnhancedDict()
d["key"] = "value"
_ = d["key"]
d.print_info()  # Shows access_count: 1
```

## Inheritance Chain

You can create inheritance chains with NewType classes:

```python
class BaseDict(NewType(dict)):
    def get_keys_sorted(self):
        return sorted(self.keys())

class ExtendedDict(BaseDict):
    def get_values_sorted(self):
        return sorted(self.values())

class AdvancedDict(ExtendedDict):
    def get_items_sorted(self):
        return sorted(self.items())
```

## Method Resolution Order (MRO)

Understanding MRO is crucial when working with NewType inheritance:

```python
from newtype import NewType

class LoggableMixin:
    def log(self, message):
        print(f"Log: {message}")

class ValidatableMixin:
    def validate(self):
        return True

class EnhancedDict(NewType(dict), LoggableMixin, ValidatableMixin):
    pass

# View MRO
print(EnhancedDict.__mro__)
```

## Type Composition

Instead of inheritance, you can use composition with NewType:

```python
class DataValidator:
    def validate_data(self, data):
        return isinstance(data, (str, int, float))

class ValidatedDict(NewType(dict)):
    def __init__(self):
        super().__init__()
        self.validator = DataValidator()

    def __setitem__(self, key, value):
        if not self.validator.validate_data(value):
            raise ValueError("Invalid data type")
        super().__setitem__(key, value)
```

## Abstract Base Classes

You can use ABC with NewType:

```python
from abc import ABC, abstractmethod

class DataContainer(ABC):
    @abstractmethod
    def process_data(self, data):
        pass

class ProcessedDict(NewType(dict), DataContainer):
    def process_data(self, data):
        self.update(data)
        return sorted(self.items())
```

## Best Practices

1. **Keep the Inheritance Chain Short**
   - Deep inheritance hierarchies can be hard to understand and maintain
   - Consider composition over inheritance for complex behaviors

2. **Use Mixins Wisely**
   - Mixins should provide focused, reusable functionality
   - Avoid mixin dependencies on other mixins

3. **Document the Inheritance Structure**
   - Clearly document the purpose of each class in the inheritance chain
   - Explain any requirements or assumptions for subclasses

4. **Handle Method Conflicts**
   - Be explicit about method resolution when multiple inheritance is used
   - Use `super()` correctly to maintain the method resolution order

## Common Patterns

### Factory Pattern
```python
class DictFactory:
    @staticmethod
    def create_dict(dict_type: str):
        if dict_type == "sorted":
            return SortedDict()
        elif dict_type == "validated":
            return ValidatedDict()
        raise ValueError(f"Unknown dict type: {dict_type}")

class SortedDict(NewType(dict)):
    def items(self):
        return sorted(super().items())

class ValidatedDict(NewType(dict)):
    def __setitem__(self, key, value):
        if not isinstance(value, (str, int, float)):
            raise ValueError("Invalid value type")
        super().__setitem__(key, value)
```

### Decorator Pattern
```python
class LoggedDict(NewType(dict)):
    def __init__(self, wrapped_dict=None):
        super().__init__()
        if wrapped_dict:
            self.update(wrapped_dict)

    def __setitem__(self, key, value):
        print(f"Setting {key}={value}")
        super().__setitem__(key, value)

# Usage
base_dict = {"a": 1}
logged_dict = LoggedDict(base_dict)
```

### Observer Pattern
```python
class ObservableDict(NewType(dict)):
    def __init__(self):
        super().__init__()
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        for observer in self.observers:
            observer(key, value)

# Usage
def log_changes(key, value):
    print(f"Changed: {key}={value}")

d = ObservableDict()
d.add_observer(log_changes)
```
