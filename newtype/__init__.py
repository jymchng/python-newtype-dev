"""python-newtype Library: Advanced Type System for Python.

This library provides a powerful and flexible way to create new types in Python that
maintain proper type information and behavior. It allows for the creation of subtypes
that preserve their type through all operations, making it ideal for creating type-safe
domain models and validated data types.

Key Features:
    - True subtype preservation through all operations
    - Automatic method interception and type coercion
    - Support for type validation during initialization
    - Seamless integration with Python's type system
    - Full support for method chaining
    - Comprehensive type hints and IDE support

Example:
    ```python
    from newtype import NewType


    class PositiveInt(NewType(int)):
        def __init__(self, val: int) -> None:
            if val <= 0:
                raise ValueError("Value must be positive")


    # All operations preserve the PositiveInt type
    x = PositiveInt(5)
    y = x + 3  # y is also a PositiveInt
    ```

The library consists of several key components:
    - NewType: The main factory function for creating new types
    - NewTypeInit: Handles initialization and validation of new types
    - NewTypeMethod: Ensures proper type preservation in method calls
    - newtype_exclude: Decorator to exclude methods from type wrapping
"""

from .extensions.newtypeinit import NewTypeInit
from .extensions.newtypemethod import NewTypeMethod
from .newtype import NewType, func_is_excluded, newtype_exclude


__version__ = "0.0.0"  # Don't manually change, let poetry-dynamic-versioning handle it
__all__ = [
    "NewType",
    "newtype_exclude",
    "func_is_excluded",
    "NewTypeInit",
    "NewTypeMethod",
    "mypy_plugin",
]
