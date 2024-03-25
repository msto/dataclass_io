from csv import DictReader
from dataclasses import fields
from pathlib import Path
from types import TracebackType
from typing import Any
from typing import Type

from dataclass_io._lib.assertions import assert_dataclass_is_valid
from dataclass_io._lib.assertions import assert_file_is_readable
from dataclass_io._lib.dataclass_extensions import DataclassInstance
from dataclass_io._lib.dataclass_extensions import fieldnames
from dataclass_io._lib.file import FileHeader
from dataclass_io._lib.file import get_header


class DataclassReader:
    def __init__(
        self,
        path: Path,
        dataclass_type: type[DataclassInstance],
        delimiter: str = "\t",
        header_comment_char: str = "#",
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

        assert_file_is_readable(path)
        assert_dataclass_is_valid(dataclass_type)

        self.dataclass_type = dataclass_type
        self.delimiter = delimiter
        self.header_comment_char = header_comment_char

        self._fin = path.open("r")

        self._header: FileHeader = get_header(
            self._fin,
            delimiter=delimiter,
            header_comment_char=header_comment_char,
        )

        if self._header is None:
            raise ValueError(f"Could not find a header in the provided file: {path}")

        if self._header.fieldnames != fieldnames(dataclass_type):
            raise ValueError(
                "The provided file does not have the same field names as the provided dataclass:\n"
                f"\tDataclass: {dataclass_type.__name__}\n"
                f"\tFile: {path}\n"
                f"\tDataclass fields: {dataclass_type.__name__}\n"
                f"\tFile: {path}\n"
            )

        self._reader = DictReader(
            self._fin,
            fieldnames=self._header.fieldnames,
            delimiter=self.delimiter,
        )

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
        for field in fields(self.dataclass_type):
            value = row[field.name]
            coerced_values[field.name] = field.type(value)

        return self.dataclass_type(**coerced_values)
