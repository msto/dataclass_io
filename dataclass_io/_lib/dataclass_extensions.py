from dataclasses import fields
from dataclasses import is_dataclass
from typing import Any
from typing import ClassVar
from typing import Protocol


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

    coerced_values: dict[str, Any] = {}

    # Coerce each value in the row to the type of the corresponding field
    for field in fields(dataclass_type):
        value = row[field.name]
        coerced_values[field.name] = field.type(value)

    return dataclass_type(**coerced_values)
