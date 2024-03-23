from csv import DictReader
from dataclasses import fields
from dataclasses import is_dataclass
from pathlib import Path
from types import TracebackType
from typing import Any
from typing import ClassVar
from typing import Protocol
from typing import Type

from dataclass_io.lib import assert_readable_dataclass
from dataclass_io.lib import assert_readable_file


class DataclassInstance(Protocol):
    """
    Type hint for a non-specific instance of a dataclass.

    `DataclassReader` is an iterator over instances of the specified dataclass type. However, the
    actual type is not known prior to instantiation. This `Protocol` is used to type hint the return
    signature of `DataclassReader`'s `__next__` method.

    https://stackoverflow.com/a/55240861
    """
    __dataclass_fields__: ClassVar[dict[str, Any]]


class DataclassReader:
    def __init__(
        self,
        path: Path,
        dataclass_type: type,
        **kwds: Any,
    ) -> None:
        """
        Args:
            path: Path to the file to read.
            dataclass_type: Dataclass type.

        Raises:
            FileNotFoundError: If the input file does not exist.
            IsADirectoryError: If the input file path is a directory.
            PermissionError: If the input file is not readable.
            TypeError: If the provided type is not a dataclass.
        """

        assert_readable_file(path)
        assert_readable_dataclass(dataclass_type)

        # NB: Somewhat annoyingly, when this validation is extracted into an external helper,
        # mypy can no longer recognize that `self._dataclass_type` is a dataclass, and complains
        # about the return type on `_row_to_dataclass`.
        #
        # I'm leaving `assert_readable_dataclass` in case we want to extend the definition of what
        # it means to be a valid dataclass, but this is needed here to satisfy type checking.
        if not is_dataclass(dataclass_type):
            raise TypeError(f"The provided type must be a dataclass: {dataclass_type.__name__}")

        self._dataclass_type = dataclass_type

        self._fin = path.open("r")
        self._reader = DictReader(self._fin, **kwds)

    def __enter__(self) -> "DataclassReader":
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        self._fin.close()

    def __iter__(self) -> "DataclassReader":
        return self

    def __next__(self) -> DataclassInstance:
        row = next(self._reader)

        return self._row_to_dataclass(row)

    def _row_to_dataclass(self, row: dict[str, str]) -> DataclassInstance:
        """
        Convert a row of a CSV file into a dataclass instance.
        """

        coerced_values: dict[str, Any] = {}

        # Coerce each value in the row to the type of the corresponding field
        for field in fields(self._dataclass_type):
            value = row[field.name]
            coerced_values[field.name] = field.type(value)

        return self._dataclass_type(**coerced_values)
