from newtype import NewType


class Mutable:
    def __init__(self, inner: int):
        self.inner = inner

    def copy(self):
        return Mutable(self.inner)


class MutableSubType(NewType(Mutable)):
    def __init__(self, mutable: Mutable, inner2: int):
        self.inner2 = inner2


def test_mutable_and_subtype():
    mutable_sub_type = MutableSubType(Mutable(1), 2)
    assert mutable_sub_type.inner == 1
    assert mutable_sub_type.inner2 == 2

    mutable_sub_type.inner2 = 3
    mutable_sub_type_copy = mutable_sub_type.copy()
    assert mutable_sub_type.inner == 1
    assert mutable_sub_type.inner2 == 3

    assert mutable_sub_type_copy.inner == 1
    assert mutable_sub_type_copy.inner2 == 3

    mutable_sub_type_copy.inner2 = 4
    assert mutable_sub_type.inner2 == 3
    assert mutable_sub_type_copy.inner2 == 4
