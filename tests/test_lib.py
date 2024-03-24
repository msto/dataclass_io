from dataclasses import dataclass
from pathlib import Path

import pytest

from dataclass_io.lib import assert_readable_dataclass
from dataclass_io.lib import assert_readable_file


def test_assert_readable_dataclass() -> None:
    """
    Test that we can validate if a dataclass is valid for reading.
    """

    @dataclass
    class FakeDataclass:
        foo: str
        bar: int

    try:
        assert_readable_dataclass(FakeDataclass)
    except TypeError:
        raise AssertionError("Failed to validate a valid dataclass") from None


def test_assert_readable_dataclass_raises_if_not_a_dataclass() -> None:
    """
    Test that we raise an error if the provided type is not a dataclass.
    """

    class BadDataclass:
        foo: str
        bar: int

    with pytest.raises(TypeError, match="The provided type must be a dataclass: BadDataclass"):
        assert_readable_dataclass(BadDataclass)


def test_assert_readable_file(tmp_path: Path) -> None:
    """
    Test that we can validate if a file is valid for reading.
    """

    fpath = tmp_path / "test.txt"
    fpath.touch()

    try:
        assert_readable_file(fpath)
    except Exception:
        raise AssertionError("Failed to validate a valid file") from None


def test_assert_readable_file_raises_if_file_does_not_exist(tmp_path: Path) -> None:
    """
    Test that we can validate if a file does not exist.
    """

    with pytest.raises(FileNotFoundError, match="The input file does not exist: "):
        assert_readable_file(tmp_path / "does_not_exist.txt")


def test_assert_readable_file_raises_if_file_is_a_directory(tmp_path: Path) -> None:
    """
    Test that we can validate if a file does not exist.
    """

    with pytest.raises(IsADirectoryError, match="The input file path is a directory: "):
        assert_readable_file(tmp_path)


def test_assert_readable_file_raises_if_file_is_unreadable(tmp_path: Path) -> None:
    """
    Test that we can validate if a file cannot be read.
    """

    fpath = tmp_path / "test.txt"
    fpath.touch(0)

    with pytest.raises(PermissionError, match="The input file is not readable: "):
        assert_readable_file(fpath)
