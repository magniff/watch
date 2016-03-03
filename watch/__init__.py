from collections.abc import Callable as _Callable
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


class ArrayOf(WatchMe, PredicateController):
    inner_type = Pred(lambda value: isinstance(value, PredicateController))

    def predicate(self, value):
        return (
            isinstance(value, (list, tuple)) and
            all(self.inner_type.predicate(item) for item in value)
        )

    def __init__(self, inner_type):
        self.inner_type = inner_type()


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
