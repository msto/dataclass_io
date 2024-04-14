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

    with DataclassWriter(filename=fpath, mode="write", dataclass_type=FakeDataclass) as writer:
        writer.write(FakeDataclass(foo="abc", bar=1))
        writer.write(FakeDataclass(foo="def", bar=2))

    with fpath.open("r") as f:
        assert next(f) == "foo\tbar\n"
        assert next(f) == "abc\t1\n"
        assert next(f) == "def\t2\n"
        with pytest.raises(StopIteration):
            next(f)


def test_writer_from_str(tmp_path: Path) -> None:
    """Test that we can create a writer when `filename` is a `str`."""
    fpath = tmp_path / "test.txt"

    with DataclassWriter(filename=str(fpath), mode="write", dataclass_type=FakeDataclass) as writer:
        writer.write(FakeDataclass(foo="abc", bar=1))

    with fpath.open("r") as f:
        assert next(f) == "foo\tbar\n"
        assert next(f) == "abc\t1\n"
        with pytest.raises(StopIteration):
            next(f)


def test_writer_writeall(tmp_path: Path) -> None:
    fpath = tmp_path / "test.txt"

    data = [
        FakeDataclass(foo="abc", bar=1),
        FakeDataclass(foo="def", bar=2),
    ]
    with DataclassWriter(filename=fpath, mode="write", dataclass_type=FakeDataclass) as writer:
        writer.writeall(data)

    with fpath.open("r") as f:
        assert next(f) == "foo\tbar\n"
        assert next(f) == "abc\t1\n"
        assert next(f) == "def\t2\n"
        with pytest.raises(StopIteration):
            next(f)


def test_writer_append(tmp_path: Path) -> None:
    """Test that we can append to a file."""
    fpath = tmp_path / "test.txt"

    with fpath.open("w") as fout:
        fout.write("foo\tbar\n")

    with DataclassWriter(filename=fpath, mode="append", dataclass_type=FakeDataclass) as writer:
        writer.write(FakeDataclass(foo="abc", bar=1))
        writer.write(FakeDataclass(foo="def", bar=2))

    with fpath.open("r") as f:
        assert next(f) == "foo\tbar\n"
        assert next(f) == "abc\t1\n"
        assert next(f) == "def\t2\n"
        with pytest.raises(StopIteration):
            next(f)


def test_writer_append_raises_if_empty(tmp_path: Path) -> None:
    """Test that we raise an error if we try to append to an empty file."""
    fpath = tmp_path / "test.txt"
    fpath.touch()

    with pytest.raises(ValueError, match="The specified output file is empty"):
        with DataclassWriter(filename=fpath, mode="append", dataclass_type=FakeDataclass) as writer:
            writer.write(FakeDataclass(foo="abc", bar=1))


def test_writer_append_raises_if_no_header(tmp_path: Path) -> None:
    """Test that we raise an error if we try to append to a file with no header."""
    fpath = tmp_path / "test.txt"
    with fpath.open("w") as fout:
        fout.write("abc\t1\n")

    with pytest.raises(ValueError, match="The provided file does not have the same field names"):
        with DataclassWriter(filename=fpath, mode="append", dataclass_type=FakeDataclass) as writer:
            writer.write(FakeDataclass(foo="abc", bar=1))


def test_writer_append_raises_if_header_does_not_match(tmp_path: Path) -> None:
    """
    Test that we raise an error if we try to append to a file whose header doesn't match our
    dataclass.
    """
    fpath = tmp_path / "test.txt"

    with fpath.open("w") as fout:
        fout.write("foo\tbar\tbaz\n")

    with pytest.raises(ValueError, match="The provided file does not have the same field names"):
        with DataclassWriter(filename=fpath, mode="append", dataclass_type=FakeDataclass) as writer:
            writer.write(FakeDataclass(foo="abc", bar=1))


def test_writer_include_fields(tmp_path: Path) -> None:
    """Test that we can include only a subset of fields."""
    fpath = tmp_path / "test.txt"

    data = [
        FakeDataclass(foo="abc", bar=1),
        FakeDataclass(foo="def", bar=2),
    ]
    with DataclassWriter(
        filename=fpath,
        mode="write",
        dataclass_type=FakeDataclass,
        include_fields=["foo"],
    ) as writer:
        writer.writeall(data)

    with fpath.open("r") as f:
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
        filename=fpath,
        mode="write",
        dataclass_type=FakeDataclass,
        include_fields=["bar", "foo"],
    ) as writer:
        writer.writeall(data)

    with fpath.open("r") as f:
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
        filename=fpath,
        mode="write",
        dataclass_type=FakeDataclass,
        exclude_fields=["bar"],
    ) as writer:
        writer.writeall(data)

    with fpath.open("r") as f:
        assert next(f) == "foo\n"
        assert next(f) == "abc\n"
        assert next(f) == "def\n"
        with pytest.raises(StopIteration):
            next(f)
