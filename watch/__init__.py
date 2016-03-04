from inspect import signature
from functools import wraps
from collections.abc import Callable as _Callable, Mapping as _Mapping

from .attr_controllers import WatchMe, PredicateController


class Callable(PredicateController):

    def predicate(self, value):
        return isinstance(value, _Callable)


class Pred(WatchMe, PredicateController):

    predicate = Callable

    def __init__(self, predicate):
        self.predicate = predicate


class ArrayOf(WatchMe, PredicateController):
    inner_type = Pred(lambda item: isinstance(item, PredicateController))

    def predicate(self, value):
        return (
            isinstance(value, (list, tuple)) and
            all(self.inner_type.predicate(item) for item in value)
        )

    def __init__(self, inner_type=Pred(lambda item: True)):
        self.inner_type = inner_type()


class MappingOf(WatchMe, PredicateController):
    keys_type = Pred(lambda item: isinstance(item, PredicateController))
    values_type = Pred(lambda item: isinstance(item, PredicateController))

    def predicate(self, value_to_check):
        return (
            isinstance(value_to_check, _Mapping) and
            all(
                self.keys_type.predicate(key) and
                self.values_type.predicate(value)
                for key, value in value_to_check.items()
            )
        )

    def __init__(
            self, keys_type=Pred(lambda item: True),
            values_type=Pred(lambda item: True)
        ):
        self.keys_type = keys_type()
        self.values_type = values_type()


class BaseCombinator(WatchMe, PredicateController):
    inner_types = ArrayOf(
        Pred(lambda item: isinstance(item, PredicateController))
    )

    def __init__(self, *inner_types):
        self.inner_types = tuple(controller() for controller in inner_types)


class SomeOf(BaseCombinator):

    def predicate(self, value):
        return any(checker.predicate(value) for checker in self.inner_types)


class CombineFrom(BaseCombinator):

    def predicate(self, value):
        return all(checker.predicate(value) for checker in self.inner_types)


class ArgumentsBindError(TypeError):
    pass


class ArgumentCheckError(TypeError):
    pass


class ResultCheckError(TypeError):
    pass


def watch_this(function):

    func_signature = signature(function)
    annotations = function.__annotations__
    return_checker = annotations.get('return', Pred(lambda item: True))

    @wraps(function)
    def decorator(*args, **kwargs):
        try:
            arguments = func_signature.bind(*args, **kwargs).arguments
        except TypeError as error:
            raise ArgumentsBindError(
                "Failed to bind arguments args=%s, kwargs=%s passed "
                "into function %s" % (args, kwargs, function.__name__)
            ) from error

        for name, value in arguments.items():
            # at this point "name in annotations" is guarantied
            checker = annotations.get(name)
            if not checker:
                continue

            if not checker.predicate(value):
                raise ArgumentCheckError(
                    "Argument %s == %s of function %s failed validation." %
                    (name, value, function.__name__)
                )

        result = function(*args, **kwargs)
        if not return_checker.predicate(result):
            raise ResultCheckError(
                "Result %s of function %s failed validation." %
                (result, function.__name__)
            )

        return result

    return decorator
