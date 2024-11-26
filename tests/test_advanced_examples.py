import logging
import time
from typing import Optional
from abc import ABC, abstractmethod
from functools import cached_property

import pytest

from newtype import NewType


def test_timed_dict():
    class TimedDict(NewType(dict)):
        def __init__(self):
            super().__init__()
            self.operation_times = {}

        def __getitem__(self, key):
            start = time.time()
            result = super().__getitem__(key)
            elapsed = time.time() - start
            self.operation_times[key] = elapsed
            return result

    d = TimedDict()
    d["key"] = "value"
    _ = d["key"]

    assert "key" in d.operation_times
    assert isinstance(d.operation_times["key"], float)
    assert d.operation_times["key"] >= 0

    # Test that it still behaves like a dict
    assert d["key"] == "value"
    assert len(d) == 1
    assert list(d.keys()) == ["key"]


class IEmail(ABC):

    @property
    @abstractmethod
    def domain(self) -> Optional[str]:
        ...

    @abstractmethod
    @cached_property
    def name(self) -> Optional[str]:
        ...

    @staticmethod
    @abstractmethod
    def from_str(s: str) -> "EmailStr":
        ...


class EmailStr(IEmail, NewType(str)):
    def __init__(self, value: str, strict: bool = True):
        if strict and "@" not in value:
            raise ValueError("Invalid email format")
        super().__init__(value)

    @property
    def domain(self) -> Optional[str]:
        if "@" in self:
            return self.split("@")[1]
        return None

    @cached_property
    def name(self) -> Optional[str]:
        if "@" in self:
            return self.split("@")[0]
        return None

    @staticmethod
    def from_str(s: str) -> "EmailStr":
        return EmailStr(s)

    def get_name(self) -> Optional[str]:
        return self.name


class Gmail(EmailStr):
    def __init__(self, value: str, strict: bool = True):
        if strict and "@gmail.com" not in value:
            raise ValueError("Invalid email format")
        super().__init__(value, strict)


def test_email_str():
    gmail = Gmail("hello@gmail.com")
    assert gmail.domain == "gmail.com"
    assert gmail.get_name.__name__ == "get_name"
    assert gmail.name == "hello"
    assert isinstance(gmail.domain, str)
    with pytest.raises(AssertionError):
        assert isinstance(gmail.domain, Gmail)

    gmail = Gmail.from_str("hello@gmail.com")
    assert gmail.domain == "gmail.com"
    assert gmail.name == "hello"
    assert isinstance(gmail, str)
    assert isinstance(gmail, EmailStr)
    with pytest.raises(AssertionError):
        # `@staticmethod` is not wrapped
        assert isinstance(gmail, Gmail)

    assert isinstance(gmail, str)
    with pytest.raises(AssertionError):
        assert isinstance(gmail, Gmail)

    # Test valid email
    email = EmailStr("user@example.com")
    assert email.domain == "example.com"
    assert email.name == "user"
    assert isinstance(email, str)
    assert isinstance(email, EmailStr)
    assert len(email) == len("user@example.com")

    with pytest.raises(ValueError):
        email.replace("@", "")

    # Test invalid email with strict mode
    with pytest.raises(ValueError):
        EmailStr("invalid")

    new_email = email.replace("user@example.com", "user1@example.com")
    assert isinstance(new_email, EmailStr)
    assert new_email.name == "user1"
    assert new_email.domain == "example.com"

    # Test invalid email with non-strict mode
    non_strict = EmailStr("invalid", strict=False)
    assert non_strict.domain is None


def test_logged_list(caplog):
    class LoggedList(NewType(list)):
        def __init__(self, logger=None):
            super().__init__()
            self.logger = logger or logging.getLogger(__name__)

        def __enter__(self):
            self.logger.info("Starting list operations")
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.logger.info("Finished list operations")
            if exc_type:
                self.logger.error(f"Error occurred: {exc_val}")
            return False

    # Test normal operation
    with caplog.at_level(logging.INFO):
        with LoggedList() as lst:
            lst.append(1)
            lst.extend([2, 3, 4])

    assert "Starting list operations" in caplog.text
    assert "Finished list operations" in caplog.text

    # Test error handling
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError):
            with LoggedList() as lst:
                raise ValueError("Test error")

    assert "Error occurred: Test error" in caplog.text


def test_method_interception():
    class InterceptedList(NewType(list)):
        def __init__(self):
            super().__init__()
            self.operation_count = 0

        def append(self, item):
            self.operation_count += 1
            super().append(item)

        def extend(self, items):
            self.operation_count += 1
            super().extend(items)

        def get_operation_count(self):
            return self.operation_count

    lst = InterceptedList()

    # Test append
    lst.append(1)
    assert lst[0] == 1
    assert lst.get_operation_count() == 1

    # Test extend
    lst.extend([2, 3])
    assert list(lst) == [1, 2, 3]
    assert lst.get_operation_count() == 2

    # Test that it still behaves like a list
    assert len(lst) == 3
    assert isinstance(lst, list)
    assert isinstance(lst, InterceptedList)
    assert lst.index(2) == 1
