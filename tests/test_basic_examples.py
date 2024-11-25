import pytest
from newtype import NewType


def test_enhanced_str():
    class EnhancedStr(NewType(str)):
        def reverse(self):
            return self[::-1]
        
        def duplicate(self):
            return self + self
    
    text = EnhancedStr("Hello")
    assert text.reverse() == "olleH"
    assert text.duplicate() == "HelloHello"
    assert text.upper() == "HELLO"
    
    # Test that it still behaves like a string
    assert isinstance(text, str)
    assert len(text) == 5
    assert text[0] == "H"


def test_typed_list():
    class TypedList(NewType(list)):
        def __init__(self, type_check=None):
            super().__init__()
            self.type_check = type_check
        
        def append(self, item):
            if self.type_check and not isinstance(item, self.type_check):
                raise TypeError(f"Item must be of type {self.type_check}")
            super().append(item)
    
    numbers = TypedList(type_check=int)
    numbers.append(42)
    assert len(numbers) == 1
    assert numbers[0] == 42
    
    with pytest.raises(TypeError):
        numbers.append("string")
    
    # Test that it works without type checking
    flexible_list = TypedList()
    flexible_list.append(42)
    flexible_list.append("string")
    assert len(flexible_list) == 2


def test_default_dict():
    class DefaultDict(NewType(dict)):
        def __init__(self, default_value=None):
            super().__init__()
            self.default_value = default_value
        
        def __getitem__(self, key):
            if key not in self:
                return self.default_value
            return super().__getitem__(key)
    
    d = DefaultDict(default_value=0)
    assert d["non_existent"] == 0
    
    d["exists"] = 42
    assert d["exists"] == 42
    
    # Test with different default values
    d_none = DefaultDict()
    assert d_none["any_key"] is None
    
    d_list = DefaultDict(default_value=[])
    assert d_list["any_key"] == []
    
    # Test that it still behaves like a dict
    assert len(d) == 1
    assert "exists" in d
    assert "non_existent" not in d


def test_inheritance_chain():
    class BaseDict(NewType(dict)):
        def get_keys_sorted(self):
            return sorted(self.keys())
    
    class ExtendedDict(BaseDict):
        def get_values_sorted(self):
            return sorted(self.values())
    
    d = ExtendedDict()
    d.update({"c": 3, "a": 1, "b": 2})
    
    assert d.get_keys_sorted() == ["a", "b", "c"]
    assert d.get_values_sorted() == [1, 2, 3]
    assert isinstance(d, dict)
    assert isinstance(d, BaseDict)
    assert isinstance(d, ExtendedDict)
