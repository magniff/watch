class AttributeDescriptor:

    def __get__(self, obj, _=None):
        if self.field_name not in obj.__dict__:
            raise AttributeError(self.field_name)
        return obj.__dict__[self.field_name]

    def __set__(self, obj, value):
        obj.__dict__[self.field_name] = value


class PredicateController(AttributeDescriptor):
    predicate = (lambda *args, **kwargs: True)

    def _complain(self, obj, value):
        raise AttributeError()

    def __set__(self, obj, value):
        if self.predicate(value):
            super().__set__(obj, value)
        else:
            self._complain(obj, value)

    def __call__(self):
        return self


class BaseTypeChecker(PredicateController):
    type_to_check = None

    def predicate(self, value_to_check):
        return (
            isinstance(value_to_check, self.type_to_check) and
            super().predicate(value_to_check)
        )


class AttributeControllerMeta(type):

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


class BaseAutoAttributedClass(metaclass=AttributeControllerMeta):
    pass
