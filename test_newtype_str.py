import re
from abc import (
    ABC,
    abstractmethod,
)

import pytest

from newtype import (
    NewType,
    newtype_exclude,
)


class NRIC(NewType(str)):
    country: "str" = "SG"

    def __init__(self, val: "str", hello):
        super().__init__(val)
        self.__validate__(val)  # valudation
        self._prefix = val[0]
        self._suffix = val[-1]
        self._digits = val[1:-1]
        self.hello = hello

    @newtype_exclude
    def __str__(self):
        return (
            f"NRIC(Prefix:{self._prefix}, Suffix:{self._suffix}, Digits:{self._digits})"
        )

    @staticmethod
    def __validate__(nric: "str"):
        alpha_ST = ("J", "Z", "I", "H", "G", "F", "E", "D", "C", "B", "A")
        alpha_GF = ("X", "W", "U", "T", "R", "Q", "P", "N", "M", "L", "K")
        alpha_M = ("K", "L", "J", "N", "P", "Q", "R", "T", "U", "W", "X")
        assert len(str(nric)) == 9, f"NRIC length must be 9, it is `{len(nric)}`"
        assert nric[0] in [
            "S",
            "T",
            "G",
            "F",
            "M",
        ], f"NRIC Prefix must be in ['S', 'T', 'G', 'F'], it is `{nric[0]}`"
        weights = [2, 7, 6, 5, 4, 3, 2]
        digits = nric[1:-1]
        weighted_sum = sum(int(digits[i]) * weights[i] for i in range(7))
        offset = 0
        if nric[0] in ["T", "G"]:
            offset = 4
        if nric[0] == "M":
            offset = 3
        expected_checksum = (offset + weighted_sum) % 11
        if nric[0] in ["S", "T"]:
            assert alpha_ST[expected_checksum] == nric[8], "Checksum is not right"
        elif nric[0] == "M":
            expected_checksum = 10 - expected_checksum
            assert alpha_M[expected_checksum] == nric[8]
        else:
            assert alpha_GF[expected_checksum] == nric[8]


class GoodManNRIC(NRIC):  # inherit from `NRIC` directly, NOT `NewType(NRIC)`
    def __init__(self, val: "str", hello: "int", bye: "int"):
        super().__init__(val, hello)  # calls NRIC.__init__(self, val, hello)
        self.bye = bye

    @property
    def prefix(self):
        return self._prefix


def test_nric():
    nric_minus_one = NRIC("S1234567D", 55)
    assert NRIC.__init__(nric_minus_one, "S1234567D", 1) is None
    assert type(nric_minus_one) is NRIC
    assert nric_minus_one == "S1234567D"
    assert nric_minus_one.hello == 1
    nric_one = NRIC("S1234567D", 69)
    assert str(nric_one) == "NRIC(Prefix:S, Suffix:D, Digits:1234567)"
    NRIC("M5398242L", 23)
    NRIC("F5611427X", 57)
    assert nric_one.hello == 69
    nric_one.hello = "bye"
    assert nric_one.hello == "bye"
    assert nric_one._prefix == "S"
    assert nric_one._digits == "1234567"
    assert nric_one._suffix == "D"
    assert nric_one.country == "SG"
    assert type(nric_one).__name__ == NRIC.__name__

    with pytest.raises(AssertionError):  # noqa: B017
        nric_one = nric_one.replace("S", "Q")

    with pytest.raises(AssertionError):  # noqa: B017
        nric_one = nric_one + "1234567"

    # print("str.replace('hello', 'hello', 'hi'): ", str.replace("hello", "hello", "hi"))
    # print("str.replace.__get__: ", str.replace.__get__)
    # print("str.replace.__get__(None, str): ", str.replace.__get__(None, str))
    # print("str.replace: ", str.replace)

    assert NRIC.replace == NRIC.replace
    assert NRIC.replace(nric_one, nric_one, ("M5398242L")) == "M5398242L"
    # assert type(NRIC.replace(nric_one, nric_one, ("M5398242L"))) is str
    assert type(NRIC.replace(nric_one, nric_one, ("M5398242L"))) is NRIC
    assert isinstance(NRIC.replace(nric_one, "S1234567D", ("M5398242L")), NRIC)
    assert NRIC.replace("S1234567D", nric_one, "M5398242L") == "M5398242L"
    assert type(NRIC.replace("S1234567D", nric_one, "M5398242L")) is str


def test_goodmannric():
    nric_one = GoodManNRIC("S1234567D", 69, 96)
    GoodManNRIC("M5398242L", 23, 69)
    GoodManNRIC("F5611427X", 57, 69)
    assert nric_one.hello == 69
    assert nric_one.bye == 96
    nric_one.hello = "bye"
    assert nric_one.hello == "bye"
    assert nric_one.prefix == "S"
    assert nric_one._prefix == "S"
    assert nric_one._digits == "1234567"
    assert nric_one._suffix == "D"
    assert type(nric_one).__name__ == GoodManNRIC.__name__

    with pytest.raises(Exception):  # noqa: B017
        nric_one = nric_one.replace("S", "Q")

    with pytest.raises(Exception):  # noqa: B017
        nric_one = nric_one + "1234567"


def test_hello_word():
    class GoodStr(NewType(str)):
        def __init__(self, value: "str", number):
            super().__init__(value)
            self.number = number

        # overriding is possible
        def __add__(self, other):
            # print("__add__ is called!")
            if isinstance(other, GoodStr):
                return self.number + other.number
            return self.number + other

    hello = GoodStr("hello", 3)
    world = GoodStr(" world!", 5)

    assert hello.number == 3
    assert world.number == 5
    assert type(hello + world) is int
    assert str(hello + world) == "8"
    assert (hello + world) == 8

    bye = hello.replace(
        "hello", world
    )  # replace the `str` in `hello` with the `str`-ness in `world`
    assert bye.number == 3
    assert world.number == 5
    assert type(bye + world) is int
    assert str(bye + world) == "8"
    assert (bye + world) == 8


class BlockchainAddress(NewType(str), ABC):
    is_blockchain_address = True

    @classmethod
    @abstractmethod
    def __newtype__(cls, val: "str") -> "Type[BlockchainAddress]":
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def _validate_address(val: "str") -> "bool":
        raise NotImplementedError

    @classmethod
    def __get_validators__(cls):
        yield cls.__newtype__


class EthereumAddress(BlockchainAddress):
    @classmethod
    def __newtype__(cls, val: "str"):
        assert cls._validate_address(
            val
        ), f"val = {val} does not match the regex of `Address`"

    def __init__(self, val: "str", is_checksum: "bool", a, b, c):
        super().__init__(val)
        self.__newtype__(val)
        self._is_checksum = is_checksum
        self.a = a
        self.b = b
        self.c = c

    @property
    def is_checksum(self):
        return self._is_checksum

    @staticmethod
    def _validate_address(address):
        import re

        # Ethereum addresses are 40 hexadecimal characters prefixed with '0x'
        if not re.match(r"^0x[0-9a-fA-F]{40}$", address):
            return False
        return True


def test_ethereum_address():
    expected = "0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97"
    eth_addr = EthereumAddress(
        "0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97", True, 1, 2, 3
    )
    assert eth_addr == expected
    eth_addr_capitalized = eth_addr.capitalize()
    assert eth_addr.capitalize() == expected.capitalize()
    assert eth_addr.is_checksum
    assert eth_addr.is_blockchain_address
    assert eth_addr.a == 1
    assert eth_addr.b == 2
    assert eth_addr.c == 3

    assert type(eth_addr_capitalized) is EthereumAddress
    assert eth_addr_capitalized.is_checksum
    assert eth_addr_capitalized.is_blockchain_address
    assert eth_addr_capitalized.a == 1
    assert eth_addr_capitalized.b == 2
    assert eth_addr_capitalized.c == 3


class ZipCode(NewType(str)):
    def __init__(self, val: "str"):
        super().__init__(val)
        self.__newtype__(val)

    @classmethod
    def __newtype__(cls, val: "str"):
        assert re.match(r"^\d{5}(-\d{4})?$", val), f"Invalid Zip Code: {val}"


class PhoneNumber(NewType(str)):
    def __init__(self, val: "str"):
        super().__init__(val)
        self.__newtype__(val)

    @classmethod
    def __newtype__(cls, val: "str"):
        assert re.match(r"^\+?1?\d{9,15}$", val), f"Invalid Phone Number: {val}"


class SSN(NewType(str)):
    def __init__(self, val: "str"):
        super().__init__(val)
        self.__newtype__(val)

    @classmethod
    def __newtype__(cls, val: "str"):
        assert re.match(r"^\d{3}-\d{2}-\d{4}$", val), f"Invalid SSN: {val}"


class Email(NewType(str)):
    def __init__(self, val: "str"):
        super().__init__(val)
        self.__newtype__(val)

    @classmethod
    def __newtype__(cls, val: "str"):
        assert re.match(r"^[^@]+@[^@]+\.[^@]+$", val), f"Invalid Email: {val}"


def test_zipcode_valid():
    zip_code = ZipCode("12345")
    assert zip_code == "12345"


def test_zipcode_invalid():
    with pytest.raises(AssertionError):
        ZipCode("1234")


def test_zipcode_valid_extended():
    zip_code = ZipCode("12345-6789")
    assert zip_code == "12345-6789"


def test_zipcode_invalid_extended():
    with pytest.raises(AssertionError):
        ZipCode("12345-678")


def test_phonenumber_valid():
    phone_number = PhoneNumber("+12345678901")
    assert phone_number == "+12345678901"


def test_phonenumber_invalid():
    with pytest.raises(AssertionError):
        PhoneNumber("12345")


def test_ssn_valid():
    ssn = SSN("123-45-6789")
    assert ssn == "123-45-6789"


def test_ssn_invalid():
    with pytest.raises(AssertionError):
        SSN("123-456-789")


def test_email_valid():
    email = Email("test@example.com")
    assert email == "test@example.com"


def test_email_invalid():
    with pytest.raises(AssertionError):
        Email("test@example")


def test_email_no_domain():
    with pytest.raises(AssertionError):
        Email("test@")


def test_email_no_username():
    with pytest.raises(AssertionError):
        Email("@example.com")


def test_email_special_characters():
    email = Email("test+alias@example.com")
    assert email == "test+alias@example.com"


def test_phonenumber_valid_no_country_code():
    phone_number = PhoneNumber("1234567890")
    assert phone_number == "1234567890"


def test_phonenumber_valid_with_country_code():
    phone_number = PhoneNumber("11234567890")
    assert phone_number == "11234567890"


def test_zipcode_invalid_characters():
    with pytest.raises(AssertionError):
        ZipCode("1234A")


def test_ssn_invalid_characters():
    with pytest.raises(AssertionError):
        SSN("123-AB-6789")


def test_email_subdomain():
    email = Email("user@mail.example.com")
    assert email == "user@mail.example.com"


def test_zipcode_upper():
    zip_code = ZipCode("12345")
    upper_zip_code = zip_code.upper()
    assert isinstance(upper_zip_code, ZipCode)
    assert upper_zip_code == "12345"


def test_zipcode_replace():
    zip_code = ZipCode("12345-6789")
    replaced_zip_code = zip_code.replace("9", "0")
    assert isinstance(replaced_zip_code, ZipCode)
    assert replaced_zip_code == "12345-6780"


def test_phonenumber_upper():
    phone_number = PhoneNumber("+12345678901")
    upper_phone_number = phone_number.upper()
    assert isinstance(upper_phone_number, PhoneNumber)
    assert upper_phone_number == "+12345678901"


def test_phonenumber_replace():
    phone_number = PhoneNumber("+12345678901")
    replaced_phone_number = phone_number.replace("+", "00")
    assert isinstance(replaced_phone_number, PhoneNumber)
    assert replaced_phone_number == "0012345678901"


def test_ssn_upper():
    ssn = SSN("123-45-6789")
    upper_ssn = ssn.upper()
    assert isinstance(upper_ssn, SSN)
    assert upper_ssn == "123-45-6789"


def test_ssn_replace():
    ssn = SSN("111-45-6189")
    replaced_ssn = ssn.replace("1", "2", 2)
    assert isinstance(replaced_ssn, SSN)
    assert replaced_ssn == "221-45-6189"


def test_email_upper():
    email = Email("test@example.com")
    upper_email = email.upper()
    assert isinstance(upper_email, Email)
    assert upper_email == "TEST@EXAMPLE.COM"


def test_email_replace():
    email = Email("test+alias@example.com")
    replaced_email = email.replace("+alias", "")
    assert isinstance(replaced_email, Email)
    assert replaced_email == "test@example.com"


def test_zipcode_isnumeric():
    zip_code = ZipCode("12345")
    assert zip_code.isnumeric()


def test_phonenumber_isnumeric():
    phone_number = PhoneNumber("1234567890")
    assert phone_number.isnumeric()


def test_ssn_isalnum():
    ssn = SSN("123-45-6789")
    assert not ssn.isalnum()


def test_email_isalnum():
    email = Email("test@example.com")
    assert not email.isalnum()


def test_phonenumber_strip():
    phone_number = " +12345678901 "
    with pytest.raises(AssertionError):
        phone_number = PhoneNumber(phone_number)
    stripped_phone_number = PhoneNumber(phone_number.strip())
    assert isinstance(stripped_phone_number, str)
    assert isinstance(stripped_phone_number, PhoneNumber)
    assert stripped_phone_number == "+12345678901"


def test_ssn_strip():
    ssn = " 123-45-6789 "
    with pytest.raises(AssertionError):
        ssn = SSN(ssn)
    stripped_ssn = ssn.strip()
    assert isinstance(SSN(stripped_ssn), SSN)
    assert isinstance(SSN(stripped_ssn), str)
    assert stripped_ssn == "123-45-6789"


def test_email_strip():
    email = Email(" test@example.com ")
    stripped_email = email.strip()
    assert isinstance(stripped_email, Email)
    assert stripped_email == "test@example.com"


def test_email_lower():
    email = Email("TEST@EXAMPLE.COM")
    lower_email = email.lower()
    assert isinstance(lower_email, Email)
    assert lower_email == "test@example.com"


def test_ssn_partition():
    ssn = SSN("123-45-6789")
    head, sep, tail = ssn.partition("-")
    assert isinstance(head, str)
    assert isinstance(sep, str)
    assert isinstance(tail, str)
    assert head == "123"
    assert sep == "-"
    assert tail == "45-6789"


class CustomString(NewType(str)):
    def __init__(self, val: str, *args, **kwargs):
        super().__init__(val)
        self.args = args
        self.kwargs = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def custom_method(self):
        return f"CustomString: {self}"


# Example subclasses
class SerialNumber(CustomString):
    pass


class PassportNumber(CustomString):
    pass


class LicensePlate(CustomString):
    pass


# Tests
def test_serial_number_attributes():
    serial = SerialNumber("SN12345", "arg1", "arg2", country="USA", year=2021)
    assert serial == "SN12345"
    assert serial.args == ("arg1", "arg2")
    assert serial.kwargs == {"country": "USA", "year": 2021}
    assert serial.country == "USA"
    assert serial.year == 2021

    replaced_serial = serial.replace("SN", "XX")
    assert isinstance(replaced_serial, SerialNumber)
    assert replaced_serial == "XX12345"
    assert replaced_serial.args == ("arg1", "arg2")
    assert replaced_serial.kwargs == {"country": "USA", "year": 2021}
    assert replaced_serial.country == "USA"
    assert replaced_serial.year == 2021


def test_passport_number_attributes():
    passport = PassportNumber("P12345678", "argA", country="Canada", issued_year=2020)
    assert passport == "P12345678"
    assert passport.args == ("argA",)
    assert passport.kwargs == {"country": "Canada", "issued_year": 2020}
    assert passport.country == "Canada"
    assert passport.issued_year == 2020

    upper_passport = passport.upper()
    assert isinstance(upper_passport, PassportNumber)
    assert upper_passport == "P12345678"
    assert upper_passport.args == ("argA",)
    assert upper_passport.kwargs == {"country": "Canada", "issued_year": 2020}
    assert upper_passport.country == "Canada"
    assert upper_passport.issued_year == 2020


def test_license_plate_attributes():
    license_plate = LicensePlate(
        "AB123CD", "argX", "argY", region="EU", valid_until=2025
    )
    assert license_plate == "AB123CD"
    assert license_plate.args == ("argX", "argY")
    assert license_plate.kwargs == {"region": "EU", "valid_until": 2025}
    assert license_plate.region == "EU"
    assert license_plate.valid_until == 2025

    stripped_license_plate = license_plate.strip()
    assert isinstance(stripped_license_plate, LicensePlate)
    assert stripped_license_plate == "AB123CD"
    assert stripped_license_plate.args == ("argX", "argY")
    assert stripped_license_plate.kwargs == {"region": "EU", "valid_until": 2025}
    assert stripped_license_plate.region == "EU"
    assert stripped_license_plate.valid_until == 2025


def test_serial_number_methods():
    serial = SerialNumber("SN98765", "arg1", "arg2", company="TechCorp", batch=42)
    assert serial == "SN98765"
    assert serial.args == ("arg1", "arg2")
    assert serial.kwargs == {"company": "TechCorp", "batch": 42}
    assert serial.company == "TechCorp"
    assert serial.batch == 42

    serial_upper = serial.upper()
    assert isinstance(serial_upper, SerialNumber)
    assert serial_upper == "SN98765"
    assert serial_upper.args == ("arg1", "arg2")
    assert serial_upper.kwargs == {"company": "TechCorp", "batch": 42}
    assert serial_upper.company == "TechCorp"
    assert serial_upper.batch == 42


def test_passport_number_methods():
    passport = PassportNumber(
        "P987654321", "argB", issued_country="India", expiration_year=2030
    )
    assert passport == "P987654321"
    assert passport.args == ("argB",)
    assert passport.kwargs == {"issued_country": "India", "expiration_year": 2030}
    assert passport.issued_country == "India"
    assert passport.expiration_year == 2030

    replaced_passport = passport.replace("P", "Q")
    assert isinstance(replaced_passport, PassportNumber)
    assert replaced_passport == "Q987654321"
    assert replaced_passport.args == ("argB",)
    assert replaced_passport.kwargs == {
        "issued_country": "India",
        "expiration_year": 2030,
    }
    assert replaced_passport.issued_country == "India"
    assert replaced_passport.expiration_year == 2030


def test_license_plate_methods():
    license_plate = LicensePlate("XY789ZT", "argM", region="AS", registration_year=2022)
    assert license_plate == "XY789ZT"
    assert license_plate.args == ("argM",)
    assert license_plate.kwargs == {"region": "AS", "registration_year": 2022}
    assert license_plate.region == "AS"
    assert license_plate.registration_year == 2022

    lower_license_plate = license_plate.lower()
    assert isinstance(lower_license_plate, LicensePlate)
    assert lower_license_plate == "xy789zt"
    assert lower_license_plate.args == ("argM",)
    assert lower_license_plate.kwargs == {"region": "AS", "registration_year": 2022}
    assert lower_license_plate.region == "AS"
    assert lower_license_plate.registration_year == 2022


def test_custom_method():
    custom_str = CustomString("Hello", extra="data")
    assert custom_str.custom_method() == "CustomString: Hello"
    assert custom_str.extra == "data"

    replaced_custom_str = custom_str.replace("Hello", "Hi")
    assert isinstance(replaced_custom_str, CustomString)
    assert replaced_custom_str.custom_method() == "CustomString: Hi"
    assert replaced_custom_str.extra == "data"
