from csv import DictReader
from pathlib import Path
from types import TracebackType
from typing import Any
from typing import Type


class DataclassReader:
    def __init__(
        self,
        path: Path,
        dc_type: type,
        **kwds: Any,
    ) -> None:
        """
        Args:
            path: Path to the file to read.
            dc_type: Dataclass type.
        """

        self._dc_type = dc_type
        self._fin = path.open("r")
        self._reader = DictReader(self._fin, **kwds)

    def __enter__(self) -> "DataclassReader":
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        self._fin.close()

    def __iter__(self) -> "DataclassReader":
        return self

    def __next__(self) -> dict[str, str]:
        return next(self._reader)
