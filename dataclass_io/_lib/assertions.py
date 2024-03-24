from dataclasses import is_dataclass
from os import R_OK
from os import access
from pathlib import Path

from dataclass_io._lib.dataclass_extensions import DataclassInstance


def assert_readable_file(path: Path) -> None:
    """
    Check that the input file exists and is readable.

    Raises:
        FileNotFoundError: If the provided file path does not exist.
        IsADirectoryError: If the provided file path is a directory.
        PermissionError: If the provided file path is not readable.
    """

    if not path.exists():
        raise FileNotFoundError(f"The input file does not exist: {path}")

    if not path.is_file():
        raise IsADirectoryError(f"The input file path is a directory: {path}")

    if not access(path, R_OK):
        raise PermissionError(f"The input file is not readable: {path}")


def assert_readable_dataclass(dc_type: type[DataclassInstance]) -> None:
    """
    Check that the input type is a parseable dataclass.

    Raises:
        TypeError: If the provided type is not a dataclass.
    """

    if not is_dataclass(dc_type):
        raise TypeError(f"The provided type must be a dataclass: {dc_type.__name__}")
