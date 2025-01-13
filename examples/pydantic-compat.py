from typing import Any

import pytest
from pydantic import BaseModel, ConfigDict, Field, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

from newtype import NewType


def is_valid_firstname_or_lastname(value: str):
    if not all(char.isalpha() for char in value):
        raise ValueError("First name must contain only alphabetic characters")
    if len(value) < 2 or len(value) > 32:
        raise ValueError("First name must be between 2 and 32 characters long")
    return


FirstOrLastNameSchema = lambda cls: core_schema.json_or_python_schema(
    json_schema=core_schema.str_schema(min_length=2, max_length=32, pattern="^[a-zA-Z]+$"),
    python_schema=core_schema.union_schema(
        [
            core_schema.is_instance_schema(cls),
            core_schema.str_schema(min_length=2, max_length=32, pattern="^[a-zA-Z]+$"),
        ]
    ),
    serialization=core_schema.str_schema(),
)


class FirstName(NewType(str)):
    def __init__(self, value: str):
        super().__init__(value)
        is_valid_firstname_or_lastname(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return FirstOrLastNameSchema(cls)


class LastName(NewType(str)):
    def __init__(self, value: str):
        super().__init__(value)
        is_valid_firstname_or_lastname(value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        return FirstOrLastNameSchema(cls)


class Person(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    first_name: FirstName = Field(..., description="The first name of the person")
    last_name: LastName = Field(..., description="The last name of the person")


def test_firstname_replace():
    first_name = FirstName("John")
    first_name = first_name.replace("John", "James")
    assert first_name == "James"
    assert isinstance(first_name, FirstName)

    with pytest.raises(ValueError):
        first_name = first_name.replace("James", "John1")


def test_pydantic_compat():
    person = Person(first_name=FirstName("John"), last_name=LastName("Doe"))
    print(person)
    assert person.first_name == "John"
    assert person.last_name == "Doe"
    assert person.model_dump_json() == '{"first_name":"John","last_name":"Doe"}'
    assert person.model_dump() == {"first_name": "John", "last_name": "Doe"}
    assert person.model_validate_json('{"first_name":"John","last_name":"Doe"}') == person
    assert person.model_validate({"first_name": "John", "last_name": "Doe"}) == person


def test_pydantic_compat_errors():
    with pytest.raises(ValueError):
        Person(first_name="John1", last_name="Doe")
    with pytest.raises(ValueError):
        Person(first_name="John", last_name="Doe1")


def test_pydantic_compat_schema():
    schema = Person.model_json_schema()
    assert schema == {
        "title": "Person",
        "type": "object",
        "properties": {
            "first_name": {
                "title": "First Name",
                "type": "string",
                "minLength": 2,
                "maxLength": 32,
                "pattern": "^[a-zA-Z]+$",
                "description": "The first name of the person",
            },
            "last_name": {
                "title": "Last Name",
                "type": "string",
                "minLength": 2,
                "maxLength": 32,
                "pattern": "^[a-zA-Z]+$",
                "description": "The last name of the person",
            },
        },
        "required": ["first_name", "last_name"],
    }


def test_pydantic_changes_name():
    class Person(BaseModel):
        model_config = ConfigDict(arbitrary_types_allowed=True)

        first_name: FirstName = Field(..., description="The first name of the person")
        last_name: LastName = Field(..., description="The last name of the person")

    james = Person(first_name=FirstName("James"), last_name=LastName("Bond"))
    james.first_name = james.first_name.replace("James", "John")
    assert james.first_name == "John"
    assert james.last_name == "Bond"

    with pytest.raises(ValueError):
        james.first_name = james.first_name.replace("John", "John1")

    assert james.first_name == "John"
    james.first_name = james.first_name.replace("Petter", "John1")
    assert james.first_name == "John"
    assert james.last_name == "Bond"

    assert isinstance(james.first_name, FirstName)
    assert isinstance(james.last_name, LastName)

    with pytest.raises(ValueError):
        james.last_name = james.last_name.replace("Bond", "Smith11")
