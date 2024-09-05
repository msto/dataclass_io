# dataclass_io

[![CI](https://github.com/msto/dataclass_io/actions/workflows/python_package.yml/badge.svg?branch=main)](https://github.com/msto/dataclass_io/actions/workflows/python_package.yml?query=branch%3Amain)
[![Python Versions](https://img.shields.io/badge/python-3.10_|_3.11_|_3.12-blue)](https://github.com/msto/dataclass_io)
[![MyPy Checked](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)

Read and write dataclasses.

`dataclass_io` provides similar functionality to the standard library's `csv.DictReader` and `csv.DictWriter`, and adds type safety.

## Installation

`dataclass_io` may be installed via `pip`:

```console
pip install dataclass_io
```

## Quickstart

### Reading

```py
from dataclasses import dataclass
from dataclass_io import DataclassReader


@dataclass
class MyData:
    foo: int
    bar: str


with open("test.tsv", "w") as testfile:
    testfile.write("foo\tbar\n")
    testfile.write("1\tabc\n")
    testfile.write("2\tdef\n")

with DataclassReader.open("test.tsv", MyData) as reader:
    for record in reader:
        print(record.foo)
```

### Writing
```py
from dataclasses import dataclass
from dataclass_io import DataclassWriter


@dataclass
class MyData:
    foo: int
    bar: str


with DataclassWriter.open("test.tsv", MyData) as writer:
    for i in range(3):
        record = MyData(foo=i, bar="something")
        writer.write(record)
```
