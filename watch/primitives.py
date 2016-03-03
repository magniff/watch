from collections.abc import (
    Callable as _Callable, Iterable as _Iterable, Mapping as _Mapping
)
from .attr_controllers import BaseTypeChecker, PredicateController


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
