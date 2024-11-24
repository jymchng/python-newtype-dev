# Don't manually change, let poetry-dynamic-versioning handle it.
__version__ = "0.0.0"

__all__: "list[str]" = []

import logging
import sys
from logging import getLogger
from typing import TYPE_CHECKING
from weakref import WeakKeyDictionary

from src.newtype.extensions.newtypeinit import (
    NEWTYPE_INIT_ARGS_STR,
    NEWTYPE_INIT_KWARGS_STR,
    NewTypeInit,
)
from src.newtype.extensions.newtypemethod import NewTypeMethod

NEWTYPE_LOGGER = getLogger("newtype-python")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)s] %(message)s",
    stream=sys.stdout,
)

NEWTYPE_EXCLUDE_FUNC_STR = "_newtype_exclude_func_"
UNDEFINED = object()

if TYPE_CHECKING:
    from typing import Type, TypeVar

    T = TypeVar("T")


__GLOBAL_INTERNAL_TYPE_CACHE__: "WeakKeyDictionary[Type[T], Type[T]]" = (
    WeakKeyDictionary()
)


def newtype_exclude(func):
    setattr(func, NEWTYPE_EXCLUDE_FUNC_STR, True)
    return func


def func_is_excluded(func):
    return getattr(func, NEWTYPE_EXCLUDE_FUNC_STR, False)


def NewType(type_: "Type[T]", **context) -> "Type[T]":
    try:
        # we try to see if it is cached, if it is not, no problem either
        if type_ in __GLOBAL_INTERNAL_TYPE_CACHE__:
            NEWTYPE_LOGGER.debug(f"`{type_}` found in cache")
            return __GLOBAL_INTERNAL_TYPE_CACHE__[type_]
    except KeyError:
        pass

    class BaseNewType(type_):
        if hasattr(type_, "__slots__"):
            __slots__ = (
                *getattr(type_, "__slots__"),
                NEWTYPE_INIT_ARGS_STR,
                NEWTYPE_INIT_KWARGS_STR,
            )

        def __init_subclass__(cls, **context) -> None:
            super().__init_subclass__(**context)
            NEWTYPE_LOGGER.debug(type_, type_.__dict__)
            NEWTYPE_LOGGER.debug("cls.__dict__: ", cls.__dict__)
            constructor = cls.__init__
            original_cls_dict = {}
            for k, v in cls.__dict__.items():
                original_cls_dict[k] = v
            NEWTYPE_LOGGER.debug("original_cls_dict: ", original_cls_dict)
            for k, v in type_.__dict__.items():
                if (
                    callable(v)
                    and (k not in object.__dict__)
                    and (k not in original_cls_dict)
                ):
                    NEWTYPE_LOGGER.debug(
                        "callable(v) and (k not in object.__dict__) and (k not in original_cls_dict); k: ",
                        k,
                    )
                    setattr(cls, k, NewTypeMethod(v, type_))
                elif k not in object.__dict__:
                    if k == "__dict__":
                        continue
                    setattr(cls, k, v)
                    NEWTYPE_LOGGER.debug("Setted")
            NEWTYPE_LOGGER.debug("original_cls_dict: ", original_cls_dict)
            for k, v in original_cls_dict.items():
                NEWTYPE_LOGGER.debug("k in original_cls_dict: ", k)
                if (
                    callable(v)
                    and k != "__init__"
                    and k in type_.__dict__
                    and not func_is_excluded(v)
                ):
                    setattr(cls, k, NewTypeMethod(v, type_))
                else:
                    if k == "__dict__":
                        continue
                    setattr(cls, k, v)
                    NEWTYPE_LOGGER.debug("Setted")
            NEWTYPE_LOGGER.debug("Setting cls.__init__")
            cls.__init__ = NewTypeInit(constructor)
            if hasattr(cls, "__slots__"):
                NEWTYPE_LOGGER.debug("cls.__slots__: ", cls.__slots__)
            NEWTYPE_LOGGER.debug("Setting cls.__init__ completed")
            NEWTYPE_LOGGER.debug(
                "cls.__dict__: ", cls.__dict__, " at end of __init_subclass__"
            )
            return cls

        def __new__(cls, value, *_args, **_kwargs):
            NEWTYPE_LOGGER.debug("cls, cls.__new__: ", cls, cls.__new__)
            if type_.__new__ == object.__new__:
                NEWTYPE_LOGGER.debug(
                    "type_.__new__ == object.__new__; type_.__new__ = ", type_.__new__
                )
                inst = type_.__new__(cls)
                NEWTYPE_LOGGER.debug("inst: ", inst)
                NEWTYPE_LOGGER.debug("type(value): ", repr(type(value)))
                NEWTYPE_LOGGER.debug("_args: ", _args)
                NEWTYPE_LOGGER.debug("_kwargs: ", _kwargs)

                # copy all the attributes in `__dict__`
                value_dict: "dict" = getattr(value, "__dict__", UNDEFINED)
                NEWTYPE_LOGGER.debug("value_dict: ", value_dict)

                if value_dict is not UNDEFINED:
                    [setattr(inst, k, v) for k, v in value_dict.items()]

                # copy all the attributes in `__slots__`
                value_slots: tuple = getattr(value, "__slots__", UNDEFINED)
                NEWTYPE_LOGGER.debug("value_slots: ", value_slots)
                if value_slots is not UNDEFINED:
                    for k in value_slots:
                        v = getattr(value, k, UNDEFINED)
                        if v is not UNDEFINED:
                            setattr(inst, k, v)
            else:
                NEWTYPE_LOGGER.debug(
                    "type_.__new__ != object.__new__; type_.__new__ = ", type_.__new__
                )
                inst = type_.__new__(cls, value)
            return inst

        def __init__(self, _value, *_args, **_kwargs):
            ...
            # we intercept the call to constructors so that we don't accidentally call `object.__init__`

    try:
        # we try to store it in a cache, if it fails, no problem either
        if type_ not in __GLOBAL_INTERNAL_TYPE_CACHE__:
            NEWTYPE_LOGGER.debug(f"`type_` = {type_} is cached...")
            __GLOBAL_INTERNAL_TYPE_CACHE__[type_] = BaseNewType
    except Exception:
        pass

    return BaseNewType
