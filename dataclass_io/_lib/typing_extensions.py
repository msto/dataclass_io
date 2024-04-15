from types import UnionType
from typing import Union
from typing import get_args
from typing import get_origin

NoneType = type(None)
"""Helpful alias for `type(None)`."""


def is_union(type_: type) -> bool:
    """
    True if `type_` is a union type.

    When declared with `Union[T, ...]` or `Optional[T]`, `get_origin()` returns `typing.Union`.
    When declared with PEP604 syntax `T | ...`, `get_origin()` returns `types.UnionType`.

    Args:
        type_: The type to check.

    Returns:
        True if `type_` is a union type.
    """
    return get_origin(type_) is Union or get_origin(type_) is UnionType


def is_optional(type_: type) -> bool:
    """
    True if `_type` is `Optional`, or the union of a single type and `None`.

    Args:
        type_: The type to check.

    Returns:
        True if `_type` is `Optional[T]`, `Union[T, None]` or `T | None`.
    """
    type_args: tuple[type] = get_args(type_)

    return is_union(type_) and (NoneType in type_args) and (len(type_args) == 2)
