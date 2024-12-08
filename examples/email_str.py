import pytest


import re


from newtype import NewType, newtype_exclude


class EmailStr(NewType(str)):
    # you can define `__slots__` to save space
    __slots__ = (
        '_local_part',
        '_domain_part',
    )

    def __init__(self, value: str):
        super().__init__()
        if "@" not in value:
            raise TypeError("`EmailStr` requires a '@' symbol within")
        self._local_part, self._domain_part = value.split("@")

    @newtype_exclude
    def __str__(self):
        return f"<Email - Local Part: {self.local_part}; Domain Part: {self.domain_part}>"

    @property
    def local_part(self):
        """Return the local part of the email address."""
        return self._local_part

    @property
    def domain_part(self):
        """Return the domain part of the email address."""
        return self._domain_part

    @property
    def full_email(self):
        """Return the full email address."""
        return str(self)

    @classmethod
    def from_string(cls, email: str):
        """Create an EmailStr instance from a string."""
        return cls(email)

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Check if the provided string is a valid email format."""
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(email_regex, email) is not None


def test_emailstr_replace():
    """`EmailStr` uses `str.replace(..)` as its own method, returning an instance of `EmailStr`
    if the resultant `str` instance is a value `EmailStr`.
    """
    peter_email = EmailStr("peter@gmail.com")
    smith_email = EmailStr("smith@gmail.com")

    with pytest.raises(Exception):
        # this raises because `peter_email` is no longer an instance of `EmailStr`
        peter_email = peter_email.replace("peter@gmail.com", "petergmail.com")

    # this works because the entire email can be 'replaced'
    james_email = smith_email.replace("smith@gmail.com", "james@gmail.com")

    # comparison with `str` is built-in
    assert james_email == "james@gmail.com"

    # `james_email` is still an `EmailStr`
    assert isinstance(james_email, EmailStr)

    # this works because the local part can be 'replaced'
    jane_email = james_email.replace("james", "jane")

    # `jane_email` is still an `EmailStr`
    assert isinstance(jane_email, EmailStr)
    assert jane_email == "jane@gmail.com"


def test_emailstr_properties_methods():
    """Test the property, class method, and static method of EmailStr."""
    # Test property
    email = EmailStr("test@example.com")
    # `property` is not coerced to `EmailStr`
    assert email.full_email == "<Email - Local Part: test; Domain Part: example.com>"
    assert isinstance(email.full_email, str)
    # `property` is not coerced to `EmailStr`
    assert not isinstance(email.full_email, EmailStr)
    assert email.local_part == "test"
    assert email.domain_part == "example.com"

    # Test class method
    email_from_string = EmailStr.from_string("classmethod@example.com")
    # `property` is not coerced to `EmailStr`
    assert (
        email_from_string.full_email
        == "<Email - Local Part: classmethod; Domain Part: example.com>"
    )
    assert email_from_string.local_part == "classmethod"
    assert email_from_string.domain_part == "example.com"

    # Test static method
    assert EmailStr.is_valid_email("valid.email@example.com") is True
    assert EmailStr.is_valid_email("invalid-email.com") is False


def test_email_str__slots__():
    email = EmailStr("test@example.com")

    with pytest.raises(AttributeError):
        email.hi = "bye"
        assert email.hi == "bye"


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])
