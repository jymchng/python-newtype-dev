# Using python-newtype with Pydantic

This guide demonstrates how to effectively use python-newtype with Pydantic to create robust, type-safe data models with custom validation.

## Overview

When building APIs or data-intensive applications, you often need to ensure that your data adheres to specific validation rules. While Pydantic provides excellent validation capabilities, combining it with python-newtype enhances your data modeling capabilities in several important ways.

Python-newtype enables you to create reusable, type-safe custom fields that maintain their type information throughout your entire codebase. This means you can define specialized types once and reuse them across multiple models, ensuring consistent behavior and validation.

With python-newtype, you can add domain-specific validation logic directly to your custom types. This validation becomes an inherent part of the type itself, ensuring that any instance of that type always meets your business requirements. The validation is enforced at the type level, making it impossible to create invalid instances.

The combination of python-newtype and Pydantic ensures consistent data handling across your application. Whether you're serializing to JSON, validating incoming data, or manipulating objects in your business logic, you can be confident that your data maintains its integrity and type safety throughout its lifecycle.

## Basic Example

Let's look at a practical example of creating a Person model with validated first and last names:

```python
from typing import Any
from newtype import NewType
from pydantic import BaseModel, ConfigDict, Field, GetCoreSchemaHandler
from pydantic_core import core_schema, CoreSchema

def is_valid_firstname_or_lastname(value: str):
    if not all(char.isalpha() for char in value):
        raise ValueError("Name must contain only alphabetic characters")
    if len(value) < 2 or len(value) > 32:
        raise ValueError("Name must be between 2 and 32 characters long")
    return

class FirstName(NewType(str)):
    def __init__(self, value: str):
        super().__init__(value)
        is_valid_firstname_or_lastname(value)

class LastName(NewType(str)):
    def __init__(self, value: str):
        super().__init__(value)
        is_valid_firstname_or_lastname(value)

class Person(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    first_name: FirstName = Field(..., description="The first name of the person")
    last_name: LastName = Field(..., description="The last name of the person")
```

In this example:
- We create custom `FirstName` and `LastName` types that inherit from `str`
- Each type includes validation to ensure names contain only letters and are between 2-32 characters
- We use these types in a Pydantic model with proper field descriptions

## Advanced Validation with Pydantic Core Schema

To provide even more robust validation and better JSON schema support, you can implement Pydantic's core schema:

```python
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
```

This setup provides:
- JSON schema validation for API documentation
- Runtime validation for both JSON and Python objects
- Proper serialization behavior

## Usage Examples

### Basic Model Creation

```python
# Create a person with valid names
person = Person(first_name=FirstName("John"), last_name=LastName("Doe"))

# Access the values
print(person.first_name)  # Output: John
print(person.last_name)   # Output: Doe
```

### JSON Serialization

```python
# Serialize to JSON
json_data = person.model_dump_json()
print(json_data)  # Output: {"first_name":"John","last_name":"Doe"}

# Deserialize from JSON
person2 = Person.model_validate_json('{"first_name":"John","last_name":"Doe"}')
assert person == person2
```

### Validation Examples

```python
# These will raise ValueError:
try:
    Person(first_name="John1", last_name="Doe")  # Contains number
except ValueError:
    print("Invalid first name")

try:
    Person(first_name="J", last_name="Doe")  # Too short
except ValueError:
    print("Name too short")
```

### Type Safety with Method Chaining

```python
person = Person(first_name=FirstName("James"), last_name=LastName("Bond"))
# Replace maintains type safety
person.first_name = person.first_name.replace("James", "John")
assert isinstance(person.first_name, FirstName)
```

## Advantages

**Type Safety and Correctness**
Python-newtype ensures that string operations return properly typed instances, maintaining type safety throughout your codebase. Type hints work correctly in your IDE and static type checkers, providing excellent autocompletion and early error detection. This level of type safety helps catch potential issues during development rather than at runtime.

**Robust Validation**
Validation logic is centralized in the type definition itself, ensuring that validation rules are consistently applied whenever an instance is created. The integration with Pydantic adds another layer of validation, combining both runtime checks and schema validation. This multi-layered approach ensures that your data always meets your requirements.

**Comprehensive Schema Generation**
The combination generates proper JSON schemas that accurately reflect your data model's constraints and structure. This is particularly valuable when building APIs, as it provides accurate OpenAPI specifications and clear validation rules in the schema. Your API documentation automatically includes all the validation rules and constraints defined in your types.

**Enhanced Maintainability**
By creating reusable custom types, you establish a single source of truth for your validation rules and type definitions. This separation of concerns makes your code more maintainable and reduces duplication. When you need to modify validation rules or add new functionality, you only need to update the type definition in one place.

**Powerful Flexibility**
The system allows you to add custom methods to your types, seamlessly integrate with existing Pydantic models, and works perfectly with frameworks like FastAPI. This flexibility means you can gradually adopt the system in your codebase and extend it as needed. You can create domain-specific methods and behaviors while maintaining all the benefits of both python-newtype and Pydantic.

## Schema Example

The generated JSON schema for our Person model looks like this:

```python
schema = Person.model_json_schema()
"""
{
    'title': 'Person',
    'type': 'object',
    'properties': {
        'first_name': {
            'title': 'First Name',
            'type': 'string',
            'minLength': 2,
            'maxLength': 32,
            'pattern': '^[a-zA-Z]+$',
            'description': 'The first name of the person'
        },
        'last_name': {
            'title': 'Last Name',
            'type': 'string',
            'minLength': 2,
            'maxLength': 32,
            'pattern': '^[a-zA-Z]+$',
            'description': 'The last name of the person'
        }
    },
    'required': ['first_name', 'last_name']
}
"""
```

## Best Practices

**Simple and Clear Validation Logic**
Keep your validation logic simple and focused. Complex validation rules should be broken down into separate, well-named functions that clearly express their purpose. Make validation rules explicit and easy to understand, and always provide descriptive error messages that help users quickly identify and fix issues. This approach makes your code more maintainable and helps other developers understand your validation requirements.

**Comprehensive Type Hints**
Always include proper type hints in your code when working with python-newtype and Pydantic. Use your NewType types in function signatures to take full advantage of static type checking. Let tools like mypy help you catch type-related errors early in development. Good type hints not only improve code quality but also provide better documentation and IDE support.

**Thorough Documentation**
Document your custom types thoroughly with clear docstrings that explain the validation rules and any special behavior. Include examples in your documentation showing how to use the types correctly. When adding custom methods to your types, document their purpose, parameters, and return types. Good documentation helps other developers understand how to use your types correctly and avoid common pitfalls.

**Graceful Error Handling**
Implement comprehensive error handling in your validation logic. Catch and handle validation errors appropriately, providing clear and helpful error messages that guide users toward the correct usage. Consider creating custom exception types for different categories of validation errors. This makes it easier to handle specific error cases and provide appropriate feedback to users.
