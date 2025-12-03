import pytest
from examples.bytes_model import BytesModel
from examples.constrained_model import Person as ConstrainedPerson
from examples.datetime_model import Event
from examples.discriminated_union_model import Owner
from examples.enum_model import Person
from examples.field_metadata_model import FieldMetadataModel
from examples.foobar_model import FooBarModel
from examples.int_enum_model import Task as IntEnumTask
from examples.list_model import ListModel
from examples.literal_model import Cat, Dog
from examples.multi_literal_model import Task as MultiLiteralTask
from examples.nested_models import Spam
from examples.pattern_model import PatternModel
from examples.recursive_model import Node
from examples.root_model import IntMapping, StringList
from examples.set_model import TagContainer
from examples.simple_model import SimpleModel
from examples.tuple_model import Coordinates
from examples.url_model import UrlModel
from examples.user import User
from examples.uuid_model import Entity
from pydantic import BaseModel

from jsonschema2pydantic import schema2model


@pytest.mark.parametrize(
    "model",
    [
        User,
        Spam,
        Person,
        Cat,
        Dog,
        SimpleModel,
        FooBarModel,
        ListModel,
        Coordinates,
        TagContainer,
        Entity,
        Event,
        ConstrainedPerson,
        MultiLiteralTask,
        Owner,
        IntEnumTask,
        PatternModel,
        BytesModel,
        UrlModel,
        Node,
        StringList,
        IntMapping,
        FieldMetadataModel,
    ],
)
def test_schema2model(model: type[BaseModel]) -> None:
    """This test converts a Pydantic model to a json schema and tries to reconstruct the
    model. We verify if the reconstruction was successful in the json schema domain
    because comparing basic containers is easier than comparing Pydantic models.
    """
    schema = model.model_json_schema()
    reconstructed = schema2model(schema)
    reconstructed_schema = reconstructed.model_json_schema()
    assert schema == reconstructed_schema
