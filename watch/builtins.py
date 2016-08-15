from collections import abc
from .attr_controllers import PredicateController, WatchMe


class Callable(PredicateController):

    def predicate(self, value):
        return isinstance(value, abc.Callable)


class BaseControlledValidator(WatchMe, PredicateController):

    def generate_error_message(self, field_name, value):
        return (
            "You tried to init <%s> by something other then another "
            "validator instance, didnt you?" % type(self).__qualname__
        )


class Pred(WatchMe, PredicateController):
    """Validation based on given 'predicate' function.
    """
    predicate = Callable

    def __init__(self, predicate):
        self.predicate = predicate

    def generate_error_message(self, field_name, value):
        return (
            "Init <%s> by callable, that takes one arg and returns bool." %
            type(self).__qualname__
        )


class InstanceOf(BaseControlledValidator):
    type_to_check = Pred(lambda item: isinstance(item, type))

    def predicate(self, value):
        return isinstance(value, self.type_to_check)

    def __init__(self, type_to_check):
        self.type_to_check = type_to_check


class Not(BaseControlledValidator):
    """Negates the result of nested validator.
    """
    inner_checker = InstanceOf(PredicateController)

    def predicate(self, value):
        return not self.inner_checker.predicate(value)

    def __init__(self, inner_checker):
        self.inner_checker = inner_checker


Whatever = Pred(lambda item: True)
Nothing = Not(Whatever)


class SubclassOf(BaseControlledValidator):
    type_to_check_against = InstanceOf(type)
    type_to_check = InstanceOf(type)

    def predicate(self, value):
        # validates value
        self.type_to_check = value

        return (
            isinstance(value, type) and
            issubclass(value, self.type_to_check_against)
        )

    def __init__(self, type_to_check_against):
        self.type_to_check_against = type_to_check_against


class HasAttr(BaseControlledValidator):
    """Checks that value has given attribute.
    """
    attr_name = InstanceOf(str)

    def predicate(self, value):
        return hasattr(value, self.attr_name)

    def __init__(self, attr_name):
        self.attr_name = attr_name


class EqualsTo(BaseControlledValidator):
    test_against = HasAttr('__eq__')

    def predicate(self, value):
        return self.test_against == value

    def __init__(self, test_against):
        self.test_against = test_against


class ArrayOf(BaseControlledValidator):
    """List or tuple of stuff, every item of which passed to additional
    inner_type validator, for example ArrayOf(Pred(lambda value: value == 5))
    """
    inner_type = InstanceOf(PredicateController)

    def predicate(self, value):
        return (
            isinstance(value, (list, tuple)) and
            all(self.inner_type.predicate(item) for item in value)
        )

    def __init__(self, inner_type=Whatever):
        self.inner_type = inner_type()


class MappingOf(BaseControlledValidator):
    """Pretty much what you expect - maps keys to values, which are
    controlled by keys_type and values_type validator respectively.
    """
    keys_type = InstanceOf(PredicateController)
    values_type = InstanceOf(PredicateController)

    def predicate(self, value_to_check):
        return (
            isinstance(value_to_check, abc.Mapping) and
            all(
                self.keys_type.predicate(key) and
                self.values_type.predicate(value)
                for key, value in value_to_check.items()
            )
        )

    def __init__(self, keys_type=Whatever, values_type=Whatever):
        self.keys_type = keys_type()
        self.values_type = values_type()


class BaseCombinator(BaseControlledValidator):
    """Base class for any validator that binds a bunch of other validators
    together. See SomeOf and CombineFrom code below.
    """
    inner_types = ArrayOf(InstanceOf(PredicateController))

    def __init__(self, *inner_types):
        self.inner_types = tuple(controller() for controller in inner_types)


class SomeOf(BaseCombinator):
    """This is just a fancy way to say OR speaking of validators.
    """

    def predicate(self, value):
        return any(checker.predicate(value) for checker in self.inner_types)


class CombineFrom(BaseCombinator):
    """Represents AND operator for validators.
    """

    def predicate(self, value):
        return all(checker.predicate(value) for checker in self.inner_types)

