from dataclasses import dataclass
from pathlib import Path

from dataclass_io.reader import DataclassReader


@dataclass(kw_only=True, eq=True)
class FakeDataclass:
    foo: str
    bar: int


def test_reader(tmp_path: Path) -> None:
    fpath = tmp_path / "test.txt"

    with fpath.open("w") as f:
        f.write("foo\tbar\n")
        f.write("abc\t1\n")

    with DataclassReader.open(filename=fpath, dataclass_type=FakeDataclass) as reader:
        rows = [row for row in reader]

    assert rows[0] == FakeDataclass(foo="abc", bar=1)


def test_reader_from_str(tmp_path: Path) -> None:
    """Test that we can create a reader when `filename` is a `str`."""
    fpath = tmp_path / "test.txt"

    with fpath.open("w") as f:
        f.write("foo\tbar\n")
        f.write("abc\t1\n")

    with DataclassReader.open(filename=str(fpath), dataclass_type=FakeDataclass) as reader:
        rows = [row for row in reader]

    assert rows[0] == FakeDataclass(foo="abc", bar=1)
