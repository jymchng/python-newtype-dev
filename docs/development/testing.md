# Testing python-newtype

This guide covers testing strategies and best practices for python-newtype.

## Test Structure

Our test suite is organized into several categories:

```
tests/
├── test_basic_examples.py    # Basic functionality tests
├── test_advanced_examples.py # Advanced feature tests
├── test_real_world.py       # Real-world use case tests
├── test_performance.py      # Performance benchmarks
└── conftest.py             # Shared fixtures and utilities
```

## Test Categories

### Unit Tests

Basic functionality tests:

```python
def test_enhanced_string():
    class UpperStr(NewType(str)):
        def __str__(self):
            return super().__str__().upper()

    text = UpperStr("hello")
    assert str(text) == "HELLO"
    assert text.lower() == "hello"

def test_validated_list():
    class IntList(NewType(list)):
        def append(self, item):
            if not isinstance(item, int):
                raise TypeError("Only integers allowed")
            super().append(item)

    numbers = IntList()
    numbers.append(42)
    with pytest.raises(TypeError):
        numbers.append("not a number")
```

### Integration Tests

Testing multiple components together:

```python
def test_config_system():
    class ConfigDict(NewType(dict)):
        def __init__(self, validator=None, logger=None):
            super().__init__()
            self.validator = validator
            self.logger = logger

        def __setitem__(self, key, value):
            if self.validator and not self.validator(key, value):
                raise ValueError("Invalid config")
            if self.logger:
                self.logger.info(f"Setting {key}={value}")
            super().__setitem__(key, value)

    # Test with both validation and logging
    logger = logging.getLogger("test")
    validator = lambda k, v: isinstance(v, (int, str))
    config = ConfigDict(validator, logger)

    config["name"] = "test"  # Should log
    config["count"] = 42     # Should log

    with pytest.raises(ValueError):
        config["invalid"] = []  # Should fail validation
```

### Property Tests

Using hypothesis for property-based testing:

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_unique_list_properties(items):
    class UniqueList(NewType(list)):
        def append(self, item):
            if item not in self:
                super().append(item)

    unique = UniqueList(items)
    # Test that all items are unique
    assert len(unique) == len(set(unique))
```

### Performance Tests

Using pytest-benchmark:

```python
def test_newtype_overhead(benchmark):
    class FastList(NewType(list)):
        pass

    def create_and_append():
        lst = FastList()
        for i in range(1000):
            lst.append(i)

    benchmark(create_and_append)
```

## Test Fixtures

Common test fixtures in `conftest.py`:

```python
import pytest
import logging

@pytest.fixture
def test_logger():
    logger = logging.getLogger("test")
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    yield logger
    logger.removeHandler(handler)

@pytest.fixture
def sample_data():
    return {
        "numbers": list(range(10)),
        "strings": ["a", "b", "c"],
        "mixed": [1, "two", 3.0]
    }
```

## Mock Objects

Using pytest's monkeypatch:

```python
def test_file_dict(monkeypatch, tmp_path):
    class FileDict(NewType(dict)):
        def __setitem__(self, key, value):
            with open(f"{key}.txt", "w") as f:
                f.write(str(value))
            super().__setitem__(key, value)

    # Temporarily change directory
    monkeypatch.chdir(tmp_path)

    # Test file operations
    d = FileDict()
    d["test"] = "value"

    assert (tmp_path / "test.txt").read_text() == "value"
```

## Error Testing

Testing error conditions and edge cases:

```python
def test_error_conditions():
    class StrictDict(NewType(dict)):
        def __setitem__(self, key, value):
            if not isinstance(key, str):
                raise TypeError("Keys must be strings")
            if not isinstance(value, (int, str)):
                raise TypeError("Values must be integers or strings")
            super().__setitem__(key, value)

    d = StrictDict()

    # Test valid cases
    d["str"] = "value"
    d["int"] = 42

    # Test invalid cases
    with pytest.raises(TypeError):
        d[123] = "value"  # Invalid key

    with pytest.raises(TypeError):
        d["key"] = []  # Invalid value
```

## Async Testing

Testing async functionality:

```python
import asyncio

async def test_async_list():
    class AsyncList(NewType(list)):
        async def async_append(self, item):
            await asyncio.sleep(0.1)  # Simulate async operation
            self.append(item)

    lst = AsyncList()
    await lst.async_append(1)
    assert lst == [1]
```

## Coverage Testing

Running tests with coverage:

```bash
pytest --cov=newtype --cov-report=html
```

Example coverage configuration (`pyproject.toml`):

```toml
[tool.coverage.run]
source = ["newtype"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
]
```
## Best Practices

1. **Test Isolation**
   - Each test should be independent
   - Use fixtures for setup and teardown
   - Avoid test interdependencies

2. **Clear Test Names**
   - Use descriptive test names
   - Follow `test_<feature>_<scenario>` pattern
   - Document complex test cases

3. **Comprehensive Testing**
   - Test both success and failure cases
   - Include edge cases
   - Test performance implications

4. **Clean Test Code**
   - Keep tests simple and focused
   - Use helper functions for common operations
   - Follow the same code style as main code
