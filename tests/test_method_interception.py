import pytest
import logging
from time import sleep

from newtype import NewType


# Define test classes here to avoid NameError
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


class ProcessedDict(NewType(dict)):
    def __setitem__(self, key, value):
        processed_value = self._pre_process(value)
        super().__setitem__(key, processed_value)

    def _pre_process(self, value):
        if isinstance(value, str):
            return value.strip()
        return value


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


class ManagedDict(NewType(dict)):
    def __enter__(self):
        self._backup = dict(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.clear()
            self.update(self._backup)
        del self._backup
        return False


class FilteredDict(NewType(dict)):
    def __iter__(self):
        return (k for k in super().__iter__() if not k.startswith("_"))

    def items(self):
        return ((k, v) for k, v in super().items() if not k.startswith("_"))

    def values(self):
        return (v for k, v in super().items() if not k.startswith("_"))

    def keys(self):
        return (k for k in self if not k.startswith("_"))


class InterceptedDict(NewType(dict)):
    _intercepted_methods = set()

    @classmethod
    def intercept(cls, method_name):
        cls._intercepted_methods.add(method_name)

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        # Fix recursion by checking only for callable attributes
        if name != "_intercepted_methods" and callable(attr) and name in self._intercepted_methods:
            print(f"Calling {name}")
        return attr


class DynamicDict(NewType(dict)):
    def __init__(self):
        super().__init__()

    def _create_get_method(self, key):
        if isinstance(key, str) and key.isidentifier():
            setattr(self, f"get_{key}", lambda k=key: self[k])

    def __setitem__(self, key, value) -> None:
        self._create_get_method(key)
        return super().__setitem__(key, value)


class CachedDict(NewType(dict)):
    _cache = {}

    def get_or_default(self, key, default=None):
        cache_key = (key, default)
        if cache_key not in self._cache:
            self._cache[cache_key] = self.get(key, default)
        return self._cache[cache_key]

    def clear_cache(self):
        self._cache.clear()


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


class ValidatedList(NewType(list)):
    def __init__(self, validator=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.validator = validator or (lambda x: True)

    def append(self, item):
        if not self.validator(item):
            raise ValueError(f"Invalid item: {item}")
        super().append(item)

    def extend(self, items):
        if not all(self.validator(item) for item in items):
            raise ValueError("Invalid items in sequence")
        super().extend(items)


class LoggedDict(NewType(dict)):
    def __init__(self, logger=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logger or logging.getLogger(__name__)

    def __setitem__(self, key, value):
        self.logger.info(f"Setting {key}={value}")
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self.logger.info(f"Deleting {key}")
        super().__delitem__(key)


class MetricsDict(NewType(dict)):
    def __init__(self):
        super().__init__()
        self.metrics = {"gets": 0, "sets": 0, "deletes": 0}

    def __getitem__(self, key):
        self.metrics["gets"] += 1
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        self.metrics["sets"] += 1
        super().__setitem__(key, value)

    def __delitem__(self, key):
        self.metrics["deletes"] += 1
        super().__delitem__(key)


def test_tracked_list():
    tracked = TrackedList()
    tracked.append(1)
    tracked.extend([2, 3])
    assert tracked.operation_count == 2
    assert list(tracked) == [1, 2, 3]


def test_processed_dict():
    processed = ProcessedDict()
    processed["key"] = "  value  "
    assert processed["key"] == "value"


def test_chainable_list():
    chainable = ChainableList()
    result = chainable.append(3).extend([1, 2]).sort()
    assert list(result) == [1, 2, 3]
    assert result is chainable


def test_managed_dict():
    managed = ManagedDict()
    managed["key"] = "value"

    try:
        with managed:
            managed["key"] = "new_value"
            assert managed["key"] == "new_value"
            raise ValueError("Test error")
    except ValueError:
        # Verify the context manager properly handled the error
        assert managed["key"] == "value"  # Should be rolled back


def test_filtered_dict():
    filtered = FilteredDict()
    filtered["public"] = 1
    filtered["_private"] = 2

    assert list(filtered.keys()) == ["public"]
    assert list(filtered.values()) == [1]
    assert list(filtered.items()) == [("public", 1)]


def test_intercepted_dict():
    InterceptedDict.intercept("clear")
    intercepted = InterceptedDict()
    intercepted["key"] = "value"
    intercepted.clear()  # Should print "Calling clear"
    assert len(intercepted) == 0


def test_dynamic_dict():
    dynamic = DynamicDict()
    dynamic["count"] = 42
    assert dynamic.get_count() == 42


def test_cached_dict():
    cached = CachedDict()
    cached["key"] = "value"

    # First call should cache
    result1 = cached.get_or_default("key", "default")
    # Second call should use cache
    result2 = cached.get_or_default("key", "default")

    assert result1 == result2 == "value"

    # Clear cache and verify it works
    cached.clear_cache()
    result3 = cached.get_or_default("key", "default")
    assert result3 == "value"


def test_lazy_dict():
    lazy = LazyDict()
    computed = False

    def compute_value():
        nonlocal computed
        computed = True
        return 42

    lazy.set_lazy("key", compute_value)
    assert not computed  # Not computed yet

    value = lazy["key"]
    assert computed  # Now computed
    assert value == 42


def test_validated_list():
    def is_positive(x):
        return x > 0

    validated = ValidatedList(validator=is_positive)
    validated.append(1)

    with pytest.raises(ValueError):
        validated.append(-1)

    with pytest.raises(ValueError):
        validated.extend([1, -1, 2])


def test_logged_dict():
    logger = logging.getLogger("test")
    logger.setLevel(logging.INFO)

    logged = LoggedDict(logger=logger)
    logged["key"] = "value"
    del logged["key"]


def test_metrics_dict():
    metrics = MetricsDict()

    # Add some delay to make timing measurable
    metrics["key"] = "value"
    sleep(0.1)
    _ = metrics["key"]

    assert metrics.metrics["gets"] == 1
    assert metrics.metrics["sets"] == 1
    assert metrics.metrics["deletes"] == 0
