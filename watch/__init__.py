from collections.abc import (
    Callable as _Callable, Iterable as _Iterable, Mapping as _Mapping
)
from .attr_controllers import (
    BaseAutoAttributedClass, BaseTypeChecker, PredicateController
)


class Callable(BaseTypeChecker):
    type_to_check = _Callable


class Integer(BaseTypeChecker):
    type_to_check = int


class Float(BaseTypeChecker):
    type_to_check = float


class Complex(BaseTypeChecker):
    type_to_check = complex


class Boolean(BaseTypeChecker):
    type_to_check = bool


class String(BaseTypeChecker):
    type_to_check = str


class Bytes(BaseTypeChecker):
    type_to_check = bytes


class Mapping(BaseTypeChecker):
    type_to_check = _Mapping


class Iterable(BaseTypeChecker):
    type_to_check = _Iterable


class Null(BaseTypeChecker):
    type_to_check = type(None)


class TypeCheckerChecker(BaseTypeChecker):
    type_to_check = PredicateController


class Pred(BaseAutoAttributedClass, PredicateController):
    predicate = Callable

    def __init__(self, predicate):
        self.predicate = predicate


class ArrayOf(BaseAutoAttributedClass, PredicateController):
    inner_type = Pred(lambda value: isinstance(value, PredicateController))

    def predicate(self, value):
        return (
            isinstance(value, (list, tuple)) and
            all(self.inner_type.predicate(item) for item in value)
        )

    def __init__(self, inner_type):
        self.inner_type = inner_type()


class BaseCombinator(BaseAutoAttributedClass, PredicateController):
    inner_types = ArrayOf(TypeCheckerChecker)

    def __init__(self, *inner_types):
        self.inner_types = tuple(controller() for controller in inner_types)


class SomeOf(BaseCombinator):
    def predicate(self, value):
        return any(checker.predicate(value) for checker in self.inner_types)


class CombineFrom(BaseCombinator):
    def predicate(self, value):
        return all(checker.predicate(value) for checker in self.inner_types)
