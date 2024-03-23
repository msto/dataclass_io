
from pathlib import Path

from dataclass_io.reader import DataclassReader


def test_reader(tmp_path: Path) -> None:

    with open(tmp_path / "test.txt", "w") as f:
        f.write("abc\n")

    with DataclassReader(tmp_path / "test.txt") as reader:
        lines = [line.strip() for line in reader]

    assert lines == ["abc"]
