from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import Annotated, Any, Literal
from uuid import UUID

from pydantic import AnyHttpUrl, BaseModel, Field, PositiveInt, RootModel, create_model


def _schema_to_type(
    prop_schema: dict, models: dict[str, Any], building: set[str] | None = None
) -> Any:
    """Convert a JSON Schema property definition to a Python type annotation."""
    if building is None:
        building = set()

    # Handle $ref references to other models/enums
    if "$ref" in prop_schema:
        ref = prop_schema["$ref"]
        # Extract model name from "#/$defs/ModelName"
        if ref.startswith("#/$defs/"):
            model_name = ref.split("/")[-1]
            # If we're currently building this model (recursive), use forward ref
            if model_name in building:
                return model_name  # Forward reference as string
            if model_name in models:
                return models[model_name]
            # Model not built yet - this shouldn't happen with proper ordering
            return model_name  # Forward reference as string
        return Any

    # Handle const (Literal types with single value)
    if "const" in prop_schema:
        const_value = prop_schema["const"]
        return Literal[const_value]

    # Handle enum in properties (multi-value Literal)
    if "enum" in prop_schema:
        enum_values = prop_schema["enum"]
        # Create a Literal type with all enum values
        return Literal[tuple(enum_values)]

    # Handle oneOf (discriminated unions)
    if "oneOf" in prop_schema:
        one_of_types = prop_schema["oneOf"]
        union_types = []
        for item in one_of_types:
            item_type = _schema_to_type(item, models, building)
            union_types.append(item_type)
        if len(union_types) == 1:
            return union_types[0]
        # Build Union type
        result = union_types[0]
        for t in union_types[1:]:
            result = result | t
        # Handle discriminator
        if "discriminator" in prop_schema:
            disc = prop_schema["discriminator"]
            prop_name = disc.get("propertyName")
            return Annotated[result, Field(discriminator=prop_name)]
        return result

    # Handle anyOf (typically used for Optional types)
    if "anyOf" in prop_schema:
        types = prop_schema["anyOf"]
        # Check for nullable pattern: [{actual_type}, {type: "null"}]
        non_null_types = [t for t in types if t.get("type") != "null"]
        has_null = any(t.get("type") == "null" for t in types)

        if len(non_null_types) == 1 and has_null:
            inner_type = _schema_to_type(non_null_types[0], models, building)
            return inner_type | None

        # For more complex anyOf, just use Any for now
        return Any

    schema_type = prop_schema.get("type")

    if schema_type == "integer":
        constraints = _get_numeric_constraints(prop_schema)
        # Check for PositiveInt (only exclusiveMinimum: 0, no other constraints)
        if constraints == {"gt": 0}:
            return PositiveInt
        if constraints:
            return Annotated[int, Field(**constraints)]
        return int

    if schema_type == "string":
        fmt = prop_schema.get("format")
        if fmt == "date-time":
            return datetime
        if fmt == "date":
            return date
        if fmt == "time":
            return time
        if fmt == "duration":
            return timedelta
        if fmt == "uuid":
            return UUID
        if fmt == "binary":
            return bytes
        if fmt == "uri":
            # Handle AnyHttpUrl with minLength constraint
            constraints = _get_string_constraints(prop_schema)
            if constraints:
                return Annotated[AnyHttpUrl, Field(**constraints)]
            return AnyHttpUrl
        # Handle string constraints
        constraints = _get_string_constraints(prop_schema)
        if constraints:
            return Annotated[str, Field(**constraints)]
        return str

    if schema_type == "object":
        # Check for dict with additionalProperties
        if "additionalProperties" in prop_schema:
            value_type = _schema_to_type(
                prop_schema["additionalProperties"], models, building
            )
            return dict[str, value_type]
        return dict

    if schema_type == "boolean":
        return bool

    if schema_type == "number":
        constraints = _get_numeric_constraints(prop_schema)
        if constraints:
            return Annotated[float, Field(**constraints)]
        return float

    if schema_type == "array":
        # Check for tuple (prefixItems)
        if "prefixItems" in prop_schema:
            prefix_types = [
                _schema_to_type(item, models, building)
                for item in prop_schema["prefixItems"]
            ]
            return tuple[tuple(prefix_types)]

        # Check for set/frozenset (uniqueItems)
        if prop_schema.get("uniqueItems"):
            if "items" in prop_schema:
                item_type = _schema_to_type(prop_schema["items"], models, building)
                return set[item_type]
            return set

        # Regular list
        if "items" in prop_schema:
            item_type = _schema_to_type(prop_schema["items"], models, building)
            return list[item_type]
        return list

    if schema_type == "null":
        return None

    return Any


def _get_numeric_constraints(prop_schema: dict) -> dict[str, Any]:
    """Extract numeric constraints from schema."""
    constraints = {}
    if "exclusiveMinimum" in prop_schema:
        constraints["gt"] = prop_schema["exclusiveMinimum"]
    if "exclusiveMaximum" in prop_schema:
        constraints["lt"] = prop_schema["exclusiveMaximum"]
    if "minimum" in prop_schema:
        constraints["ge"] = prop_schema["minimum"]
    if "maximum" in prop_schema:
        constraints["le"] = prop_schema["maximum"]
    if "multipleOf" in prop_schema:
        constraints["multiple_of"] = prop_schema["multipleOf"]
    return constraints


def _get_string_constraints(prop_schema: dict) -> dict[str, Any]:
    """Extract string constraints from schema."""
    constraints = {}
    if "minLength" in prop_schema:
        constraints["min_length"] = prop_schema["minLength"]
    if "maxLength" in prop_schema:
        constraints["max_length"] = prop_schema["maxLength"]
    if "pattern" in prop_schema:
        constraints["pattern"] = prop_schema["pattern"]
    return constraints


def _get_field_metadata(prop_schema: dict) -> dict[str, Any]:
    """Extract field metadata (description, examples, deprecated) from schema."""
    metadata = {}
    if "description" in prop_schema:
        metadata["description"] = prop_schema["description"]
    if "examples" in prop_schema:
        metadata["examples"] = prop_schema["examples"]
    if "deprecated" in prop_schema:
        metadata["deprecated"] = prop_schema["deprecated"]
    return metadata


def _build_enum(name: str, schema: dict) -> type[Enum]:
    """Build an Enum class from a schema with enum values."""
    enum_values = schema.get("enum", [])
    schema_type = schema.get("type", "string")

    # Create enum members as name=value pairs
    members = {str(v): v for v in enum_values}

    # Determine base class based on type
    if schema_type == "string":
        return Enum(name, members, type=str)  # type: ignore[return-value]
    elif schema_type == "integer":
        return Enum(name, members, type=int)  # type: ignore[return-value]
    else:
        return Enum(name, members)  # type: ignore[return-value]


def _build_model(
    schema: dict, models: dict[str, Any], building: set[str] | None = None
) -> type[BaseModel]:
    """Build a single model from a schema, using existing models for references."""
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    title = schema.get("title", "DynamicModel")

    if building is None:
        building = set()
    building = building | {title}  # Mark this model as being built

    field_definitions: dict[str, Any] = {}

    for prop_name, prop_schema in properties.items():
        python_type = _schema_to_type(prop_schema, models, building)
        default = prop_schema.get("default", ...)
        metadata = _get_field_metadata(prop_schema)

        if prop_name not in required and default is ...:
            default = ...

        # If we have metadata, use Field to attach it
        if metadata:
            if default is ...:
                field_definitions[prop_name] = (python_type, Field(**metadata))
            else:
                field_definitions[prop_name] = (
                    python_type,
                    Field(default=default, **metadata),
                )
        elif default is ...:
            field_definitions[prop_name] = (python_type, ...)
        else:
            field_definitions[prop_name] = (python_type, default)

    model = create_model(title, **field_definitions)

    # Store model immediately so recursive refs can find it
    models[title] = model

    # Rebuild to resolve forward references
    model.model_rebuild()

    return model


def _topological_sort_defs(defs: dict[str, dict]) -> list[str]:
    """Sort $defs by dependency order (models with no deps first)."""
    # Build dependency graph
    deps: dict[str, set[str]] = {}
    for name, schema in defs.items():
        deps[name] = set()
        # Find all $ref references in this schema
        _find_refs(schema, deps[name])
        # Remove self-references (recursive models)
        deps[name].discard(name)

    # Topological sort using Kahn's algorithm
    result = []
    in_degree = {name: 0 for name in defs}
    for name, dependencies in deps.items():
        for dep in dependencies:
            if dep in in_degree:
                in_degree[name] += 1

    queue = [name for name, degree in in_degree.items() if degree == 0]

    while queue:
        node = queue.pop(0)
        result.append(node)
        for name, dependencies in deps.items():
            if node in dependencies:
                in_degree[name] -= 1
                if in_degree[name] == 0 and name not in result:
                    queue.append(name)

    return result


def _find_refs(schema: dict, refs: set[str]) -> None:
    """Recursively find all $ref references in a schema."""
    if isinstance(schema, dict):
        if "$ref" in schema:
            ref = schema["$ref"]
            if ref.startswith("#/$defs/"):
                refs.add(ref.split("/")[-1])
        for value in schema.values():
            _find_refs(value, refs)
    elif isinstance(schema, list):
        for item in schema:
            _find_refs(item, refs)


def _build_root_model(
    schema: dict, models: dict[str, Any], title: str
) -> type[RootModel]:  # type: ignore[type-arg]
    """Build a RootModel from a schema without properties."""
    root_type = _schema_to_type(schema, models, set())

    # Create a RootModel subclass with the correct root type
    class DynamicRootModel(RootModel[root_type]):  # type: ignore[valid-type]
        pass

    DynamicRootModel.__name__ = title
    DynamicRootModel.__qualname__ = title
    return DynamicRootModel


def schema2model(schema: dict) -> type[BaseModel]:
    """Convert a JSON Schema dictionary to a Pydantic BaseModel class."""
    models: dict[str, Any] = {}

    # First, build all models/enums from $defs in dependency order
    defs = schema.get("$defs", {})
    if defs:
        sorted_names = _topological_sort_defs(defs)
        for name in sorted_names:
            def_schema = defs[name]
            # Check if this is an enum definition
            if "enum" in def_schema:
                models[name] = _build_enum(name, def_schema)
            else:
                models[name] = _build_model(def_schema, models)

    # Check if root schema is just a $ref (recursive model case)
    if "$ref" in schema and "properties" not in schema:
        ref = schema["$ref"]
        if ref.startswith("#/$defs/"):
            model_name = ref.split("/")[-1]
            return models[model_name]

    # Check if this is a RootModel (no properties, direct type)
    if "properties" not in schema:
        title = schema.get("title", "DynamicRootModel")
        return _build_root_model(schema, models, title)

    # Build the main model
    return _build_model(schema, models)
