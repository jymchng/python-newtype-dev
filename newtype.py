# Don't manually change, let poetry-dynamic-versioning handle it.
__version__ = "0.0.0"

__all__: "list[str]" = []

from typing import TYPE_CHECKING, Protocol
from weakref import WeakKeyDictionary

from newtypeinit import NewInit, NEWTYPE_INIT_ARGS_STR, NEWTYPE_INIT_KWARGS_STR
from newtypemethod import NewTypeMethod

NEWTYPE_EXCLUDE_FUNC_STR = "_newtype_exclude_func_"
UNDEFINED = object()

if TYPE_CHECKING:
    from typing import Any, Dict, Tuple, Type, TypeVar

    T = TypeVar("T")

    class NewTypeObject(Protocol):
        _args_: "Tuple[Any, ...]"
        _kwargs_: "Dict[str, Any]"


__GLOBAL_INTERNAL_TYPE_CACHE__: "WeakKeyDictionary[Type, Type]" = WeakKeyDictionary()


def newtype_exclude(func):
    setattr(func, NEWTYPE_EXCLUDE_FUNC_STR, True)
    return func


def func_is_excluded(func):
    return getattr(func, NEWTYPE_EXCLUDE_FUNC_STR, False)


def NewType(type_: "T", **context) -> "T":
    try:
        # we try to see if it is cached, if it is not, no problem either
        if type_ in __GLOBAL_INTERNAL_TYPE_CACHE__:
            # print("Found in cache")
            return __GLOBAL_INTERNAL_TYPE_CACHE__[type_]
    except KeyError:
        pass

    if hasattr(type_, "__slots__"):
        from abc import ABCMeta

        class NewTypeMeta(ABCMeta):
            def __new__(meta, name, bases, attrs):
                return ABCMeta.__new__(
                    meta,
                    name,
                    bases,
                    {
                        **attrs,
                        **{
                            "__slots__": (
                                *type_.__slots__,
                                NEWTYPE_INIT_ARGS_STR,
                                NEWTYPE_INIT_KWARGS_STR,
                            )
                        },
                    },
                )

        metaclass = NewTypeMeta
    else:
        metaclass = type

    # class BaseBaseNewType(type_):
    #     def __init_subclass__(cls, **context) -> None:
    #         super().__init_subclass__(**context)
    #         # print(type_, type_.__dict__)
    #         print("cls.__dict__: ", cls.__dict__)
    #         constructor = cls.__init__
    #         original_cls_dict = {}
    #         for k, v in cls.__dict__.items():
    #             original_cls_dict[k] = v
    #         print("original_cls_dict: ", original_cls_dict)
    #         for k, v in type_.__dict__.items():
    #             if callable(v) and (k not in object.__dict__):
    #                 print("callable(v) and (k not in object.__dict__) and (k not in cls.__dict__); k: ", k)
    #                 setattr(cls, k, NewTypeMethod(v, type_))
    #             elif k not in object.__dict__:
    #                 if k == "__dict__":
    #                     continue
    #                 setattr(cls, k, v)
    #                 # print("Setted")
    #         print("original_cls_dict: ", original_cls_dict)
    #         for k, v in original_cls_dict.items():
    #             print("k in original_cls_dict: ", k)
    #             if callable(v) and k != '__init__':
    #                 setattr(cls, k, NewTypeMethod(v, type_))
    #             else:
    #                 if k in ("__dict__",):
    #                     continue
    #                 setattr(cls, k, v)
    #                 # print("Setted")
    #         # print("Setting cls.__init__")
    #         cls.__init__ = NewInit(constructor)
    #         # print("Setting cls.__init__ completed")
    #         print(cls.__init__())
    #         print("cls.__dict__: ", cls.__dict__, " at end of __init_subclass__")
    #         return cls

    class BaseNewType(type_):
        if hasattr(type_, "__slots__"):
            __slots__ = (
                *getattr(type_, "__slots__"),
                NEWTYPE_INIT_ARGS_STR,
                NEWTYPE_INIT_KWARGS_STR,
            )

        def __init_subclass__(cls, **context) -> None:
            super().__init_subclass__(**context)
            # print(type_, type_.__dict__)
            # print("cls.__dict__: ", cls.__dict__)
            constructor = cls.__init__
            original_cls_dict = {}
            for k, v in cls.__dict__.items():
                original_cls_dict[k] = v
            # print("original_cls_dict: ", original_cls_dict)
            for k, v in type_.__dict__.items():
                if (
                    callable(v)
                    and (k not in object.__dict__)
                    and (k not in original_cls_dict)
                ):
                    # print("callable(v) and (k not in object.__dict__) and (k not in original_cls_dict); k: ", k)
                    setattr(cls, k, NewTypeMethod(v, type_))
                elif k not in object.__dict__:
                    if k == "__dict__":
                        continue
                    setattr(cls, k, v)
                    # print("Setted")
            # print("original_cls_dict: ", original_cls_dict)
            for k, v in original_cls_dict.items():
                # print("k in original_cls_dict: ", k)
                if (
                    callable(v)
                    and k != "__init__"
                    and k in type_.__dict__
                    and not func_is_excluded(v)
                ):
                    setattr(cls, k, NewTypeMethod(v, type_))
                else:
                    if k in ("__dict__",):
                        continue
                    setattr(cls, k, v)
                    # print("Setted")
            # print("Setting cls.__init__")
            cls.__init__ = NewInit(constructor)
            if hasattr(cls, "__slots__"):
                print("cls.__slots__: ", cls.__slots__)
            # print("cls.__init__: ", cls.__init__('S1234567D'))
            # print("Setting cls.__init__ completed")
            # print("cls.__dict__: ", cls.__dict__, " at end of __init_subclass__")
            return cls

        def __new__(cls, value, *_args, **_kwargs):
            # print("cls, cls.__new__: ", cls, cls.__new__)
            if type_.__new__ == object.__new__:
                # print("type_.__new__ == object.__new__; type_.__new__ = ", type_.__new__)
                inst = type_.__new__(cls)
                # print("inst: ", inst)
                # print("type(value): ", repr(type(value)))
                # print("_args: ", _args)
                # print("_kwargs: ", _kwargs)

                value_dict: dict = getattr(value, "__dict__", UNDEFINED)
                # print("value_dict: ", value_dict)
                if value_dict is not UNDEFINED:
                    for k, v in value_dict.items():
                        setattr(inst, k, v)
                value_slots: tuple = getattr(value, "__slots__", UNDEFINED)
                # print("value_slots: ", value_slots)
                if value_slots is not UNDEFINED:
                    for k in value_slots:
                        v = getattr(value, k, UNDEFINED)
                        if v is not UNDEFINED:
                            setattr(inst, k, v)
            else:
                # print("type_.__new__ != object.__new__; type_.__new__ = ", type_.__new__)
                inst = type_.__new__(cls, value)
            return inst

        def __init__(self, _value, *_args, **_kwargs):
            ...
            # we intercept the call to constructors so that we don't accidentally call `object.__init__`

    try:
        # we try to store it in a cache, if it fails, no problem either
        if type_ not in __GLOBAL_INTERNAL_TYPE_CACHE__:
            # print("Cached...")
            __GLOBAL_INTERNAL_TYPE_CACHE__[type_] = BaseNewType
    except Exception:
        pass

    return BaseNewType
