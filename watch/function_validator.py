from inspect import signature

from .attr_controllers import WatchMe, PredicateController
from .builtins import Callable, Whatever, MappingOf, InstanceOf, HasAttr


class ArgumentCheckError(TypeError):
    pass


class ResultCheckError(TypeError):
    pass


MapOfPredicates = MappingOf(
    keys_type=InstanceOf(str), values_type=InstanceOf(PredicateController)
)


class InterfacedFunction(WatchMe):
    function = Callable
    interface = MapOfPredicates

    # customization related stuff
    result_failed_handler = Callable
    argument_failed_handler = Callable

    def compare_params(self):
        return all(
            name in signature(self.function).parameters for name in
            (item for item in self.interface if item != 'return')
        )

    def __init__(self, function, interface):
        self.interface = interface
        self.function = function

        if not self.compare_params():
            raise ValueError(
                "Function %s doesn`t implement interface %s." %
                (self.function.__name__, dict(self.interface))
            )
        # you may wanna override following fail handlers
        self.result_failed_handler = default_result_failed_handler
        self.argument_failed_handler = default_argument_failed_handler

    def __call__(self, **kwargs):
        func_signature = signature(self.function)
        arguments = func_signature.bind(**kwargs).arguments

        # following code validates arguments passed to the function
        for name, value in arguments.items():
            if not self.interface.get(name, Whatever).predicate(value):
                self.argument_failed_handler(self.function, name, value)

        # ok, lets evaluate function and validate the result
        return_checker = self.interface.get('return', Whatever)
        result = self.function(**kwargs)
        if not return_checker.predicate(result):
            self.result_failed_handler(self.function, kwargs, result)

        return result


class CallableWithInterface(WatchMe, PredicateController):
    interface = MapOfPredicates

    def predicate(self, value):
        precondition = (
            InstanceOf(InterfacedFunction).predicate(value) and
            HasAttr('interface').predicate(value) and
            MapOfPredicates.predicate(value.interface)
        )

        return precondition and value.interface == self.interface

    def __init__(self, inteface):
        self.interface = inteface


def default_result_failed_handler(func, kwargs, result):
    raise ResultCheckError(
        "Result %s of function %s failed validation." %
        (result, func.__name__)
    )


def default_argument_failed_handler(func, attr_name, attr_value):
    raise ArgumentCheckError(
        "Argument %s == %s of function %s failed validation." %
        (attr_name, attr_value, func.__name__)
    )


def implements(interface):
    def builder(function):
        interfaced_function = InterfacedFunction(function, interface)
        return interfaced_function

    return builder
