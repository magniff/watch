import pytest


from watch import (
    WatchMe, ArrayOf, SomeOf, CombineFrom, Pred, TypeCheckerChecker
)


def test_attr_simple():
    class MyClass(WatchMe):
        foo = Pred(lambda item: isinstance(item, int))

    instance = MyClass()
    instance.foo = 10
    assert instance.foo == 10

    with pytest.raises(AttributeError):
        instance.foo = "Hello world"


def test_array_of():
    class MyClass(WatchMe):
        foo = ArrayOf(Pred(lambda item: isinstance(item, int)))

    instance = MyClass()
    instance.foo = [1, 2, 3]
    assert instance.foo == [1, 2, 3]

    with pytest.raises(AttributeError):
        instance.foo = "Hello world"

    with pytest.raises(AttributeError):
        instance.foo = [1, 2, "hello world"]


def test_type_checker_checker():
    class MyClass(WatchMe):
        foo = TypeCheckerChecker

    Integer = Pred(lambda item: isinstance(item, int))()
    instance = MyClass()
    instance.foo = Integer
    assert instance.foo == Integer

    with pytest.raises(AttributeError):
        instance.foo = 10


def test_array_of_array_of():
    class MyClass(WatchMe):
        foo = ArrayOf(ArrayOf(Pred(lambda item: isinstance(item, int))))

    instance = MyClass()
    instance.foo = [[1, 2, 3], [4, 5, 6]]
    assert instance.foo == [[1, 2, 3], [4, 5, 6]]

    with pytest.raises(AttributeError):
        instance.foo = {1: "tar"}


def test_array_of_some_of():
    class MyClass(WatchMe):
        foo = ArrayOf(
            SomeOf(
                Pred(lambda item: isinstance(item, int)),
                Pred(lambda item: isinstance(item, str)),
                ArrayOf(Pred(lambda item: isinstance(item, int)))
            )
        )

    instance = MyClass()
    instance.foo = ["Hello", 10]
    assert instance.foo == ["Hello", 10]

    instance.foo = [[1, 2, 3], "Hello", 210]
    assert instance.foo == [[1, 2, 3], "Hello", 210]

    with pytest.raises(AttributeError):
        instance.foo = {1: "tar"}


def test_someof0():
    class MyClass(WatchMe):
        foo = SomeOf(Pred(lambda item: isinstance(item, int)))

    instance = MyClass()
    instance.foo = 10
    assert instance.foo == 10

    with pytest.raises(AttributeError):
        instance.foo = "Hello world"


def test_someof1():
    class MyClass(WatchMe):
        foo = SomeOf(
            Pred(lambda item: isinstance(item, int)),
            Pred(lambda item: isinstance(item, str))
        )

    instance = MyClass()

    instance.foo = 10
    assert instance.foo == 10

    instance.foo = "this is sparta"
    assert instance.foo == "this is sparta"

    with pytest.raises(AttributeError):
        instance.foo = {1: 2}


def test_someof2():
    class MyClass(WatchMe):
        foo = SomeOf(
            SomeOf(
                SomeOf(
                    SomeOf(
                        Pred(lambda item: isinstance(item, int)),
                        Pred(lambda item: isinstance(item, str))
                    )
                )
            )
        )

    instance = MyClass()

    instance.foo = 10
    assert instance.foo == 10

    instance.foo = "this is sparta"
    assert instance.foo == "this is sparta"

    with pytest.raises(AttributeError):
        instance.foo = {1: 2}


def test_someof3():
    Integer = Pred(lambda item: isinstance(item, int))

    class MyClass(WatchMe):
        foo = SomeOf(
            ArrayOf(CombineFrom(Integer, Pred(lambda value: value < 5))),
            ArrayOf(CombineFrom(Integer, Pred(lambda value: value > 10))),
        )

    instance = MyClass()

    instance.foo = [1, 2, 3]
    assert instance.foo == [1, 2, 3]

    instance.foo = [20, 30, 40]
    assert instance.foo == [20, 30, 40]

    with pytest.raises(AttributeError):
        instance.foo = [1, 2, 100]

    with pytest.raises(AttributeError):
        instance.foo = [100, 200, -1]


def test_array_of_checkers():
    class MyClass(WatchMe):
        foo = ArrayOf(TypeCheckerChecker)

    instance = MyClass()
    pass_into = (Pred(lambda item: isinstance(item, int)),)
    instance.foo = pass_into
    assert instance.foo == pass_into

    with pytest.raises(AttributeError):
        instance.foo = 10


def test_pred():
    class MyClass(WatchMe):
        foo = Pred(lambda value: value > 10)

    instance = MyClass()
    instance.foo = 20
    assert instance.foo == 20

    with pytest.raises(AttributeError):
        instance.foo = 5


def test_combine_from0():
    class MyClass(WatchMe):
        foo = CombineFrom(
            Pred(lambda item: isinstance(item, int)),
            Pred(lambda value: value > 10),
            Pred(lambda value: value < 20)
        )

    instance = MyClass()
    instance.foo = 15
    assert instance.foo == 15

    with pytest.raises(AttributeError):
        instance.foo = 5

    with pytest.raises(AttributeError):
        instance.foo = 25


def test_combine_from1():
    class MyClass(WatchMe):
        foo = CombineFrom(
            Pred(lambda item: isinstance(item, str)),
            Pred(lambda value: len(value) > 3),
            Pred(lambda value: len(value) < 6),
            Pred(lambda value: value == value[::-1])
        )

    instance = MyClass()
    instance.foo = "abba"
    assert instance.foo == "abba"

    with pytest.raises(AttributeError):
        instance.foo = "aba"

    with pytest.raises(AttributeError):
        instance.foo = "abcddcba"
