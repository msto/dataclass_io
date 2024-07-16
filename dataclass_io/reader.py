from contextlib import contextmanager
from csv import DictReader
from pathlib import Path
from typing import Any
from typing import Iterator

from dataclass_io._lib.assertions import assert_dataclass_is_valid
from dataclass_io._lib.assertions import assert_file_header_matches_dataclass
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
    _header: FileHeader
    _reader: DictReader

    def __init__(
        self,
        fin: ReadableFileHandle,
        dataclass_type: type[DataclassInstance],
        delimiter: str = "\t",
        comment_prefix: str = "#",
        **kwds: Any,
    ) -> None:
        """
        Args:
            fin: Open file handle for reading.
            dataclass_type: Dataclass type.
            delimiter: The input file delimiter.
            comment_prefix: The prefix for any comment/preface rows preceding the header row.
            dataclass_type: Dataclass type.

        Raises:
            TypeError: If the provided type is not a dataclass.
        """
        assert_dataclass_is_valid(dataclass_type)
        assert_file_header_matches_dataclass(
            file=fin,
            dataclass_type=dataclass_type,
            delimiter=delimiter,
            comment_prefix=comment_prefix,
        )

        self._dataclass_type = dataclass_type
        self._fin = fin
        self._header = get_header(
            reader=self._fin, delimiter=delimiter, comment_prefix=comment_prefix
        )
        self._reader = DictReader(
            f=self._fin,
            fieldnames=fieldnames(dataclass_type),
            delimiter=delimiter,
        )

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
        delimiter: str = "\t",
        comment_prefix: str = "#",
    ) -> Iterator["DataclassReader"]:
        """
        Open a new `DataclassReader` from a file path.

        Args:
            filename: The path to the file from which dataclass instances will be read.
            dataclass_type: The dataclass type to read from file.
            delimiter: The input file delimiter.
            comment_prefix: The prefix for any comment/preface rows preceding the header row. These
                rows will be ignored when reading the file.

        Yields:
            A `DataclassReader` instance.

        Raises:
            FileNotFoundError: If the input file does not exist.
            IsADirectoryError: If the input file path is a directory.
            PermissionError: If the input file is not readable.
        """
        filepath: Path = Path(filename)

        # NB: The `DataclassReader` constructor will validate that the provided type is a valid
        # dataclass and that the file's header matches the fields of the provided dataclass type.
        assert_file_is_readable(filepath)

        fin = filepath.open("r")
        try:
            yield cls(
                fin=fin,
                dataclass_type=dataclass_type,
                delimiter=delimiter,
                comment_prefix=comment_prefix,
            )
        finally:
            fin.close()
