"""Type stub for the newtypemethod C extension module.

This module provides type hints for the NewTypeMethod descriptor class, which is responsible
for method interception and type preservation in NewType subclasses. It ensures that
methods of NewType subclasses maintain proper type information and behavior.

The NewTypeMethod class implements the descriptor protocol (__get__) and is callable,
allowing it to both bind methods properly and maintain type information when the methods
are called.

Example:
    ```python
    class SafeStr(NewType(str)):
        def upper(self) -> "SafeStr":
            # This method is wrapped by NewTypeMethod to ensure the return value
            # is properly typed as SafeStr instead of str
            return super().upper()
    ```

In this example, NewTypeMethod ensures that the upper() method returns a SafeStr
instance instead of a regular str, maintaining type safety throughout the operation.
"""

from typing import Any, Callable, Optional, Type, TypeVar, overload

T = TypeVar("T")

class NewTypeMethod:
    """Descriptor class for handling NewType subclass method calls.

    This class is responsible for intercepting method calls on NewType subclasses
    and ensuring proper type preservation. It implements both the descriptor protocol
    and the callable interface.

    Args:
        func (Callable[..., Any]): The method to be wrapped
        wrapped_cls (Type[Any]): The NewType subclass that owns this method

    Attributes
    ----------
        func_get: The bound method if the wrapped function is a descriptor
        has_get: Boolean indicating if the wrapped function has __get__
        obj: The instance the method is bound to (None for unbound calls)
        cls: The class that owns this method
        wrapped_cls: The NewType subclass this method belongs to
    """

    def __init__(self, func: Callable[..., Any], wrapped_cls: type[Any]) -> None: ...
    def __get__(self, inst: Any | None, owner: type[Any] | None) -> NewTypeMethod:
        """Implement the descriptor protocol for method binding.

        This method is called when accessing a method on either the class or an
        instance. It ensures proper method binding and type preservation.

        Args:
            inst: The instance the method is being accessed from (None for class access)
            owner: The class that owns this method

        Returns
        -------
            A bound or unbound NewTypeMethod instance
        """
        ...

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Handle the actual method call.

        This method is called when invoking a method on a NewType subclass instance.
        It ensures that:
        1. The original method is called with proper arguments
        2. The return value maintains the correct type
        3. Type information is preserved for method chaining

        Args:
            *args: Positional arguments for the method call
            **kwargs: Keyword arguments for the method call

        Returns
        -------
            The result of the method call, properly typed as the NewType subclass
        """
        ...
