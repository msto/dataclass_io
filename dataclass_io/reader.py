from csv import DictReader
from pathlib import Path
from types import TracebackType
from typing import Any
from typing import Type

from dataclass_io._lib.assertions import assert_dataclass_is_valid
from dataclass_io._lib.assertions import assert_file_header_matches_dataclass
from dataclass_io._lib.assertions import assert_file_is_readable
from dataclass_io._lib.dataclass_extensions import DataclassInstance
from dataclass_io._lib.dataclass_extensions import fieldnames
from dataclass_io._lib.dataclass_extensions import row_to_dataclass
from dataclass_io._lib.file import FileFormat
from dataclass_io._lib.file import FileHeader
from dataclass_io._lib.file import ReadableFileHandle
from dataclass_io._lib.file import get_header


class DataclassReader:
    _dataclass_type: type[DataclassInstance]
    _fin: ReadableFileHandle
    _header: FileHeader
    _reader: DictReader

    def __init__(
        self,
        filename: str | Path,
        dataclass_type: type[DataclassInstance],
        delimiter: str = "\t",
        comment: str = "#",
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

        filepath: Path = filename if isinstance(filename, Path) else Path(filename)
        file_format = FileFormat(
            delimiter=delimiter,
            comment=comment,
        )

        assert_dataclass_is_valid(dataclass_type)
        assert_file_is_readable(filepath)
        assert_file_header_matches_dataclass(filepath, dataclass_type, file_format)

        self._dataclass_type = dataclass_type
        self._fin = filepath.open("r")
        self._header = get_header(reader=self._fin, file_format=file_format)
        self._reader = DictReader(
            f=self._fin,
            fieldnames=fieldnames(dataclass_type),
            delimiter=file_format.delimiter,
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

    @classmethod
    @contextmanager
    def open(
        cls,
        filename: str | Path,
        dataclass_type: type[DataclassInstance],
        comment_prefix: str = DEFAULT_COMMENT_PREFIX,
    ) -> Iterator["DataclassReader"]:
        """
        Open a new `DataclassReader` from a file path.

        Raises:
            FileNotFoundError: If the input file does not exist.
            IsADirectoryError: If the input file path is a directory.
            PermissionError: If the input file is not readable.
        """
        filepath: Path = Path(filename)

        assert_dataclass_is_valid(dataclass_type)
        assert_file_is_readable(filepath)
        assert_file_header_matches_dataclass(filepath, dataclass_type, comment_prefix=comment_prefix)

        fin = filepath.open("r")
        try:
            yield cls(
                fin=fin,
                dataclass_type=dataclass_type,
                delimiter=delimiter,
                comment=comment,
            )
        finally:
            fin.close()
