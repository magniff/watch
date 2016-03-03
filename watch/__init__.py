from collections.abc import Callable as _Callable, Mapping as _Mapping
from .attr_controllers import WatchMe, PredicateController


class Callable(PredicateController):
    def predicate(self, value):
        return isinstance(value, _Callable)


class TypeCheckerChecker(PredicateController):
    def predicate(self, value):
        return isinstance(value, PredicateController)


class Pred(WatchMe, PredicateController):

    predicate = Callable

    def __init__(self, predicate):
        self.predicate = predicate


Whatever = Pred(lambda item: True)


class ArrayOf(WatchMe, PredicateController):
    inner_type = Pred(lambda value: isinstance(value, PredicateController))

    def predicate(self, value):
        return (
            isinstance(value, (list, tuple)) and
            all(self.inner_type.predicate(item) for item in value)
        )

    def __init__(self, inner_type=None):
        self.inner_type = inner_type and inner_type() or Whatever


class Mapping(WatchMe, PredicateController):
    keys_type = Pred(lambda value: isinstance(value, PredicateController))
    values_type = Pred(lambda value: isinstance(value, PredicateController))

    def predicate(self, value_to_check):
        return (
            isinstance(value_to_check, _Mapping) and
            all(
                self.keys_type.predicate(key) and
                self.values_type.predicate(value)
                for key, value in value_to_check.items()
            )
        )

    def __init__(self, keys_type=None, values_type=None):
        self.keys_type = keys_type and keys_type() or Whatever
        self.values_type = values_type and values_type() or Whatever


class BaseCombinator(WatchMe, PredicateController):
    inner_types = ArrayOf(TypeCheckerChecker)

    def __init__(self, *inner_types):
        self.inner_types = tuple(controller() for controller in inner_types)


class SomeOf(BaseCombinator):
    def predicate(self, value):
        return any(checker.predicate(value) for checker in self.inner_types)


class CombineFrom(BaseCombinator):
    def predicate(self, value):
        return all(checker.predicate(value) for checker in self.inner_types)
