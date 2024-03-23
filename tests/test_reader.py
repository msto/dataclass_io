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
        f.write("abc\t1\n")

    dictreader_kwds = {"fieldnames": ["foo", "bar"], "delimiter": "\t"}
    with DataclassReader(path=fpath, dataclass_type=FakeDataclass, **dictreader_kwds) as reader:
        rows = [row for row in reader]

    assert rows[0] == FakeDataclass(foo="abc", bar=1)
