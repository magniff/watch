import pytest
from watch.builtins import InstanceOf, SubclassOf, HasAttr, EqualsTo


def test_instanceof():
    String = InstanceOf(str)

    assert String.predicate("Hello")
    assert not String.predicate(10)

    with pytest.raises(AttributeError):
        # this doesnt make sense
        InstanceOf(10)


def test_subclassof():
    IsType = SubclassOf(object)

    assert IsType.predicate(int)

    with pytest.raises(AttributeError):
        IsType.predicate(10)

    with pytest.raises(AttributeError):
        SubclassOf(10)


def test_hasattr():
    assert HasAttr('__add__').predicate(10)
    assert not HasAttr('some').predicate(10)

    with pytest.raises(AttributeError):
        assert HasAttr(10)


def test_equals():
    assert EqualsTo(10).predicate(10)
    assert not EqualsTo(10).predicate(11)
