#!/usr/bin/env python3
"""
Demo script showing key features of python-newtype library.
"""

from newtype import NewType


# Example 1: Type-preserving string operations
class SafeStr(NewType(str)):
    def __init__(self, val):
        super().__init__()
        if "<script>" in val.lower():
            raise ValueError("XSS attempt detected")


# Example 2: Enhanced integers with validation
class PositiveInt(NewType(int)):
    def __init__(self, val):
        super().__init__()
        if val <= 0:
            raise ValueError("Value must be positive")


# Example 3: Dictionary with logging
class LoggedDict(NewType(dict)):
    def __setitem__(self, key, value):
        print(f"Setting {key} = {value}")
        result = super().__setitem__(key, value)
        return result


def main():
    # Demonstrate SafeStr
    print("\n=== SafeStr Demo ===")
    text = SafeStr("Hello, World!")
    print(f"Original: {text}")
    print(f"Upper: {text.upper()}")  # Still returns SafeStr
    print(f"Sliced: {text[:5]}")  # Still returns SafeStr

    try:
        SafeStr("Bad <script>alert('xss')</script>")
        print("Should not reach here!")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Demonstrate PositiveInt
    print("\n=== PositiveInt Demo ===")
    num = PositiveInt(42)
    print(f"Original: {num}")
    result = num + 10  # Still returns PositiveInt
    print(f"Added 10: {result}")
    print(f"Type of result: {type(result)}")

    try:
        PositiveInt(-5)
        print("Should not reach here!")
    except ValueError as e:
        print(f"Caught expected error: {e}")

    # Demonstrate LoggedDict
    print("\n=== LoggedDict Demo ===")
    d = LoggedDict({"initial": "value"})
    d["key1"] = "value1"
    d["key2"] = "value2"

    # Show that copied dict maintains type
    d2 = d.copy()
    print(f"\nCopied dict type: {type(d2)}")
    d2["key3"] = "value3"


if __name__ == "__main__":
    main()
