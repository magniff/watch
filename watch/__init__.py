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


class ArgumentCheckError(TypeError):
    pass


class ResultCheckError(TypeError):
    pass


class EyeOn(WatchMe, PredicateController):
    attr_failed = Callable
    result_failed = Callable
    function = Callable

    def __call__(self, function):
        # this set triggers function validation agains Callable validator
        self.function = function

        func_signature = signature(self.function)
        annotations = function.__annotations__

        @wraps(self.function)
        def decorator(*args, **kwargs):
            arguments = func_signature.bind(*args, **kwargs).arguments

            # following code validates arguments passed to the function
            for name, value in arguments.items():
                checker = annotations.get(name)

                if not checker:
                    continue

                if not checker.predicate(value):
                    self.attr_failed(function, name, value)

            # ok, lets evaluate function and validate the result
            return_checker = annotations.get('return', Pred(lambda item: True))
            result = function(*args, **kwargs)
            if not return_checker.predicate(result):
                self.result_failed(function, args, kwargs, result)

            return result

        return decorator

    def __init__(self, attr_failed=None, result_failed=None):
        self.attr_failed = attr_failed or default_attr_failed_handler
        self.result_failed = result_failed or default_result_failed_handler


# little ailas to make function like name
watch_this = EyeOn


def default_result_failed_handler(func, args, kwargs, result):
    raise ResultCheckError(
        "Result %s of function %s failed validation." %
        (result, func.__name__)
    )


def default_attr_failed_handler(func, attr_name, attr_value):
    raise ArgumentCheckError(
        "Argument %s == %s of function %s failed validation." %
        (attr_name, attr_value, func.__name__)
    )
