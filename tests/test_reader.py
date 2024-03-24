from dataclasses import dataclass
from pathlib import Path

from dataclass_io.reader import DataclassReader


@dataclass
class FakeDataclass:
    foo: str
    bar: int


def test_reader(tmp_path: Path) -> None:
    fpath = tmp_path / "test.txt"

    with open(fpath, "w") as f:
        f.write("foo\tbar\n")
        f.write("abc\t1\n")

    with DataclassReader(path=fpath, dataclass_type=FakeDataclass) as reader:
        rows = [row for row in reader]

    assert rows[0] == FakeDataclass(foo="abc", bar=1)
