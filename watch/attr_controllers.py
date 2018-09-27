import copy


class AttributeDescriptor:
    """This class expresses some common logic for every attribute descriptor,
    not biggy.
    """
    def __getattr__(self, attr_name):
        if attr_name == 'field_name':
            raise TypeError(
                'In order to use %s as a descriptor-validator, you should '
                'inherit your class from watch.WatchMe.' % repr(self)
            )
        return super().__getattribute__(attr_name)

    def __get__(self, obj, klass=None):
        # when attr being looked up in the class instead of instance
        # "klass" is always not None
        if obj is None:
            return self

        try:
            return obj.__dict__[self.field_name]
        except KeyError:
            raise AttributeError(
                "Object %s has no attribute '%s'." % (obj, self.field_name)
            )

    def __set__(self, obj, value):
        obj.__dict__[self.field_name] = value


class PredicateController(AttributeDescriptor):
    """Base class for any validator type in 'watch'.
    """
    predicate = None

    def __set__(self, obj, value):
        if self.predicate(value):
            super().__set__(obj, value)
        else:
            obj.complain(self.field_name, value)

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

    def __new__(cls, name, bases, attrs):
        for name, value in attrs.items():
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
                attrs[name] = value_snapshot

        return super().__new__(cls, name, bases, attrs)


class WatchMe(metaclass=AttributeControllerMeta):
    """Inherit this class to make your class controlled by watch.
    """

    def generate_error_message(self, field_name, value):
        return (
            "Failed to set attribute '%s' of object %s to be %s." %
            (
                field_name, object.__repr__(self), object.__repr__(value)
            )
        )

    def complain(self, field_name, value):
        """This method is invoked on setattr validation failure.
        It is up to the class to decide how to handle validation error.
        """
        raise AttributeError(
            self.generate_error_message(field_name, value)
        )

