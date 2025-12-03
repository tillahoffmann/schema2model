# jsonschema2pydantic

Convert JSON Schema dictionaries to Pydantic models.

## Installation

```bash
pip install jsonschema2pydantic
```

## Usage

```python
from jsonschema2pydantic import schema2model

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
