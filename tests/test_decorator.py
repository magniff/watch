import pytest
from watch import (
    implements, ArrayOf, Pred, CombineFrom, ArgumentCheckError,
    ResultCheckError, WatchMe
)
from watch.function_validator import CallableWithInterface


from watch.builtins import InstanceOf


Integer = Pred(lambda item: isinstance(item, int))
Positive = Pred(lambda item: item > 0)
PositiveInteger = CombineFrom(Integer, Positive)


def test_returns():

    @implements({'return': ArrayOf(Integer)})
    def valid():
        return [1, 2, 3]

    @implements({'return': ArrayOf(Integer)})
    def invalid():
        return "hello the children!"

    assert valid()

    with pytest.raises(ResultCheckError):
        invalid()


def test_arguments():

    interface = {'value': PositiveInteger(), 'return': PositiveInteger()}

    @implements(interface)
    def factorial(value, mode=None):
        return 1 if value == 1 else value * factorial(value=value - 1)

    assert factorial(value=10) == 3628800
    assert factorial(value=10, mode=1) == 3628800

    with pytest.raises(ArgumentCheckError):
        factorial(value="hello")

    with pytest.raises(ArgumentCheckError):
        factorial(value=0)

    with pytest.raises(ArgumentCheckError):
        factorial(value=-10)


def test_callable_with_interface():
    interface = {
        'a': InstanceOf(int), 'b': InstanceOf(int), 'return': InstanceOf(int)
    }

    another_interface = {
        'a': InstanceOf(int), 'b': InstanceOf(int), 'return': InstanceOf(str)
    }

    @implements(interface)
    def function_that_fits(a, b):
        return a + b

    @implements(another_interface)
    def function_that_doesnt_fit(a, b):
        return a + b

    class A(WatchMe):
        foo = CallableWithInterface(interface)

    a = A()
    a.foo = function_that_fits

    with pytest.raises(AttributeError):
        a.foo = function_that_doesnt_fit


def test_function_does_not_implement_interface():
    interface = {
        'a': InstanceOf(int), 'b': InstanceOf(int), 'return': InstanceOf(int)
    }

    @implements(interface)
    def function(a, b, c):
        return a + c

    with pytest.raises(ValueError):
        @implements(interface)
        def function1(a, c):
            return a + c
