class AttributeDescriptor:

    def __get__(self, obj, klass=None):
        # when attr being looked up in class instead of instance
        if klass is not None and obj is None:
            return self

        if self.field_name not in obj.__dict__:
            raise AttributeError(
                "Object %s has no attribute '%s'." % (obj, self.field_name)
            )
        return obj.__dict__[self.field_name]

    def __set__(self, obj, value):
        obj.__dict__[self.field_name] = value


class PredicateController(AttributeDescriptor):
    predicate = None

    def __set__(self, obj, value):
        if self.predicate(value):
            super().__set__(obj, value)
        else:
            obj.complain(self.field_name, value)

    def __call__(self):
        return self


class AttributeControllerMeta(type):

    def __setattr__(self, attr_name, value):
        if isinstance(value, PredicateController):
            value.field_name = attr_name

        super().__setattr__(attr_name, value)

    def __new__(cls, name, bases, attrs):

        for name, value in attrs.items():
            value_is_descriptor_class = (
                isinstance(value, type) and
                issubclass(value, AttributeDescriptor)
            )

            if value_is_descriptor_class:
                value = value()
                attrs[name] = value

            if isinstance(value, AttributeDescriptor):
                value.field_name = name

        return super().__new__(cls, name, bases, attrs)


class WatchMe(metaclass=AttributeControllerMeta):

    def complain(self, field_name, value):
        raise AttributeError(
            "Cant set attribute '%s' of object %s to be %s." %
            (field_name, self, repr(value))
        )
