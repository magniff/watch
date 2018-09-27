from collections import abc
from operator import xor
from functools import reduce


from .attr_controllers import PredicateController, WatchMe


class BaseControlledValidator(WatchMe, PredicateController):

    def generate_error_message(self, field_name, value):
        return (
            "You tried to init <%s> by something other then another "
            "validator instance, didnt you?" % type(self).__qualname__
        )


class Predicate(WatchMe, PredicateController):
    """Validation based on given 'predicate' function.
    """

    # this wont let Pred object be inited with non callable checker
    predicate = type(
        "AnonymousCallableChecker",
        (PredicateController,),
        {
            "predicate": lambda self, value: isinstance(value, abc.Callable)
        }
    )

    def __init__(self, predicate):
        self.predicate = predicate

    def generate_error_message(self, field_name, value):
        return (
            "Init <%s> by callable, that takes one arg and returns bool." %
            type(self).__qualname__
        )


Whatever = Predicate(lambda item: True)
Nothing = Predicate(lambda item: False)


class InstanceOf(BaseControlledValidator):
    type_to_check = Predicate(lambda item: isinstance(item, type))

    def predicate(self, value):
        return isinstance(value, self.type_to_check)

    def __init__(self, type_to_check):
        self.type_to_check = type_to_check


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


class Not(BaseControlledValidator):
    """
    Negates the result of nested validator.
    """
    inner_checker = InstanceOf(PredicateController)

    def predicate(self, value):
        return not self.inner_checker.predicate(value)

    def __init__(self, inner_checker):
        self.inner_checker = inner_checker


class AgnosticComparator(BaseControlledValidator):
    value_to_check_agains = Not(InstanceOf(PredicateController))

    def __init__(self, value_to_check_against):
        self.value_to_check_against = value_to_check_against


class GtThen(AgnosticComparator):

    def predicate(self, value):
        return value > self.value_to_check_against


class GtEqThen(AgnosticComparator):

    def predicate(self, value):
        return value >= self.value_to_check_against


class LtThen(AgnosticComparator):

    def predicate(self, value):
        return value < self.value_to_check_against


class LtEqThen(AgnosticComparator):

    def predicate(self, value):
        return value <= self.value_to_check_against



class Nullable(BaseControlledValidator):
    inner_checker = InstanceOf(PredicateController)

    def predicate(self, value):
        return value is None or self.inner_checker.predicate(value)

    def __init__(self, inner_checker):
        self.inner_checker = inner_checker


class HasAttr(BaseControlledValidator):
    """
    Checks that value has given attribute.
    """

    attribute_name = InstanceOf(str)

    def predicate(self, value):
        return hasattr(value, self.attribute_name)

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name


class Just(BaseControlledValidator):
    test_against = HasAttr("__eq__")

    def predicate(self, value):
        return self.test_against == value

    def __init__(self, value):
        self.test_against = value


class Container(BaseControlledValidator):
    """
    Container of stuff, every item of which is passed to additional
    inner_type validator.
    Example: Container(Gt(5) & Lt(10))

    Warning: validation actually iterates over the container, thus in some
    cases (e.g. generators) validation may screw up your container.
    """

    inner_validator = InstanceOf(PredicateController)
    container_type = SubclassOf(abc.Iterable)

    def predicate(self, value):
        return (
            isinstance(value, self.container_type) and
            all(self.inner_validator.predicate(item) for item in value)
        )

    def __init__(self, items=None, container=None):
        """NOTE: strings and all kinds of mappings have the same Iterable
        interface, so choose wisely.
        """
        self.inner_validator = items and items() or Whatever()
        self.container_type = container or abc.Iterable


class Mapping(BaseControlledValidator):
    """
    Pretty much what you expect - maps keys to values, which are
    controlled by keys_type and values_type validator respectively.
    """

    keys_type = InstanceOf(PredicateController)
    values_type = InstanceOf(PredicateController)
    container_type = SubclassOf(abc.Mapping)

    def predicate(self, value_to_check):
        return (
            isinstance(value_to_check, self.container_type) and
            all(
                self.keys_type.predicate(key) and
                self.values_type.predicate(value)
                for key, value in value_to_check.items()
            )
        )

    def __init__(self, keys=None, values=None, container=None):
        # keys should be hashble and comparable
        self.keys_type = (
            HasAttr("__eq__") & HasAttr("__hash__") & (keys or Whatever)
        )
        self.values_type = values or Whatever
        self.container_type = container or abc.Mapping


class NAryConstructor(BaseControlledValidator):
    """
    Base class for any validator that binds a bunch of other validators
    together. See SomeOf and CombineFrom code below.
    """

    combined_from = Container(
        InstanceOf(PredicateController), container=list
    )

    def __init__(self, *combine_from):
        self.combined_from = list(controller() for controller in combine_from)


class Or(NAryConstructor):

    def predicate(self, value):
        return any(checker.predicate(value) for checker in self.combined_from)


class And(NAryConstructor):

    def predicate(self, value):
        return all(checker.predicate(value) for checker in self.combined_from)


class Xor(NAryConstructor):

    def predicate(self, value):
        return reduce(
            xor,
            (checker.predicate(value) for checker in self.combined_from),
            False
        )

# Alias name, does it make sense to you?
Choose = Xor

