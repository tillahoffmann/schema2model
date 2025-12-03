# schema2model

[![CI](https://github.com/tillahoffmann/schema2model/actions/workflows/main.yml/badge.svg)](https://github.com/tillahoffmann/schema2model/actions/workflows/main.yml)
[![PyPI](https://img.shields.io/pypi/v/schema2model)](https://pypi.org/project/schema2model/)

Convert JSON Schema dictionaries to Pydantic models.

## Installation

```bash
pip install schema2model
```

## Usage

```python
from schema2model import schema2model

schema = {
    "title": "User",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    },
    "required": ["name", "age"]
}

User = schema2model(schema)
user = User(name="Alice", age=30)
```

## Supported Features

- Basic types: `str`, `int`, `float`, `bool`
- Collections: `list`, `set`, `tuple`, `dict`
- Date/time: `datetime`, `date`, `time`, `timedelta`
- Special types: `UUID`, `bytes`, `AnyHttpUrl`
- Nested models and enums
- Recursive models
- `RootModel`
- Discriminated unions
- Field constraints (`gt`, `lt`, `min_length`, `pattern`, etc.)
- Field metadata (`description`, `examples`, `deprecated`)
