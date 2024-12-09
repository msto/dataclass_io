from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def datadir() -> Path:
    """Path to the test data directory."""

    return Path(__file__).parent / "data"
