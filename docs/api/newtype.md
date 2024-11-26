# API Reference

## Core Components

### NewType Factory

::: newtype.NewType
    options:
      show_root_heading: true
      show_source: true

### newtype_exclude Decorator

::: newtype.newtype_exclude
    options:
      show_root_heading: true
      show_source: true

## Type System Components

These are internal components that power Python NewType. While they're not typically used directly, understanding them can be helpful for advanced usage or debugging.

### NewTypeInit Descriptor

::: newtype.NewTypeInit
    options:
      show_root_heading: true
      show_source: true

### NewTypeMethod Descriptor

::: newtype.extensions.NewTypeMethod
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

The library uses Python's standard logging module for debugging and error reporting. The logger name is 'newtype'.
