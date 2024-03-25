from dataclasses import is_dataclass
from os import R_OK
from os import W_OK
from os import access
from os import stat
from pathlib import Path

from dataclass_io._lib.dataclass_extensions import DataclassInstance
from dataclass_io._lib.dataclass_extensions import fieldnames
from dataclass_io._lib.file import get_header


def assert_file_is_readable(path: Path) -> None:
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


def assert_file_is_writable(path: Path, overwrite: bool = True) -> None:
    """
    Check that the output file path is writable.

    Optionally, ensure the output file does not exist.

    Raises:
        FileExistsError: If the provided file path exists when `overwrite` is set to `False`.
        FileNotFoundError: If the provided file path's parent directory does not exist.
        IsADirectoryError: If the provided file path is a directory.
        PermissionError: If the provided file path is not writable.
    """

    if path.exists():
        if not overwrite:
            raise FileExistsError(
                f"The output file already exists: {path}\n"
                "Specify `overwrite=True` to overwrite the existing file."
            )

        if not path.is_file():
            raise IsADirectoryError(f"The output file path is a directory: {path}")

        if not access(path, W_OK):
            raise PermissionError(f"The output file is not writable: {path}")

    else:
        if not path.parent.exists():
            raise FileNotFoundError(
                f"The specified directory for the output file path does not exist: {path.parent}"
            )

        if not access(path.parent, W_OK):
            raise PermissionError(
                f"The specified directory for the output file path is not writable: {path.parent}"
            )


def assert_file_is_appendable(path: Path, dataclass_type: type[DataclassInstance]) -> None:
    if not path.exists():
        raise FileNotFoundError(f"The specified output file does not exist: {path}")

    if not path.is_file():
        raise IsADirectoryError(f"The specified output file path is a directory: {path}")

    if not access(path, W_OK):
        raise PermissionError(f"The specified output file is not writable: {path}")

    if stat(path).st_size == 0:
        raise ValueError(f"The specified output file is empty: {path}")

    if not access(path, R_OK):
        raise PermissionError(
            f"The specified output file is not readable: {path}\n"
            "The output file must be readable to append to it. "
            "The header of the existing output file is checked for consistency with the provided "
            "dataclass before appending to it."
        )

    # TODO: pass delimiter and header_comment_char to get_header
    with path.open("r") as f:
        header = get_header(f)
        if header is None:
            raise ValueError(f"Could not find a header in the specified output file: {path}")

        if header.fieldnames != fieldnames(dataclass_type):
            raise ValueError(
                "The specified output file does not have the same field names as the provided "
                f"dataclass {path}"
            )


def assert_dataclass_is_valid(dataclass_type: type[DataclassInstance]) -> None:
    """
    Check that the input type is a parseable dataclass.

    Raises:
        TypeError: If the provided type is not a dataclass.
    """

    if not is_dataclass(dataclass_type):
        raise TypeError(f"The provided type must be a dataclass: {dataclass_type.__name__}")
