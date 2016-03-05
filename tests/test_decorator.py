import pytest
from watch import (
    watch_this, ArrayOf, Pred, CombineFrom, ArgumentCheckError, ResultCheckError
)


Integer = Pred(lambda item: isinstance(item, int))
Positive = Pred(lambda item: item > 0)
PositiveInteger = CombineFrom(Integer, Positive)


def test_returns():

    @watch_this()
    def valid() -> ArrayOf(Integer):
        return [1, 2, 3]

    @watch_this()
    def invalid() -> ArrayOf(Integer):
        return "hello the children!"

    assert valid()

    with pytest.raises(ResultCheckError):
        invalid()


def test_arguments():

    @watch_this()
    def factorial(value: PositiveInteger, mode=None) -> PositiveInteger:
        return 1 if value == 1 else value * factorial(value - 1)

    assert factorial(10) == 3628800
    assert factorial(value=10, mode=1) == 3628800

    with pytest.raises(ArgumentCheckError):
        factorial("hello")

    with pytest.raises(ArgumentCheckError):
        factorial(0)

    with pytest.raises(ArgumentCheckError):
        factorial(-10)
