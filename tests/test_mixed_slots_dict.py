from newtype import NewType


class MixedBase:
    __slots__ = ['slot_val']

    def __init__(self, slot_val: int):
        self.slot_val = slot_val

    def copy(self):
        return MixedBase(self.slot_val)


class MixedSubType(NewType(MixedBase)):
    # No __slots__, so will use __dict__
    def __init__(self, base: MixedBase, dict_val: str):
        self.dict_val = dict_val


def test_mixed_slots_dict():
    # Create instances
    mixed_sub = MixedSubType(MixedBase(1), "test")
    assert mixed_sub.slot_val == 1
    assert mixed_sub.dict_val == "test"

    # Modify and copy
    mixed_sub.dict_val = "modified"
    mixed_copy = mixed_sub.copy()

    # Verify copy has correct values
    assert mixed_copy.slot_val == 1
    assert mixed_copy.dict_val == "modified"

    # Verify modifications don't affect original
    mixed_copy.dict_val = "new value"
    assert mixed_sub.dict_val == "modified"
    assert mixed_copy.dict_val == "new value"

    # Verify slot behavior
    try:
        mixed_sub.slot_val = 2  # Should work
        assert mixed_sub.slot_val == 2
    except AttributeError:
        assert False, "Should be able to modify slot values"

    # Verify dict behavior
    mixed_sub.new_attr = "dynamic"  # Should work
    assert mixed_sub.new_attr == "dynamic"
