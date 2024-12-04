"""Core implementation of the python-newtype library.

This module provides the main functionality for creating new types that preserve their
type information through all operations. It implements method interception, type
preservation, and proper inheritance handling.

The module consists of several key components:
    - NewType: The main factory function for creating new types
    - newtype_exclude: Decorator to exclude methods from type wrapping
    - BaseNewType: The base class for all NewType instances
    - Type caching system for performance optimization

The type system is designed to maintain proper type information while allowing for
full functionality of the wrapped types. It achieves this through careful method
interception and proper handling of Python's descriptor protocol.

Technical Details:
    - Uses a WeakKeyDictionary for type caching to prevent memory leaks
    - Implements proper slots handling for optimized memory usage
    - Maintains proper method resolution order (MRO)
    - Preserves all original type attributes and methods
    - Handles both normal and descriptor methods
"""

from typing import (
    TYPE_CHECKING,
    Any,
    Sequence,
    TypeVar,
    Union,
    cast,
)


if TYPE_CHECKING:
    from typing import (
        Callable,
        Dict,
        List,
    )

__all__: "List[str]" = []

import logging
import sys
from logging import getLogger
from weakref import WeakKeyDictionary

from .extensions.newtypeinit import (
    NEWTYPE_INIT_ARGS_STR,
    NEWTYPE_INIT_KWARGS_STR,
    NewTypeInit,
)
from .extensions.newtypemethod import NewTypeMethod


NEWTYPE_LOGGER = getLogger("newtype-python")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)s] %(message)s",
    stream=sys.stdout,
)

NEWTYPE_EXCLUDE_FUNC_STR = "_newtype_exclude_func_"
UNDEFINED = object()


T = TypeVar("T", bound=type)


__GLOBAL_INTERNAL_TYPE_CACHE__: "WeakKeyDictionary" = WeakKeyDictionary()


def newtype_exclude(func: "Callable"):
    """Decorator to exclude a method from type wrapping.

    This decorator marks methods that should not be wrapped by NewTypeMethod,
    allowing them to maintain their original behavior without type preservation.

    Args:
        func: The function to be excluded from type wrapping

    Returns
    -------
        The original function, marked with an exclusion flag

    Example:
        ```python
        class SafeStr(NewType(str)):
            @newtype_exclude
            def dangerous_operation(self) -> str:
                # This method will return a regular str, not a SafeStr
                return str(self)
        ```
    """
    setattr(func, NEWTYPE_EXCLUDE_FUNC_STR, True)
    return func


def func_is_excluded(func):
    """Check if a function is excluded from type wrapping.

    Args:
        func: The function to check

    Returns
    -------
        bool: True if the function is excluded, False otherwise
    """
    return getattr(func, NEWTYPE_EXCLUDE_FUNC_STR, False)


def NewType(base_type: T, **context: "Dict[str, Any]") -> T:  # noqa: N802, C901
    """Create a new type that preserves type information through all operations.

    This is the main factory function for creating new types. It wraps an existing
    type and ensures that all operations on instances of the new type preserve
    their type information.

    Args:
        base_type: The base type to wrap
        **context: Additional context for type creation (reserved for future use)

    Returns
    -------
        A new type that inherits from the base type and preserves type information

    Example:
        ```python
        class ValidatedStr(NewType(str)):
            def __init__(self, val: str) -> None:
                if not val.strip():
                    raise ValueError("String cannot be empty")


        # All operations preserve ValidatedStr type
        x = ValidatedStr("hello")
        y = x.upper()  # y is ValidatedStr, not str
        ```

    Technical Details:
        - Uses a global cache to prevent duplicate type creation
        - Properly handles slots and descriptors
        - Maintains all original type functionality
        - Provides proper type hints for IDE support
    """
    # Add a type check for base_type
    if not isinstance(base_type, type):
        raise TypeError(f"Expected a type, got {type(base_type).__name__}")

    try:
        # we try to see if it is cached, if it is not, no problem either
        if base_type in __GLOBAL_INTERNAL_TYPE_CACHE__:
            NEWTYPE_LOGGER.debug(f"`{base_type}` found in cache")
            return __GLOBAL_INTERNAL_TYPE_CACHE__[base_type]
    except KeyError:
        NEWTYPE_LOGGER.debug("Exception occurred but ignored during caching of NewType")
        pass

    class BaseNewType(base_type):  # type: ignore[valid-type, misc]
        """Base class for all NewType instances.

        This class provides the core functionality for type preservation and
        method interception. It handles:
        - Proper initialization of new instances
        - Method wrapping for type preservation
        - Slot handling for optimized memory usage
        - Attribute access and modification
        """

        if hasattr(base_type, "__slots__"):
            __slots__ = (
                *base_type.__slots__,
                NEWTYPE_INIT_ARGS_STR,
                NEWTYPE_INIT_KWARGS_STR,
            )

        def __init_subclass__(cls, **context) -> None:
            """Initialize a subclass of BaseNewType.

            This method is called when creating a new subclass of BaseNewType.
            It handles:
            - Method wrapping setup
            - Attribute copying from base type
            - Proper method resolution order
            - Constructor initialization

            Args:
                **context: Additional context for subclass initialization
            """
            super().__init_subclass__(**context)
            NEWTYPE_LOGGER.debug(base_type, base_type.__dict__)
            NEWTYPE_LOGGER.debug("cls.__dict__: ", cls.__dict__)

            constructor = cls.__init__
            original_cls_dict = {}
            for k, v in cls.__dict__.items():
                original_cls_dict[k] = v
            NEWTYPE_LOGGER.debug("original_cls_dict: ", original_cls_dict)
            for k, v in base_type.__dict__.items():
                if callable(v) and (k not in object.__dict__) and (k not in original_cls_dict):
                    NEWTYPE_LOGGER.debug(
                        "callable(v) and (k not in object.__dict__) and \
                            (k not in original_cls_dict) ; k: ",
                        k,
                    )
                    setattr(cls, k, NewTypeMethod(v, base_type))
                elif k not in object.__dict__:
                    if k == "__dict__":
                        continue
                    setattr(cls, k, v)
                    NEWTYPE_LOGGER.debug("Set")
            NEWTYPE_LOGGER.debug("original_cls_dict: ", original_cls_dict)
            for k, v in original_cls_dict.items():
                NEWTYPE_LOGGER.debug("k in original_cls_dict: ", k)
                if (
                    callable(v)
                    and k != "__init__"
                    and k in base_type.__dict__
                    and not func_is_excluded(v)
                ):
                    setattr(cls, k, NewTypeMethod(v, base_type))
                else:
                    if k == "__dict__":
                        continue
                    setattr(cls, k, v)
                    NEWTYPE_LOGGER.debug("Set")
            NEWTYPE_LOGGER.debug("Setting cls.__init__")
            cls.__init__ = NewTypeInit(constructor)  # type: ignore[method-assign]
            if hasattr(cls, "__slots__"):
                NEWTYPE_LOGGER.debug("cls.__slots__: ", cls.__slots__)
            NEWTYPE_LOGGER.debug("Setting cls.__init__ completed")
            NEWTYPE_LOGGER.debug("cls.__dict__: ", cls.__dict__, " at end of __init_subclass__")

        def __new__(cls, value=None, *_args, **_kwargs):
            """Create a new instance of BaseNewType.

            This method handles the creation of new instances, ensuring that
            type information is preserved.

            Args:
                value: The value to initialize the instance with
                *_args: Additional positional arguments
                **_kwargs: Additional keyword arguments
            """
            NEWTYPE_LOGGER.debug("cls, cls.__new__: ", cls, cls.__new__)
            if base_type.__new__ == object.__new__:
                NEWTYPE_LOGGER.debug(
                    "base_type.__new__ == object.__new__; base_type.__new__ = ", base_type.__new__
                )
                inst = object.__new__(cls)
                NEWTYPE_LOGGER.debug("inst: ", inst)
                NEWTYPE_LOGGER.debug("type(value): ", repr(type(value)))
                NEWTYPE_LOGGER.debug("_args: ", _args)
                NEWTYPE_LOGGER.debug("_kwargs: ", _kwargs)

                # copy all the attributes in `__dict__`
                value_dict: Union[dict, object] = getattr(value, "__dict__", UNDEFINED)
                NEWTYPE_LOGGER.debug("value_dict: ", value_dict)

                if value_dict is not UNDEFINED and isinstance(value_dict, dict):
                    for k, v in value_dict.items():
                        setattr(inst, k, v)

                # copy all the attributes in `__slots__`
                value_slots: Union[Sequence[str], object] = getattr(value, "__slots__", UNDEFINED)
                NEWTYPE_LOGGER.debug("value_slots: ", value_slots)
                if value_slots is not UNDEFINED:
                    for k in value_slots:
                        v = getattr(value, k, UNDEFINED)
                        if v is not UNDEFINED:
                            setattr(inst, k, v)
            else:
                NEWTYPE_LOGGER.debug(
                    "base_type.__new__ != object.__new__; base_type.__new__ = ", base_type.__new__
                )
                inst = cast("BaseNewType", base_type.__new__(cls, value))
            return inst

        def __init__(self, _value=None, *_args, **_kwargs):
            """Initialize an instance of BaseNewType.

            This method is called when an instance is created. It handles
            the initialization of the instance, ensuring that type information
            is preserved.

            Args:
                _value: The value to initialize the instance with
                *_args: Additional positional arguments
                **_kwargs: Additional keyword arguments
            """
            ...

    try:
        # we try to store it in a cache, if it fails, no problem either
        if base_type not in __GLOBAL_INTERNAL_TYPE_CACHE__:
            NEWTYPE_LOGGER.debug(f"`base_type` = {base_type} is cached...")
            __GLOBAL_INTERNAL_TYPE_CACHE__[base_type] = BaseNewType
    except Exception:
        NEWTYPE_LOGGER.debug("Exception occurred but ignored during caching of NewType")
        pass

    return cast(T, BaseNewType)
