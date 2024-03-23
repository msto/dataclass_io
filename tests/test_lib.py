from dataclasses import dataclass

import pytest

from dataclass_io.lib import assert_readable_dataclass


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
