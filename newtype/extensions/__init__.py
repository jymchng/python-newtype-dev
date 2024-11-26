"""Extension modules for Python NewType.

This package contains C extension modules that implement core functionality
for the Python NewType library:

- newtypeinit: Handles initialization and validation of NewType instances
- newtypemethod: Ensures proper type preservation in method calls
"""

from .newtypeinit import NEWTYPE_INIT_ARGS_STR, NEWTYPE_INIT_KWARGS_STR, NewTypeInit
from .newtypemethod import NewTypeMethod


__all__ = ["NewTypeInit", "NewTypeMethod", "NEWTYPE_INIT_ARGS_STR", "NEWTYPE_INIT_KWARGS_STR"]
