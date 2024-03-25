# dataclass_io

[![CI](https://github.com/msto/dataclass_io/actions/workflows/python_package.yml/badge.svg?branch=main)](https://github.com/msto/dataclass_io/actions/workflows/python_package.yml?query=branch%3Amain)
[![Python Versions](https://img.shields.io/badge/python-3.11_|_3.12-blue)](https://github.com/msto/dataclass_io)
[![MyPy Checked](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://docs.astral.sh/ruff/)

Dataclass IO.

## Usage

```py
from dataclasses import dataclass
from dataclass_io import DataclassReader


@dataclass
class MyData:
    foo: int
    bar: str


with DataclassReader(path, MyData) as reader:
    for record in reader:
        do_something(record.foo)
```


```py
from dataclasses import dataclass
from dataclass_io import DataclassWriter


@dataclass
class MyData:
    foo: int
    bar: str


with DataclassWriter(path, MyData) as writer:
    for i in range(3):
        record = MyData(foo=i, bar="something")
        writer.write(record)
```
