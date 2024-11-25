from .extensions.newtypeinit import NewTypeInit
from .extensions.newtypemethod import NewTypeMethod
from .newtype import NewType, func_is_excluded, newtype_exclude


__version__ = "0.0.0"  # Don't manually change, let poetry-dynamic-versioning handle it
__all__ = ["NewType", "newtype_exclude", "func_is_excluded", "NewTypeInit", "NewTypeMethod"]
