from csv import DictReader
from pathlib import Path
from types import TracebackType
from typing import Any
from typing import Type

from dataclass_io._lib.assertions import assert_dataclass_is_valid
from dataclass_io._lib.assertions import assert_file_is_readable
from dataclass_io._lib.dataclass_extensions import DataclassInstance
from dataclass_io._lib.dataclass_extensions import fieldnames
from dataclass_io._lib.dataclass_extensions import row_to_dataclass
from dataclass_io._lib.file import FileHeader
from dataclass_io._lib.file import ReadableFileHandle
from dataclass_io._lib.file import get_header


class DataclassReader:
    _dataclass_type: type[DataclassInstance]
    _fin: ReadableFileHandle
    _reader: DictReader

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

        self._dataclass_type = dataclass_type
        self._fin = path.open("r")

        header: FileHeader = get_header(
            self._fin,
            delimiter=delimiter,
            header_comment_char=header_comment_char,
        )

        if header is None:
            raise ValueError(f"Could not find a header in the provided file: {path}")

        if header.fieldnames != fieldnames(dataclass_type):
            raise ValueError(
                "The provided file does not have the same field names as the provided dataclass:\n"
                f"\tDataclass: {dataclass_type.__name__}\n"
                f"\tFile: {path}\n"
                f"\tDataclass fields: {', '.join(fieldnames(dataclass_type))}\n"
                f"\tFile: {', '.join(header.fieldnames)}\n"
            )

        self._reader = DictReader(
            self._fin,
            fieldnames=header.fieldnames,
            delimiter=delimiter,
        )

    def __enter__(self) -> "DataclassReader":
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the reader."""
        self._fin.close()

    def __iter__(self) -> "DataclassReader":
        return self

    def __next__(self) -> DataclassInstance:
        row = next(self._reader)

        return row_to_dataclass(row, self._dataclass_type)
