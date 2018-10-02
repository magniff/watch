import copy


# this should provide watch.builtins, which on its own
# depends on this core module
import watch


class AttributeDescriptor:
    """This class expresses some common logic for every attribute descriptor,
    not biggy.
    """

    def __getattr__(self, attribute):
        if attribute == "field_name":
            raise TypeError(
                "In order to use %s as a descriptor-validator, you should "
                "inherit your class from watch.WatchMe type." % repr(self)
            )
        return super().__getattribute__(attribute)

    def __get__(self, passed_instance, passed_type=None):
        # when attr being looked up in the class instead of instance
        # "passed_type" is always not None
        if passed_instance is None:
            return self
        try:
            return passed_instance.__dict__[self.field_name]
        except KeyError as key_error:
            attribute_error = AttributeError(
                "%s object has no attribute '%s'." %
                (
                    type(passed_instance).__qualname__, self.field_name
                )
            )
            raise attribute_error from key_error

    def __set__(self, passed_instance, value):
        passed_instance.__dict__[self.field_name] = value
        return None


class PredicateController(AttributeDescriptor):
    """Base class for any validator type in 'watch'.

    Uses python`s late binding to introduce magics like __and__ way before
    corresponding predicate nodes being implemented.
    """
    predicate = None

    def __rshift__(self, value):
        return watch.builtins.Mapping(keys=self, values=value)

    def __gt__(self, value):
        return self & watch.builtins.GtThen(value)

    def __ge__(self, value):
        return self & watch.builtins.GtEqThen(value)

    def __lt__(self, value):
        return self & watch.builtins.LtThen(value)

    def __le__(self, value):
        return self & watch.builtins.LtEqThen(value)

    def __invert__(self):
        return watch.builtins.Not(self)

    def __or__(self, other):
        return watch.builtins.Or(self, other)

    def __and__(self, other):
        return watch.builtins.And(self, other)

    def __xor__(self, other):
        return watch.builtins.Xor(self, other)

    def __set__(self, passed_instance, value):
        if passed_instance.keep_eye_on_me:
            if self.predicate(value):
                super().__set__(passed_instance, value)
            else:
                passed_instance.complain(self.field_name, value)
        else:
            super().__set__(passed_instance, value)

    def __call__(self):
        return self


class AttributeControllerMeta(type):
    """Basic meta for watch.WatchMe. Its main concern is to bind descriptors
    to actual attributes in class.
    """

    def __setattr__(self, attr_name, value):
        if isinstance(value, PredicateController):
            value.field_name = attr_name
        super().__setattr__(attr_name, value)

    def __new__(cls, class_name, bases, attributes):
        for name, value in attributes.items():
            is_value_descriptor = (
                isinstance(value, AttributeDescriptor) or
                (
                    isinstance(value, type) and
                    issubclass(value, AttributeDescriptor)
                )
            )
            if is_value_descriptor:
                # each watched typed receives its own copy of
                # descriptor instance
                value_snapshot = copy.deepcopy(value())
                value_snapshot.field_name = name
                attributes[name] = value_snapshot

        return super().__new__(cls, class_name, bases, attributes)


class WatchMe(metaclass=AttributeControllerMeta):
    """Inherit this class to make your class controlled by watch.
    """

    # global validation flag, override it for any child type or even certain
    # instance to disable validation
    keep_eye_on_me = True

    def generate_error_message(self, field_name, value):
        return (
            "watch: Failed to set attribute '%s' of object %s to be %s." %
            (
                field_name, object.__repr__(self), value
            )
        )

    def complain(self, field_name, value):
        """This method is invoked on setattr validation failure.
        It is up to the class to decide how to handle validation error.
        """
        raise AttributeError(
            self.generate_error_message(field_name, value)
        )

