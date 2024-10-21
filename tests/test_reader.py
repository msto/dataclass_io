from dataclasses import dataclass
from pathlib import Path
from typing import cast

import pytest

from dataclass_io.reader import DataclassReader


@pytest.mark.parametrize("kw_only", [True, False])
@pytest.mark.parametrize("eq", [True, False])
@pytest.mark.parametrize("frozen", [True, False])
def test_reader(kw_only: bool, eq: bool, frozen: bool, tmp_path: Path) -> None:
    fpath = tmp_path / "test.txt"

    @dataclass(frozen=frozen, eq=eq, kw_only=kw_only)  # type: ignore[literal-required]
    class FakeDataclass:
        foo: str
        bar: int

    with fpath.open("w") as f:
        f.write("foo\tbar\n")
        f.write("abc\t1\n")

    rows: list[FakeDataclass]
    with DataclassReader.open(filename=fpath, dataclass_type=FakeDataclass) as reader:
        # TODO make `DataclassReader` generic
        rows = cast(list[FakeDataclass], [row for row in reader])

    assert len(rows) == 1

    if eq:
        assert rows[0] == FakeDataclass(foo="abc", bar=1)
    else:
        assert isinstance(rows[0], FakeDataclass)
        assert rows[0].foo == "abc"
        assert rows[0].bar == 1
