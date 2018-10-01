from collections import abc
from operator import xor
from functools import reduce


from .core import PredicateController, WatchMe


class BaseControlledValidator(WatchMe, PredicateController):

    def generate_error_message(self, field_name, value):
        return (
            "It is not allowed to initialize %s object with a value of %s." %
            (
                type(self).__qualname__, value
            )
        )


class Predicate(BaseControlledValidator):
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


Whatever = Predicate(lambda item: True)
Nothing = Predicate(lambda item: False)


class InstanceOf(BaseControlledValidator):
    types = Predicate(
        lambda value: (
            isinstance(value, abc.Iterable) and len(value) > 0 and
            all(isinstance(subvalue, type) for subvalue in value)
        )
    )

    def predicate(self, value):
        return isinstance(value, self.types)

    def __init__(self, *types):
        self.types = tuple(types)


class SubclassOf(BaseControlledValidator):
    types = Predicate(
        lambda value: (
            isinstance(value, abc.Iterable) and
            all(isinstance(subvalue, type) for subvalue in value)
        )
    )

    def predicate(self, value):
        return isinstance(value, type) and issubclass(value, self.types)

    def __init__(self, *types):
        self.types = tuple(types)


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


class HasAttr(BaseControlledValidator):
    """
    Checks that value has given attribute.
    """

    attribute_name = InstanceOf(str)

    def predicate(self, value):
        return hasattr(value, self.attribute_name)

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name


class Container(BaseControlledValidator):
    """
    Container of stuff, every item of which is passed to additional
    inner_type validator.
    Example: Container(Gt(5) & Lt(10))

    Warning: validation actually iterates over the container, thus in some
    cases (e.g. generators) validation may screw up your container.
    """

    items = InstanceOf(PredicateController)
    container_type = SubclassOf(abc.Iterable)

    def predicate(self, value):
        return (
            isinstance(value, self.container_type) and
            all(self.items.predicate(item) for item in value)
        )

    def __init__(self, items=None, container=None):
        """NOTE: strings and all kinds of mappings have the same Iterable
        interface, so choose wisely.
        """
        self.items = items is not None and items or Whatever
        self.container_type = container or abc.Iterable


class Mapping(BaseControlledValidator):
    """
    Pretty much what you expect - maps keys to values, which are
    controlled by 'keys' and 'values' validators respectively.
    """

    keys = InstanceOf(PredicateController)
    values = InstanceOf(PredicateController)
    container_type = SubclassOf(abc.Mapping)

    def predicate(self, value_to_check):
        return (
            isinstance(value_to_check, self.container_type) and
            all(
                self.keys.predicate(key) and
                self.values.predicate(value)
                for key, value in value_to_check.items()
            )
        )

    def __init__(self, keys=None, values=None, container=None):
        self.keys = keys or Whatever
        self.values = values or Whatever
        self.container_type = container or abc.Mapping


class NAryConstructor(BaseControlledValidator):
    """
    Base class for any validator that binds a bunch of other validators
    together. See the code for And, Or and Xor nodes below.
    """

    combined_from = Predicate(
        lambda value: (
            isinstance(value, abc.Iterable) and
            len(value) > 0 and
            all(
                isinstance(subvalue, PredicateController) for
                subvalue in value
            )
        )
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


class Just(BaseControlledValidator):
    """Just is an exact match validator, e.g. Just(10) is True only
    for the value of 10.  Accepts multiple init values at once, e.g.
    Just(1,2,3) is the same as Just(1) | Just(2) | Just(3)
    """

    test_against = And(
        Container(HasAttr("__eq__"), container=tuple),
        Predicate(lambda value: len(value) > 0),
    )

    def predicate(self, value):
        return value in self.test_against

    def __init__(self, *values):
        self.test_against = tuple(values)

