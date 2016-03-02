import pytest


from watch import (
    BaseAutoAttributedClass, Integer, String, ArrayOf, SomeOf,
    TypeCheckerChecker
)


def test_attr_simple():
    class MyClass(BaseAutoAttributedClass):
        foo = Integer

    instance = MyClass()
    instance.foo = 10
    assert instance.foo == 10

    with pytest.raises(AttributeError):
        instance.foo = "Hello world"


def test_array_of():
    class MyClass(BaseAutoAttributedClass):
        foo = ArrayOf(Integer)

    instance = MyClass()
    instance.foo = [1, 2, 3]
    assert instance.foo == [1, 2, 3]

    with pytest.raises(AttributeError):
        instance.foo = "Hello world"

    with pytest.raises(AttributeError):
        instance.foo = [1, 2, "hello world"]


def test_type_checker_checker():
    class MyClass(BaseAutoAttributedClass):
        foo = TypeCheckerChecker

    integer = Integer()
    instance = MyClass()
    instance.foo = integer
    assert instance.foo == integer

    with pytest.raises(AttributeError):
        instance.foo = 10


def test_array_of_array_of():
    class MyClass(BaseAutoAttributedClass):
        foo = ArrayOf(ArrayOf(Integer))

    instance = MyClass()
    instance.foo = [[1, 2, 3], [4, 5, 6]]
    assert instance.foo == [[1, 2, 3], [4, 5, 6]]

    with pytest.raises(AttributeError):
        instance.foo = {1: "tar"}


def test_array_of_some_of():
    class MyClass(BaseAutoAttributedClass):
        foo = ArrayOf(SomeOf(Integer, String, ArrayOf(Integer)))

    instance = MyClass()
    instance.foo = ["Hello", 10]
    assert instance.foo == ["Hello", 10]

    instance.foo = [[1, 2, 3], "Hello", 210]
    assert instance.foo == [[1, 2, 3], "Hello", 210]

    with pytest.raises(AttributeError):
        instance.foo = {1: "tar"}


def test_someof0():
    class MyClass(BaseAutoAttributedClass):
        foo = SomeOf(Integer)

    instance = MyClass()
    instance.foo = 10
    assert instance.foo == 10

    with pytest.raises(AttributeError):
        instance.foo = "Hello world"


def test_someof0():
    class MyClass(BaseAutoAttributedClass):
        foo = SomeOf(Integer, String)

    instance = MyClass()

    instance.foo = 10
    assert instance.foo == 10

    instance.foo = "this is sparta"
    assert instance.foo == "this is sparta"

    with pytest.raises(AttributeError):
        instance.foo = {1: 2}


def test_someof1():
    class MyClass(BaseAutoAttributedClass):
        foo = SomeOf(SomeOf(SomeOf(SomeOf(Integer, String))))

    instance = MyClass()

    instance.foo = 10
    assert instance.foo == 10

    instance.foo = "this is sparta"
    assert instance.foo == "this is sparta"

    with pytest.raises(AttributeError):
        instance.foo = {1: 2}


def test_array_of_checkers():
    class MyClass(BaseAutoAttributedClass):
        foo = ArrayOf(TypeCheckerChecker)

    instance = MyClass()
    pass_into = (Integer(),)
    instance.foo = pass_into
    assert instance.foo == pass_into

    with pytest.raises(AttributeError):
        instance.foo = 10
