import logging
import os
from typing import Any, Callable, List, Optional, Type, Union

from mypy.nodes import Argument, FuncDef, RefExpr, SymbolTableNode, TypeInfo, Var
from mypy.plugin import ClassDefContext, Plugin
from mypy.plugins.common import add_method
from mypy.types import AnyType, CallableType, Instance, TypeOfAny, UnionType
from mypy.types import Type as MypyType


# Set up logging
logger = logging.getLogger("newtype.mypy_plugin")
# Remove any existing handlers to prevent duplicates
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Only enable logging if __PYNT_DEBUG__ is set to "true"
if os.environ.get("__PYNT_DEBUG__", "").lower() == "true":
    # Create a file handler
    file_handler = logging.FileHandler("mypy_plugin.log")
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.WARNING)


def convert_union_type(typ: MypyType) -> MypyType:
    """Convert a type to use UnionType instead of | operator."""
    if isinstance(typ, UnionType):
        # If it's already a UnionType, convert its items
        return UnionType([convert_union_type(t) for t in typ.items])
    elif isinstance(typ, Instance) and typ.args:
        return typ.copy_modified(args=[convert_union_type(arg) for arg in typ.args])
    return typ


class NewTypePlugin(Plugin):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        logger.info("Initializing NewTypePlugin")

    def get_base_class_hook(self, fullname: str) -> Optional[Callable[[ClassDefContext], None]]:
        logger.debug(f"get_base_class_hook called with fullname: {fullname}")
        if "newtype.NewType" in fullname:
            logger.info(f"Found NewType class: {fullname}")
            return handle_newtype_class
        logger.debug(f"No hook for {fullname}")
        return None


def handle_newtype_class(ctx: ClassDefContext) -> None:  # noqa: C901
    logger.info(f"Processing NewType class: {ctx.cls.fullname}")

    if not hasattr(ctx.reason, "args") or not ctx.reason.args:
        logger.warning("No arguments provided to NewType")
        return

    # Get base type from NewType argument
    base_type_expr = ctx.reason.args[0]
    logger.debug(f"Base type expression: {base_type_expr}")

    if not isinstance(base_type_expr, RefExpr):
        logger.warning(f"Base type expression is not a RefExpr: {type(base_type_expr)}")
        return

    base_type: Optional[SymbolTableNode]

    # Handle built-in types specially
    if base_type_expr.fullname and base_type_expr.fullname.startswith("builtins."):
        logger.debug(f"Looking up built-in type: {base_type_expr.fullname}")
        base_type = ctx.api.lookup_fully_qualified(base_type_expr.fullname)
    else:
        logger.debug(f"Looking up qualified type: {base_type_expr.fullname}")
        base_type = ctx.api.lookup_qualified(base_type_expr.fullname, ctx.cls)

    if not base_type:
        logger.warning(f"Could not find base type: {base_type_expr.fullname}")
        return
    if not isinstance(base_type.node, TypeInfo):
        logger.warning(f"Base type node is not a TypeInfo: {type(base_type.node)}")
        return

    # Set up inheritance
    logger.info(f"Setting up inheritance for {ctx.cls.fullname} from {base_type.node.fullname}")
    base_instance = Instance(base_type.node, [])
    info = ctx.cls.info
    info.bases = [base_instance]
    info.mro = [info, base_type.node] + base_type.node.mro[1:]
    logger.debug(f"MRO: {[t.fullname for t in info.mro]}")

    # Copy all methods from base type
    logger.info(f"Processing methods from base type {base_type.node.fullname}")
    for name, node in base_type.node.names.items():
        if isinstance(node.node, FuncDef) and isinstance(node.node.type, CallableType):
            logger.debug(f"Processing method: {name}")
            method_type = node.node.type

            # Convert return type to subtype if it matches base type
            ret_type = convert_union_type(method_type.ret_type)
            logger.debug(f"Original return type for {name}: {ret_type}")

            if isinstance(ret_type, Instance) and ret_type.type == base_type.node:
                logger.debug(f"Converting return type for {name} to {info.fullname}")
                ret_type = Instance(info, [])
            elif isinstance(ret_type, UnionType):
                logger.debug(f"Processing union return type for {name}: {ret_type}")
                items: List[Union[MypyType, Instance]] = []
                for item in ret_type.items:
                    if isinstance(item, Instance) and item.type == base_type.node:
                        logger.debug(f"Converting union item from {item} to {info.fullname}")
                        items.append(Instance(info, []))
                    else:
                        items.append(item)
                ret_type = UnionType(items)
                logger.debug(f"Final union return type for {name}: {ret_type}")

            # Create arguments list, preserving original argument types
            arguments = []
            if method_type.arg_types:
                logger.debug(f"Processing arguments for method {name}")
                # Skip first argument (self)
                for i, (arg_type, arg_kind, arg_name) in enumerate(
                    zip(
                        method_type.arg_types[1:],
                        method_type.arg_kinds[1:],
                        method_type.arg_names[1:] or [""] * len(method_type.arg_types[1:]),
                    ),
                    start=1,
                ):
                    logger.debug(
                        f"Processing argument {i} for {name}: \
                            {arg_name or f'arg{i}'} of type {arg_type}"
                    )

                    # Special handling for __contains__ method
                    if name == "__contains__" and i == 1:
                        logger.debug(
                            "Using Any type for __contains__ argument to satisfy Container protocol"
                        )
                        arg_type = AnyType(TypeOfAny.special_form)
                    else:
                        # Convert any union types in arguments
                        arg_type = convert_union_type(arg_type)

                    # Create a new variable for the argument
                    var = Var(arg_name or f"arg{i}", arg_type)
                    var.is_ready = True

                    # Create the argument
                    arg = Argument(
                        variable=var,
                        type_annotation=arg_type,
                        initializer=None,
                        kind=arg_kind,
                    )
                    arguments.append(arg)

            # Add method to class
            logger.info(f"Adding method {name} to {ctx.cls.fullname} with return type {ret_type}")
            add_method(ctx, name, arguments, ret_type)


def plugin(version: str) -> Type[Plugin]:
    logger.info(f"Initializing plugin for mypy version: {version}")
    return NewTypePlugin
