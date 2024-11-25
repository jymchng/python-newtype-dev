"""Type stub for the newtypeinit C extension module.

This module provides type hints for the NewTypeInit descriptor class, which is responsible
for handling the initialization of NewType subclasses. It ensures proper type preservation
and method interception during instance creation.

The NewTypeInit class implements the descriptor protocol (__get__) and is callable,
allowing it to both intercept instance creation and maintain proper type information
throughout the initialization process.

Example:
    ```python
    class SafeStr(NewType(str)):
        def __init__(self, val: str) -> None:
            if "<script>" in val.lower():
                raise ValueError("XSS attempt detected")
    ```

The initialization of SafeStr is handled by NewTypeInit, which ensures that:
1. The __init__ method is called with proper arguments
2. The resulting instance maintains its SafeStr type
3. All string operations return SafeStr instances
"""

from typing import Any, Callable, Optional, Type, TypeVar, overload

NEWTYPE_INIT_ARGS_STR: str
NEWTYPE_INIT_KWARGS_STR: str

T = TypeVar("T")

class NewTypeInit:
    """Descriptor class for handling NewType subclass initialization.

    This class is responsible for intercepting instance creation of NewType subclasses
    and ensuring proper type preservation. It implements both the descriptor protocol
    and the callable interface.

    Args:
        func (Callable[..., Any]): The initialization function to be wrapped,
            typically the __init__ method of the NewType subclass.

    Attributes
    ----------
        func_get: The bound method if the wrapped function is a descriptor
        has_get: Boolean indicating if the wrapped function has __get__
        obj: The instance being initialized (None for unbound calls)
        cls: The class being initialized
    """

    def __init__(self, func: Callable[..., Any]) -> None: ...
    def __get__(self, inst: Any | None, owner: type[Any] | None) -> NewTypeInit:
        """Implement the descriptor protocol for method binding.

        This method is called when accessing the initialization method on either
        the class or an instance. It ensures proper method binding and type preservation.

        Args:
            inst: The instance the method is being accessed from (None for class access)
            owner: The class that owns this method

        Returns
        -------
            A bound or unbound NewTypeInit instance
        """
        ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Handle the actual initialization call.

        This method is called when creating a new instance of a NewType subclass.
        It ensures that:
        1. The parent class's __new__ is called properly
        2. The instance's __init__ is called with the provided arguments
        3. The correct type is preserved throughout the process

        Args:
            *args: Positional arguments for initialization
            **kwargs: Keyword arguments for initialization

        Returns
        -------
            A properly initialized instance of the NewType subclass
        """
        ...
