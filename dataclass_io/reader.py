
from pathlib import Path
from types import TracebackType
from typing import Type


class DataclassReader:
    def __init__(self, path: Path):

        self._reader = path.open("r")

    def __enter__(self) -> "DataclassReader":
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        self._reader.close()

    def __iter__(self) -> "DataclassReader":
        return self

    def __next__(self) -> str:
        return next(self._reader)
