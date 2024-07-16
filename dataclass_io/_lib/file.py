from dataclasses import dataclass
from enum import Enum
from enum import unique
from io import TextIOWrapper
from typing import IO
from typing import Any
from typing import Optional
from typing import TypeAlias

ReadableFileHandle: TypeAlias = TextIOWrapper
"""A file handle open for reading."""

WritableFileHandle: TypeAlias = TextIOWrapper | IO[Any]
"""A file handle open for writing."""


@unique
class WriteMode(Enum):
    """
    The mode in which to open a file for writing.

    Attributes:
        value: The mode.
        abbreviation: The short version of the mode (used with Python's `open()`).
    """

    value: str
    abbreviation: str

    def __new__(cls, value: str, abbreviation: str) -> "WriteMode":
        enum = object.__new__(cls)
        enum._value_ = value

        return enum

    # NB: Specifying the additional fields in the `__init__` method instead of `__new__` is
    # necessary in order to construct `WriteMode` from only the value (e.g. `WriteMode("append")`).
    # Otherwise, `mypy` complains about a missing positional argument.
    # https://stackoverflow.com/a/54732120
    def __init__(self, _: str, abbreviation: str = None):
        self.abbreviation = abbreviation

    WRITE = "write", "w"
    """Write to a new file."""

    APPEND = "append", "a"
    """Append to an existing file."""


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


def get_header(
    reader: ReadableFileHandle,
    delimiter: str,
    comment_prefix: str,
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

    # TODO: optionally reset file handle to the original position after reading the header

    preface: list[str] = []

    for line in reader:
        if line.startswith(comment_prefix) or line.strip() == "":
            preface.append(line.strip())
        else:
            break
    else:
        return None

    fieldnames = line.strip().split(delimiter)

    return FileHeader(preface=preface, fieldnames=fieldnames)
