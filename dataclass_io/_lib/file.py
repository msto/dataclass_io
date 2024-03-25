from dataclasses import dataclass
from io import TextIOWrapper
from typing import IO
from typing import Optional
from typing import TextIO
from typing import TypeAlias

ReadableFileHandle: TypeAlias = TextIOWrapper | IO | TextIO


@dataclass(frozen=True, kw_only=True)
class FileHeader:
    """
    Header of a file.

    A file's header contains an optional preface, consisting of lines prefixed by a comment
    character and/or empty lines, and a required row of fieldnames before the data rows begin.

    Attributes:
        preface: A list of any lines preceding the fieldnames.
        fieldnames: The field names specified in the final line of the header.
    """

    preface: list[str]
    fieldnames: list[str]


def get_header(
    reader: ReadableFileHandle,
    delimiter: str = "\t",
    header_comment_char: str = "#",
) -> Optional[FileHeader]:
    """
    Read the header from an open file.

    The first row after any commented or empty lines will be used as the fieldnames.

    Lines preceding the fieldnames will be returned in the `preface.`

    NB: This function returns `Optional` instead of raising an error because the name of the
    source file is not in scope, making it difficult to provide a helpful error message. It is
    the responsibility of the caller to raise an error if the file is empty.

    See original proof-of-concept here: https://github.com/fulcrumgenomics/fgpyo/pull/103

    Args:
        reader: An open, readable file handle.
        comment_char: The character which indicates the start of a comment line.

    Returns:
        A `FileHeader` containing the field names and any preceding lines.
        None if the file was empty or contained only comments or empty lines.
    """

    preface: list[str] = []

    for line in reader:
        if line.startswith(header_comment_char) or line.strip() == "":
            preface.append(line.strip())
        else:
            break
    else:
        return None

    fieldnames = line.strip().split(delimiter)

    return FileHeader(preface=preface, fieldnames=fieldnames)
