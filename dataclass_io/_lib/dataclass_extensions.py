from dataclasses import fields
from dataclasses import is_dataclass
from typing import Any
from typing import ClassVar
from typing import Protocol

from pydantic.dataclasses import dataclass as pydantic_dataclass
from pydantic.dataclasses import is_pydantic_dataclass


class DataclassInstance(Protocol):
    """
    Type hint for a non-specific instance of a dataclass.

    `DataclassReader` is an iterator over instances of the specified dataclass type. However, the
    actual type is not known prior to instantiation. This `Protocol` is used to type hint the return
    signature of `DataclassReader`'s `__next__` method.

    https://stackoverflow.com/a/55240861
    """

    __dataclass_fields__: ClassVar[dict[str, Any]]


def fieldnames(dataclass_type: type[DataclassInstance]) -> list[str]:
    """
    Return the fieldnames of the specified dataclass.
    """

    if not is_dataclass(dataclass_type):
        raise TypeError(f"The provided type must be a dataclass: {dataclass_type.__name__}")

    return [f.name for f in fields(dataclass_type)]


def row_to_dataclass(
    row: dict[str, str],
    dataclass_type: type[DataclassInstance],
) -> DataclassInstance:
    """
    Convert a row of a CSV file into a dataclass instance.

    Args:
        row: A dictionary mapping each fieldname to its (string) value.
        dataclass_type: The dataclass to which the row will be casted.
    """

    data: DataclassInstance

    # TODO support classes which inherit from `pydantic.BaseModel`
    if is_pydantic_dataclass(dataclass_type):
        # If we received a pydantic dataclass, we can simply use its validation
        data = dataclass_type(**row)
    else:
        # If we received a stdlib dataclass, we use pydantic's dataclass decorator to create a
        # version of the dataclass with validation. We instantiate from this version to take
        # advantage of pydantic's validation, but then unpack the validated data in order to return
        # an instance of the user-specified dataclass.

        params = dataclass_type.__dataclass_params__  # type:ignore[attr-defined]

        pydantic_cls = pydantic_dataclass(
            _cls=dataclass_type,
            repr=params.repr,
            eq=params.eq,
            order=params.order,
            unsafe_hash=params.unsafe_hash,
            frozen=params.frozen,
        )

        validated_data = pydantic_cls(**row)
        unpacked_data = {
            field.name: getattr(validated_data, field.name) for field in fields(dataclass_type)
        }

        data = dataclass_type(**unpacked_data)

    return data
