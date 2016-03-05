from inspect import signature
from functools import wraps

from .attr_controllers import WatchMe, PredicateController
from .builtins import Pred, Callable


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
