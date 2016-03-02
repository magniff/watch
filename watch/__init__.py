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


class Boolean(BaseTypeChecker):
    type_to_check = bool


class String(BaseTypeChecker):
    type_to_check = str


class Mapping(BaseTypeChecker):
    type_to_check = _Mapping


class Iterable(BaseTypeChecker):
    type_to_check = _Iterable


class Null(BaseTypeChecker):
    type_to_check = type(None)


class TypeCheckerChecker(BaseTypeChecker):
    type_to_check = PredicateController


class ArrayOf(BaseAutoAttributedClass, PredicateController):
    inner_type = TypeCheckerChecker

    def predicate(self, value):
        return (
            isinstance(value, (list, tuple)) and
            all(self.inner_type.predicate(item) for item in value)
        )

    def __init__(self, inner_type):
        self.inner_type = inner_type()


class SomeOf(BaseAutoAttributedClass, PredicateController):
    inner_types = ArrayOf(TypeCheckerChecker)

    def predicate(self, value):
        return any(checker.predicate(value) for checker in self.inner_types)

    def __init__(self, *inner_types):
        self.inner_types = tuple(
            controller() for controller in inner_types
        )
