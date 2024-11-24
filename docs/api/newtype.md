# API Reference

## NewType

::: newtype.NewType
    options:
      show_root_heading: true
      show_source: true

## newtype_exclude

::: newtype.newtype_exclude
    options:
      show_root_heading: true
      show_source: true

## Internal Functions and Classes

These are internal components that power Python NewType. While they're not typically used directly, understanding them can be helpful for advanced usage or debugging.

### NewTypeMethod

::: newtype.extensions.newtypemethod.NewTypeMethod
    options:
      show_root_heading: true
      show_source: true

### NewTypeInit

::: newtype.extensions.newtypeinit.NewTypeInit
    options:
      show_root_heading: true
      show_source: true

## Constants

### NEWTYPE_INIT_ARGS_STR
Internal string constant used to store initialization arguments.

### NEWTYPE_INIT_KWARGS_STR
Internal string constant used to store initialization keyword arguments.

### NEWTYPE_EXCLUDE_FUNC_STR
Internal string constant used to mark functions that should not be wrapped.

## Type Variables

### T
Type variable used for generic type hints in the implementation.

## Logging

The library uses Python's standard logging module. You can configure logging for debug output:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)s] %(message)s"
)
```

The logger name is "newtype-python".