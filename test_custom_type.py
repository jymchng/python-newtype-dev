from typing import TYPE_CHECKING

import pytest

from newtype import NewType

if TYPE_CHECKING:
    from typing import List, Optional


class Super:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    # If a class method is called for a derived class, the derived class
    # object is passed as the implied first argument.
    @classmethod
    def from_dict(cls, dict_):
        # `cls` can be `Super` or `Derived`
        return cls(dict_["name"], dict_["age"])


class Derived(Super):
    def __init__(self, a, b, c, d):
        super().__init__(a, b)
        self.c = c
        self.d = d


def test_super_derived():
    with pytest.raises(TypeError):
        derived = Derived.from_dict({"name": "John", "age": 38, "c": "c", "d": "d"})
        assert derived.a == "John"
        assert derived.b == 38
        assert derived.c == "c"
        assert derived.d == "d"


class Employee:
    name: str
    age: int

    def __init__(self, name: str, age: int):
        print("Employee.__init__")
        self.name = name
        self.age = age

    def set_age(self, age: int):
        self.age = age

    def set_name(self, name: str):
        self.name = name

    def get_age(self) -> int:
        return self.age

    def get_name(self) -> str:
        return self.name

    def copy(self) -> "Employee":
        return Employee(self.name, self.age)

    def promote(self) -> "Manager":
        return Manager(self)

    def promote_with_employees(self, employees: "List[Employee]"):
        return Manager(self, employees)

    @classmethod
    # If a class method is called for a derived class, the derived class
    # object is passed as the implied first argument.
    def from_dict(cls, data: "Optional[dict]"):
        if data is None:
            return None
        employee = cls(data["name"], data["age"])
        return employee

    @classmethod
    def get_class_name(cls) -> str:
        return cls.__name__

    @classmethod
    def default(cls) -> "Employee":
        return cls("", 0)

    @property
    def uppercased_name(self):
        return self.name.upper()


BaseNewTypeEmployee = NewType(Employee)


class Manager(BaseNewTypeEmployee):
    employees: "List[Employee]"

    def __init__(
        self, employee: Employee, employees: "Optional[List[Employee]]" = None
    ):
        print("Manager.__init__")
        print("employee: ", employee)
        print("employees: ", employees)
        print(super().__init__)
        super().__init__(employee)
        self.employees = employees or []

    def add_employee(self, employee: Employee):
        self.employees.append(employee)

    def get_employees(self) -> list:
        return self.employees

    def get_name(self):
        name = super().get_name()
        assert name == self.name
        return f"Manager<{name}>"


def test_manager():
    employee_one = Employee("John", 35)
    employee_two = Employee("Jim", 33)
    employee_three = Employee("Alex", 56)

    manager = Manager(employee_one, [employee_two])  # congrats to john!
    copied_manager = manager.copy()
    assert type(copied_manager) is Manager
    assert copied_manager.get_name() == "Manager<John>"
    assert copied_manager.get_age() == 35
    assert copied_manager.get_employees() == [employee_two]
    assert copied_manager.uppercased_name == "JOHN"

    promoted_manager = manager.promote()
    assert type(promoted_manager) is Manager
    assert promoted_manager.get_name() == "Manager<John>"
    assert promoted_manager.get_age() == 35
    assert promoted_manager.get_employees() == []
    assert promoted_manager.uppercased_name == "JOHN"

    promoted_manager_with_employees = manager.promote_with_employees(
        [employee_two, employee_three]
    )
    assert type(promoted_manager_with_employees) is Manager
    assert promoted_manager_with_employees.get_name() == "Manager<John>"
    assert promoted_manager_with_employees.uppercased_name == "JOHN"
    assert promoted_manager_with_employees.get_age() == 35
    assert promoted_manager_with_employees.get_employees() == [
        employee_two,
        employee_three,
    ]

    # normal behavior, this will call Manager(employee="Peter", employees=37) through the classmethod
    manager_from_dict = promoted_manager_with_employees.from_dict(
        {"name": "Peter", "age": 37}
    )
    assert type(manager_from_dict) is Manager
    assert not hasattr(manager_from_dict, "name")
    assert not hasattr(manager_from_dict, "age")
    # assert manager_from_dict.get_name() == "Peter"
    # assert manager_from_dict.get_age() == 37
    assert manager_from_dict.get_employees() == 37


def test_manager_employees():
    employee_one = Employee("Peter", 22)
    employee_two = Employee("John", 23)
    manager_one = Manager(Employee("Steve", 33), employees=[employee_one, employee_two])

    assert (
        manager_one.from_dict.__get__(manager_one, Manager)(
            {"name": "Julia", "age": 38}
        ).get_class_name()
        == "Manager"
    )
    assert manager_one._newtype_init_kwargs_ == {
        "employees": [employee_one, employee_two]
    }

    assert (
        Employee.from_dict.__get__(manager_one, Employee)(
            {"name": "Julia", "age": 38}
        ).get_class_name()
        == "Employee"
    )
    assert manager_one.get_employees.__get__(manager_one, Manager)() == [
        employee_one,
        employee_two,
    ]
    Manager.set_name(manager_one, "Peter")
    assert manager_one.name == "Peter"
