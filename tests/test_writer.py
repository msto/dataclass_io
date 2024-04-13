from dataclasses import dataclass
from pathlib import Path

import pytest

from dataclass_io.writer import DataclassWriter


@dataclass
class FakeDataclass:
    foo: str
    bar: int


def test_writer(tmp_path: Path) -> None:
    fpath = tmp_path / "test.txt"

    with DataclassWriter(path=fpath, mode="write", dataclass_type=FakeDataclass) as writer:
        writer.write(FakeDataclass(foo="abc", bar=1))
        writer.write(FakeDataclass(foo="def", bar=2))

    with open(fpath, "r") as f:
        assert next(f) == "foo\tbar\n"
        assert next(f) == "abc\t1\n"
        assert next(f) == "def\t2\n"
        with pytest.raises(StopIteration):
            next(f)


def test_writer_writeall(tmp_path: Path) -> None:
    fpath = tmp_path / "test.txt"

    data = [
        FakeDataclass(foo="abc", bar=1),
        FakeDataclass(foo="def", bar=2),
    ]
    with DataclassWriter(path=fpath, mode="write", dataclass_type=FakeDataclass) as writer:
        writer.writeall(data)

    with open(fpath, "r") as f:
        assert next(f) == "foo\tbar\n"
        assert next(f) == "abc\t1\n"
        assert next(f) == "def\t2\n"
        with pytest.raises(StopIteration):
            next(f)


def test_writer_include_fields(tmp_path: Path) -> None:
    """Test that we can include only a subset of fields."""
    fpath = tmp_path / "test.txt"

    data = [
        FakeDataclass(foo="abc", bar=1),
        FakeDataclass(foo="def", bar=2),
    ]
    with DataclassWriter(
        path=fpath,
        mode="write",
        dataclass_type=FakeDataclass,
        include_fields=["foo"],
    ) as writer:
        writer.writeall(data)

    with open(fpath, "r") as f:
        assert next(f) == "foo\n"
        assert next(f) == "abc\n"
        assert next(f) == "def\n"
        with pytest.raises(StopIteration):
            next(f)


def test_writer_include_fields_reorders(tmp_path: Path) -> None:
    """Test that we can reorder the output fields."""
    fpath = tmp_path / "test.txt"

    data = [
        FakeDataclass(foo="abc", bar=1),
        FakeDataclass(foo="def", bar=2),
    ]
    with DataclassWriter(
        path=fpath,
        mode="write",
        dataclass_type=FakeDataclass,
        include_fields=["bar", "foo"],
    ) as writer:
        writer.writeall(data)

    with open(fpath, "r") as f:
        assert next(f) == "bar\tfoo\n"
        assert next(f) == "1\tabc\n"
        assert next(f) == "2\tdef\n"
        with pytest.raises(StopIteration):
            next(f)


def test_writer_exclude_fields(tmp_path: Path) -> None:
    """Test that we can exclude fields from being written."""

    fpath = tmp_path / "test.txt"

    data = [
        FakeDataclass(foo="abc", bar=1),
        FakeDataclass(foo="def", bar=2),
    ]
    with DataclassWriter(
        path=fpath,
        mode="write",
        dataclass_type=FakeDataclass,
        exclude_fields=["bar"],
    ) as writer:
        writer.writeall(data)

    with open(fpath, "r") as f:
        assert next(f) == "foo\n"
        assert next(f) == "abc\n"
        assert next(f) == "def\n"
        with pytest.raises(StopIteration):
            next(f)
