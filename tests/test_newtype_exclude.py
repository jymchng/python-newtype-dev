import pytest
from newtype import newtype_exclude, func_is_excluded

def test_newtype_exclude():
    def test_func():
        pass
    
    newtype_exclude(test_func)
    assert func_is_excluded(test_func)

def test_func_is_excluded_false():
    def another_func():
        pass
    
    assert not func_is_excluded(another_func)

def test_multiple_exclusions():
    def func_one():
        pass
    
    def func_two():
        pass
    
    newtype_exclude(func_one)
    newtype_exclude(func_two)

    assert func_is_excluded(func_one)
    assert func_is_excluded(func_two)

def test_not_excluded_function():
    def normal_func():
        pass
    
    assert not func_is_excluded(normal_func)

def test_exclude_same_func_twice():
    def repeat_func():
        pass
    
    newtype_exclude(repeat_func)
    newtype_exclude(repeat_func)

    assert func_is_excluded(repeat_func)

def test_exclusion_on_lambda():
    test_lambda = lambda x: x
    newtype_exclude(test_lambda)
    assert func_is_excluded(test_lambda)

def test_exclusion_on_method():
    class MyClass:
        @newtype_exclude
        def method(self):
            pass
        
    obj = MyClass()
    assert func_is_excluded(obj.method)

def test_exclusion_on_bound_method():
    class MyClass:
        def method(self):
            pass
        
    obj = MyClass()
    newtype_exclude(MyClass.method)
    assert func_is_excluded(MyClass.method)

def test_exclusion_on_static_method():
    class MyClass:
        @staticmethod
        def static_method():
            pass
        
    newtype_exclude(MyClass.static_method)
    assert func_is_excluded(MyClass.static_method)

def test_none_excluded():
    assert not func_is_excluded(None)