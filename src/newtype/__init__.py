from .newtype import NewType, newtype_exclude, func_is_excluded
from .extensions.newtypeinit import NewTypeInit
from .extensions.newtypemethod import NewTypeMethod

__version__ = "0.0.0"  # Don't manually change, let poetry-dynamic-versioning handle it
__all__ = ["NewType", "newtype_exclude", "func_is_excluded", "NewTypeInit", "NewTypeMethod"]
