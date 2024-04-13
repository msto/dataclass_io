from csv import DictWriter
from dataclasses import asdict
from enum import Enum
from enum import unique
from io import TextIOWrapper
from pathlib import Path
from types import TracebackType
from typing import IO
from typing import Any
from typing import Iterable
from typing import TextIO
from typing import Type
from typing import TypeAlias

from dataclass_io._lib.assertions import assert_dataclass_is_valid
from dataclass_io._lib.assertions import assert_fieldnames_are_dataclass_attributes
from dataclass_io._lib.assertions import assert_file_is_appendable
from dataclass_io._lib.assertions import assert_file_is_writable
from dataclass_io._lib.dataclass_extensions import DataclassInstance
from dataclass_io._lib.dataclass_extensions import fieldnames

WritableFileHandle: TypeAlias = TextIOWrapper | IO | TextIO


@unique
class WriteMode(Enum):
    APPEND = "a"
    WRITE = "w"


class DataclassWriter:
    def __init__(
        self,
        path: Path,
        dataclass_type: type[DataclassInstance],
        mode: str = "w",
        delimiter: str = "\t",
        overwrite: bool = True,
        include_fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
        **kwds: Any,
    ) -> None:
        """
        Args:
            path: Path to the file to write.
            dataclass_type: Dataclass type.

        Raises:
            FileNotFoundError: If the input file does not exist.
            IsADirectoryError: If the input file path is a directory.
            PermissionError: If the input file is not readable.
            TypeError: If the provided type is not a dataclass.
        """

        try:
            write_mode = WriteMode(mode)
        except ValueError:
            raise ValueError(f"`mode` must be either 'a' (append) or 'w' (write): {mode}") from None

        assert_dataclass_is_valid(dataclass_type)

        if include_fields is not None and exclude_fields is not None:
            raise ValueError(
                "Only one of `include_fields` and `exclude_fields` may be specified, not both."
            )
        elif exclude_fields is not None:
            assert_fieldnames_are_dataclass_attributes(exclude_fields, dataclass_type)
            self._fieldnames = [f for f in fieldnames(dataclass_type) if f not in exclude_fields]
        elif include_fields is not None:
            assert_fieldnames_are_dataclass_attributes(include_fields, dataclass_type)
            self._fieldnames = include_fields
        else:
            self._fieldnames = fieldnames(dataclass_type)

        if write_mode is WriteMode.WRITE:
            assert_file_is_writable(path, overwrite=overwrite)
        else:
            assert_file_is_appendable(path, dataclass_type=dataclass_type)
            raise NotImplementedError

        self.dataclass_type = dataclass_type
        self.delimiter = delimiter
        self._fout = path.open(mode)

        # TODO: optionally add preface
        # If we aren't appending, write the header before any rows
        if write_mode is WriteMode.WRITE:
            self._fout.write(self.delimiter.join(self._fieldnames) + "\n")

        self._writer = DictWriter(
            f=self._fout,
            fieldnames=self._fieldnames,
            delimiter=self.delimiter,
        )

    def __enter__(self) -> "DataclassWriter":
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._fout.close()

    def write(self, dataclass_instance: DataclassInstance) -> None:
        # Filter and/or re-order output fields if necessary
        row = asdict(dataclass_instance)
        row = {fieldname: row[fieldname] for fieldname in self._fieldnames}

        self._writer.writerow(row)

    def writeall(self, dataclass_instances: Iterable[DataclassInstance]) -> None:
        for dataclass_instance in dataclass_instances:
            self.write(dataclass_instance)
