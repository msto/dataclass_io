from dataclasses import dataclass
from pathlib import Path

import pytest

from dataclass_io._lib.assertions import assert_dataclass_is_valid
from dataclass_io._lib.assertions import assert_file_is_readable
from dataclass_io._lib.assertions import assert_file_is_writable


def test_assert_dataclass_is_valid() -> None:
    """
    Test that we can validate if a dataclass is valid for reading.
    """

    @dataclass
    class FakeDataclass:
        foo: str
        bar: int

    try:
        assert_dataclass_is_valid(FakeDataclass)
    except TypeError:
        raise AssertionError("Failed to validate a valid dataclass") from None


def test_assert_dataclass_is_valid_raises_if_not_a_dataclass() -> None:
    """
    Test that we raise an error if the provided type is not a dataclass.
    """

    class BadDataclass:
        foo: str
        bar: int

    with pytest.raises(TypeError, match="The provided type must be a dataclass: BadDataclass"):
        # mypy (correctly) flags that `BadDataclass` is not a dataclass.
        # We still want to test that we can enforce this at runtime, so here it's ok to ignore.
        assert_dataclass_is_valid(BadDataclass)  # type: ignore[arg-type]


def test_assert_file_is_readable(tmp_path: Path) -> None:
    """
    Test that we can validate if a file is valid for reading.
    """

    fpath = tmp_path / "test.txt"
    fpath.touch()

    try:
        assert_file_is_readable(fpath)
    except Exception:
        raise AssertionError("Failed to validate a valid file") from None


def test_assert_file_is_readable_raises_if_file_does_not_exist(tmp_path: Path) -> None:
    """
    Test that we can validate if a file does not exist.
    """

    with pytest.raises(FileNotFoundError, match="The input file does not exist: "):
        assert_file_is_readable(tmp_path / "does_not_exist.txt")


def test_assert_file_is_readable_raises_if_file_is_a_directory(tmp_path: Path) -> None:
    """
    Test that we can validate if a file does not exist.
    """

    with pytest.raises(IsADirectoryError, match="The input file path is a directory: "):
        assert_file_is_readable(tmp_path)


def test_assert_file_is_readable_raises_if_file_is_unreadable(tmp_path: Path) -> None:
    """
    Test that we can validate if a file cannot be read.
    """

    fpath = tmp_path / "test.txt"
    fpath.touch(0)

    with pytest.raises(PermissionError, match="The input file is not readable: "):
        assert_file_is_readable(fpath)


def test_assert_file_is_writable(tmp_path: Path) -> None:
    """
    Test that we can validate if a file path is valid for writing.
    """

    # Non-existing files are writable
    fpath = tmp_path / "test.txt"
    try:
        assert_file_is_writable(fpath, overwrite=False)
    except Exception:
        raise AssertionError("Failed to validate a valid file") from None

    # Existing files are writable if `overwrite=True`
    fpath.touch()
    try:
        assert_file_is_writable(fpath, overwrite=True)
    except Exception:
        raise AssertionError("Failed to validate a valid file") from None


def test_assert_file_is_writable_raises_if_file_exists(tmp_path: Path) -> None:
    """
    Test that we raise an error if the output file already exists when `overwrite=False`.
    """

    fpath = tmp_path / "test.txt"
    fpath.touch()

    with pytest.raises(FileExistsError, match="The output file already exists: "):
        assert_file_is_writable(tmp_path, overwrite=False)


def test_assert_file_is_writable_raises_if_file_is_directory(tmp_path: Path) -> None:
    """
    Test that we raise an error if the output file path exists and is a directory.
    """
    with pytest.raises(IsADirectoryError, match="The output file path is a directory: "):
        assert_file_is_writable(tmp_path, overwrite=True)


def test_assert_file_is_writable_raises_if_parent_directory_does_not_exist(tmp_path: Path) -> None:
    """
    Test that we raise an error if the parent directory of the output file path does not exist.
    """

    fpath = tmp_path / "abc" / "test.txt"

    with pytest.raises(FileNotFoundError, match="The specified directory for the output"):
        assert_file_is_writable(fpath, overwrite=True)
