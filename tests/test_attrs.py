import pytest


from watch import (WatchMe, Container, Any, All, Predicate, Mapping)


def test_attr_simple():
    class MyClass(WatchMe):
        foo = Predicate(lambda item: isinstance(item, int))

    instance = MyClass()
    instance.foo = 10
    assert instance.foo == 10

    with pytest.raises(AttributeError):
        instance.foo = "Hello world"


def test_array_of():
    class MyClass(WatchMe):
        foo = Container(Predicate(lambda item: isinstance(item, int)))

    instance = MyClass()
    instance.foo = [1, 2, 3]
    assert instance.foo == [1, 2, 3]

    with pytest.raises(AttributeError):
        instance.foo = "Hello world"

    with pytest.raises(AttributeError):
        instance.foo = [1, 2, "hello world"]


def test_array_of_array_of():
    class MyClass(WatchMe):
        foo = Container(Container(Predicate(lambda item: isinstance(item, int))))

    instance = MyClass()
    instance.foo = [[1, 2, 3], [4, 5, 6]]
    assert instance.foo == [[1, 2, 3], [4, 5, 6]]

    with pytest.raises(AttributeError):
        instance.foo = {1: "tar"}


def test_array_of_some_of():

    class MyClass(WatchMe):
        foo = Container(
            Any(
                Predicate(lambda item: isinstance(item, int)),
                Predicate(lambda item: isinstance(item, str)),
                Container(Predicate(lambda item: isinstance(item, int)))
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
        foo = Any(Predicate(lambda item: isinstance(item, int)))

    instance = MyClass()
    instance.foo = 10
    assert instance.foo == 10

    with pytest.raises(AttributeError):
        instance.foo = "Hello world"


def test_someof1():
    class MyClass(WatchMe):
        foo = Any(
            Predicate(lambda item: isinstance(item, int)),
            Predicate(lambda item: isinstance(item, str))
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
        foo = Any(
            Any(
                Any(
                    Any(
                        Predicate(lambda item: isinstance(item, int)),
                        Predicate(lambda item: isinstance(item, str))
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
    Integer = Predicate(lambda item: isinstance(item, int))

    class MyClass(WatchMe):
        foo = Any(
            Container(All(Integer, Predicate(lambda value: value < 5))),
            Container(All(Integer, Predicate(lambda value: value > 10))),
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


def test_Predicate():
    class MyClass(WatchMe):
        foo = Predicate(lambda value: value > 10)

    instance = MyClass()
    instance.foo = 20
    assert instance.foo == 20

    with pytest.raises(AttributeError):
        instance.foo = 5


def test_combine_from0():
    class MyClass(WatchMe):
        foo = All(
            Predicate(lambda item: isinstance(item, int)),
            Predicate(lambda value: value > 10),
            Predicate(lambda value: value < 20)
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
        foo = All(
            Predicate(lambda item: isinstance(item, str)),
            Predicate(lambda value: len(value) > 3),
            Predicate(lambda value: len(value) < 6),
            Predicate(lambda value: value == value[::-1])
        )

    instance = MyClass()
    instance.foo = "abba"
    assert instance.foo == "abba"

    with pytest.raises(AttributeError):
        instance.foo = "aba"

    with pytest.raises(AttributeError):
        instance.foo = "abcddcba"


def test_MappingOf():
    class MyClass(WatchMe):
        foo = Mapping(
            keys_type=Predicate(lambda item: isinstance(item, str)),
            values_type=Predicate(lambda item: isinstance(item, int))
        )

    instance = MyClass()
    instance.foo = {"hello": 1}
    assert instance.foo == {"hello": 1}

    with pytest.raises(AttributeError):
        instance.foo = "aba"

    with pytest.raises(AttributeError):
        instance.foo = {"hello": "world"}


def test_MappingOf_array_cant_init_with_noncontroller():

    with pytest.raises(AttributeError):
        Mapping(keys_type=int)
        Mapping(keys_type=10)
        Container(keys_type=int)


def test_bind_checkers_deffered():
    class A(WatchMe):
        pass

    A.foo = Predicate(lambda item: isinstance(item, int))
    a = A()
    a.foo = 10
    assert a.foo == 10

    with pytest.raises(AttributeError):
        a.foo = "aaaa"


def test_attr_accesibble_from_class():
    class A(WatchMe):
        foo = Predicate(lambda value: isinstance(value, int))

    assert hasattr(A, "foo")


def test_desctiptor_field_names():
    Some = Predicate(lambda value: isinstance(value, int))

    class A(WatchMe):
        foo = Some

    class B(WatchMe):
        bar = Some

    a = A()
    b = B()

    assert A.foo is not B.bar
    assert A.foo.field_name == "foo"
    assert B.bar.field_name == "bar"

