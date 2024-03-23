from csv import DictReader
from dataclasses import dataclass
from dataclasses import fields
from dataclasses import is_dataclass
from io import TextIOWrapper
from pathlib import Path
from types import TracebackType
from typing import IO
from typing import Any
from typing import ClassVar
from typing import Optional
from typing import Protocol
from typing import TextIO
from typing import Type
from typing import TypeAlias

from dataclass_io.lib import assert_readable_dataclass
from dataclass_io.lib import assert_readable_file

ReadableFileHandle: TypeAlias = TextIOWrapper | IO | TextIO


class DataclassInstance(Protocol):
    """
    Type hint for a non-specific instance of a dataclass.

    `DataclassReader` is an iterator over instances of the specified dataclass type. However, the
    actual type is not known prior to instantiation. This `Protocol` is used to type hint the return
    signature of `DataclassReader`'s `__next__` method.

    https://stackoverflow.com/a/55240861
    """

    __dataclass_fields__: ClassVar[dict[str, Any]]


@dataclass(frozen=True, kw_only=True)
class FileHeader:
    """
    Header of a file.

    A file's header contains an optional preface, consisting of lines prefixed by a comment
    character and/or empty lines, and a required row of fieldnames before the data rows begin.

    Attributes:
        preface: A list of any lines preceding the fieldnames.
        fieldnames: The field names specified in the final line of the header.
    """

    preface: list[str]
    fieldnames: list[str]


class DataclassReader:
    def __init__(
        self,
        path: Path,
        dataclass_type: type,
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

        self.dataclass_type = dataclass_type
        self.delimiter = delimiter
        self.header_comment_char = header_comment_char

        self._fin = path.open("r")

        self._header = self._get_header(self._fin)
        if self._header is None:
            raise ValueError(f"Could not find a header in the provided file: {path}")

        if self._header.fieldnames != [f.name for f in fields(dataclass_type)]:
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

    def _get_header(
        self,
        reader: ReadableFileHandle,
    ) -> Optional[FileHeader]:
        """
        Read the header from an open file.

        The first row after any commented or empty lines will be used as the fieldnames.

        Lines preceding the fieldnames will be returned in the `preface.`

        NB: This function returns `Optional` instead of raising an error because the name of the
        source file is not in scope, making it difficult to provide a helpful error message. It is
        the responsibility of the caller to raise an error if the file is empty.

        See original proof-of-concept here: https://github.com/fulcrumgenomics/fgpyo/pull/103

        Args:
            reader: An open, readable file handle.
            comment_char: The character which indicates the start of a comment line.

        Returns:
            A `FileHeader` containing the field names and any preceding lines.
            None if the file was empty or contained only comments or empty lines.
        """

        preface: list[str] = []

        for line in reader:
            if line.startswith(self.header_comment_char) or line.strip() == "":
                preface.append(line.strip())
            else:
                break
        else:
            return None

        fieldnames = line.strip().split(self.delimiter)

        return FileHeader(preface=preface, fieldnames=fieldnames)
