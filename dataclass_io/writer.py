from contextlib import contextmanager
from csv import DictWriter
from dataclasses import asdict
from pathlib import Path
from typing import Any
from typing import Iterable
from typing import Iterator

from dataclass_io._lib.assertions import assert_dataclass_is_valid
from dataclass_io._lib.assertions import assert_fieldnames_are_dataclass_attributes
from dataclass_io._lib.assertions import assert_file_header_matches_dataclass
from dataclass_io._lib.assertions import assert_file_is_appendable
from dataclass_io._lib.assertions import assert_file_is_writable
from dataclass_io._lib.dataclass_extensions import DataclassInstance
from dataclass_io._lib.dataclass_extensions import fieldnames
from dataclass_io._lib.file import WritableFileHandle
from dataclass_io._lib.file import WriteMode


class DataclassWriter:
    _dataclass_type: type[DataclassInstance]
    _fieldnames: list[str]
    _fout: WritableFileHandle
    _writer: DictWriter

    def __init__(
        self,
        fout: WritableFileHandle,
        dataclass_type: type[DataclassInstance],
        delimiter: str = "\t",
        include_fields: list[str] | None = None,
        exclude_fields: list[str] | None = None,
        write_header: bool = True,
        **kwds: Any,
    ) -> None:
        """
        Args:
            fout: Open file handle for writing.
            dataclass_type: Dataclass type.
            delimiter: The output file delimiter.
            include_fields: If specified, only the listed fieldnames will be included when writing
                records to file. Fields will be written in the order provided.
                May not be used together with `exclude_fields`.
            exclude_fields: If specified, any listed fieldnames will be excluded when writing
                records to file.
                May not be used together with `include_fields`.
            write_header: If True, a header row consisting of the dataclass's fieldnames will be
                written before any records are written (including or excluding any fields specified
                by `include_fields` or `exclude_fields`).

        Raises:
            TypeError: If the provided type is not a dataclass.
            ValueError: If both `include_fields` and `exclude_fields` are specified.
        """
        assert_dataclass_is_valid(dataclass_type)

        self._dataclass_type = dataclass_type
        self._fieldnames = _validate_output_fieldnames(
            dataclass_type=dataclass_type,
            include_fields=include_fields,
            exclude_fields=exclude_fields,
        )
        self._fout = fout
        self._writer = DictWriter(
            f=self._fout,
            fieldnames=self._fieldnames,
            delimiter=delimiter,
        )

        # TODO: permit writing comment/preface rows before header
        if write_header:
            self._writer.writeheader()

    def write(self, dataclass_instance: DataclassInstance) -> None:
        """
        Write a single dataclass instance to file.

        The dataclass is converted to a dictionary and then written using the underlying
        `csv.DictWriter`. If the `DataclassWriter` was created using the `include_fields` or
        `exclude_fields` arguments, the attributes of the dataclass are subset and/or reordered
        accordingly before writing.

        Args:
            dataclass_instance: An instance of the specified dataclass.

        Raises:
            ValueError: If the provided instance is not an instance of the writer's dataclass.
        """

        # TODO: consider permitting other dataclass types *if* they contain the required attributes
        if not isinstance(dataclass_instance, self._dataclass_type):
            raise ValueError(f"Must provide instances of {self._dataclass_type.__name__}")

        # Filter and/or re-order output fields if necessary
        row = asdict(dataclass_instance)
        row = {fieldname: row[fieldname] for fieldname in self._fieldnames}

        self._writer.writerow(row)

    def writeall(self, dataclass_instances: Iterable[DataclassInstance]) -> None:
        """
        Write multiple dataclass instances to file.

        Each dataclass is converted to a dictionary and then written using the underlying
        `csv.DictWriter`. If the `DataclassWriter` was created using the `include_fields` or
        `exclude_fields` arguments, the attributes of each dataclass are subset and/or reordered
        accordingly before writing.

        Args:
            dataclass_instances: A sequence of instances of the specified dataclass.

        Raises:
            ValueError: If any of the provided instances are not an instance of the writer's
                dataclass.
        """
        for dataclass_instance in dataclass_instances:
            self.write(dataclass_instance)

    @classmethod
    @contextmanager
    def open(
        cls,
        filename: str | Path,
        dataclass_type: type[DataclassInstance],
        mode: str = "write",
        overwrite: bool = True,
        delimiter: str = "\t",
        comment_prefix: str = "#",
        **kwds: Any,
    ) -> Iterator["DataclassWriter"]:
        """
        Open a new `DataclassWriter` from a file path.

        Args:
            filename: The path to the file to which dataclass instances will be written.
            dataclass_type: The dataclass type to write to file.
            mode: Either `"write"` or `"append"`.
                - If `"write"`, the specified file `path` must not already exist unless
                `overwrite=True` is specified.
                - If `"append"`, the specified file `path` must already exist and contain a header
                row matching the specified dataclass and any specified `include_fields` or
                `exclude_fields`.
            overwrite: If `True`, and `mode="write"`, the file specified at `path` will be
                overwritten if it exists.
            delimiter: The output file delimiter.
            comment_prefix: The prefix for any comment/preface rows preceding the header row.
                (This argument is ignored when `mode="write"`. It is used when `mode="append"` to
                validate that the existing file's header matches the specified dataclass.)
            **kwds: Additional keyword arguments to be passed to the `DataclassWriter` constructor.

        Yields:
            A `DataclassWriter` instance.

        Raises:
            TypeError: If the provided type is not a dataclass.
            FileNotFoundError: If the output file does not exist when trying to append.
            IsADirectoryError: If the output file path is a directory.
            PermissionError: If the output file is not writable.
            PermissionError: If `mode="append"` and the output file is not readable. (The output
                file must be readable in order to validate that the existing file's header matches
                the dataclass's fields.)
        """

        filepath: Path = Path(filename)

        try:
            write_mode = WriteMode(mode)
        except ValueError:
            raise ValueError(f"`mode` must be either 'write' or 'append': {mode}") from None

        assert_dataclass_is_valid(dataclass_type)
        if write_mode is WriteMode.WRITE:
            assert_file_is_writable(filepath, overwrite=overwrite)
        else:
            assert_file_is_appendable(filepath, dataclass_type=dataclass_type)
            assert_file_header_matches_dataclass(
                file=filepath,
                dataclass_type=dataclass_type,
                delimiter=delimiter,
                comment_prefix=comment_prefix,
            )

        fout = filepath.open(write_mode.abbreviation)
        try:
            yield cls(
                fout=fout,
                dataclass_type=dataclass_type,
                write_header=(write_mode is WriteMode.WRITE),  # Skip header when appending
                **kwds,
            )
        finally:
            fout.close()


def _validate_output_fieldnames(
    dataclass_type: type[DataclassInstance],
    include_fields: list[str] | None = None,
    exclude_fields: list[str] | None = None,
) -> list[str]:
    """
    Subset and/or re-order the dataclass's fieldnames based on the specified include/exclude lists.

    * Only one of `include_fields` and `exclude_fields` may be specified.
    * All fieldnames specified in `include_fields` must be fields on `dataclass_type`. If this
      argument is specified, fields will be returned in the order they appear in the list.
    * All fieldnames specified in `exclude_fields` must be fields on `dataclass_type`. (This is
      technically unnecessary, but is a safeguard against passing an incorrect list.)
    * If neither `include_fields` or `exclude_fields` are specified, return the `dataclass_type`'s
      fieldnames.

    Raises:
        ValueError: If both `include_fields` and `exclude_fields` are specified.
    """

    if include_fields is not None and exclude_fields is not None:
        raise ValueError(
            "Only one of `include_fields` and `exclude_fields` may be specified, not both."
        )
    elif exclude_fields is not None:
        assert_fieldnames_are_dataclass_attributes(exclude_fields, dataclass_type)
        output_fieldnames = [f for f in fieldnames(dataclass_type) if f not in exclude_fields]
    elif include_fields is not None:
        assert_fieldnames_are_dataclass_attributes(include_fields, dataclass_type)
        output_fieldnames = include_fields
    else:
        output_fieldnames = fieldnames(dataclass_type)

    return output_fieldnames
