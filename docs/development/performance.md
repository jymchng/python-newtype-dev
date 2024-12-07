# Performance Considerations

This document outlines performance considerations when using python-newtype and provides guidance on optimizing your code.

## Memory Usage

python-newtype is designed to be memory-efficient, with minimal overhead compared to the base types being wrapped. However, there are a few things to keep in mind:

1. Each wrapped instance maintains a reference to its base class
2. Additional attributes and methods will consume extra memory
3. Method interception adds a small overhead for intercepted calls

## Performance Impact

### Method Call Overhead

When using NewType, there is a small performance overhead for method calls due to the interception mechanism:

```python
from newtype import NewType
import time

# Regular string
regular_str = "hello" * 1000
start = time.time()
for _ in range(10000):
    regular_str.upper()
regular_time = time.time() - start

# NewType string
class EnhancedStr(NewType(str)):
    pass

enhanced_str = EnhancedStr("hello" * 1000)
start = time.time()
for _ in range(10000):
    enhanced_str.upper()
newtype_time = time.time() - start

print(f"Regular string time: {regular_time:.4f}s")
print(f"NewType string time: {newtype_time:.4f}s")
```

The overhead is typically negligible for most applications but may become noticeable in performance-critical loops.

## Optimization Tips

### 1. Minimize Method Interception

Only intercept methods when necessary:

```python
from newtype import NewType, newtype_exclude

class OptimizedDict(NewType(dict)):
    # Mark methods that don't need interception
    @newtype_exclude
    def get(self, key, default=None):
        return super().get(key, default)
```

### 2. Avoid Unnecessary Wrapping

Don't wrap objects unnecessarily:

```python
# Less efficient
class SimpleList(NewType(list)):
    pass

# More efficient - use regular list if no new functionality is needed
regular_list = []
```

## Benchmarking

Always benchmark your specific use case to ensure performance meets your requirements. Use Python's `timeit` module or a profiling tool like cProfile for accurate measurements.

Example benchmarking code:

```python
import timeit

def benchmark_regular_vs_newtype():
    setup = """
from newtype import NewType

class EnhancedStr(NewType(str)):
    def reverse(self):
        return self[::-1]

regular_str = "hello" * 100
enhanced_str = EnhancedStr("hello" * 100)
    """

    regular_code = "regular_str.upper()"
    enhanced_code = "enhanced_str.upper()"

    regular_time = timeit.timeit(regular_code, setup=setup, number=100000)
    enhanced_time = timeit.timeit(enhanced_code, setup=setup, number=100000)

    print(f"Regular string: {regular_time:.4f}s")
    print(f"Enhanced string: {enhanced_time:.4f}s")
```

## Memory Profiling

For memory-critical applications, use memory profiling tools:

```python
from memory_profiler import profile

@profile
def memory_test():
    # Regular dict
    d1 = {str(i): i for i in range(1000)}

    # NewType dict
    class TrackedDict(NewType(dict)):
        def __setitem__(self, key, value):
            super().__setitem__(key, value)

    d2 = TrackedDict()
    for i in range(1000):
        d2[str(i)] = i
```
