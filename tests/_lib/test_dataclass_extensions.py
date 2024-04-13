from dataclasses import dataclass

import pytest

from dataclass_io._lib.dataclass_extensions import fieldnames


def test_fieldnames() -> None:
    """Test we can get the fieldnames of a dataclass."""

    @dataclass
    class FakeDataclass:
        foo: str
        bar: int

    assert fieldnames(FakeDataclass) == ["foo", "bar"]


def test_fieldnames_raises_if_not_a_dataclass() -> None:
    """Test we raise if we get a non-dataclass."""

    class BadDataclass:
        foo: str
        bar: int

    with pytest.raises(TypeError, match="The provided type must be a dataclass: BadDataclass"):
        fieldnames(BadDataclass)  # type: ignore[arg-type]
