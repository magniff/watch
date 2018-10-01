import py.test


import watch


class Mixin:

    def __setattr__(self, attr, value):
        super().__setattr__("checkpoint", True)
        super().__setattr__(attr, value)


def test_pridicated_bind_to_watchme():
    """Tests, that using a watch's validators inside a class, that not being
    inherited from WatchMe base class generates an error.
    """

    with py.test.raises(TypeError):

        class SomeClass:
            foo = watch.builtins.Whatever

        s = SomeClass()
        s.foo = 10


def test_pridicated_bind_to_watchme():
    """Tests, that AttributeError is not broken by introducing watch lib.
    """

    with py.test.raises(AttributeError):

        class SomeClass(watch.WatchMe):
            foo = watch.builtins.Whatever

        s = SomeClass()
        s.foo


@py.test.mark.parametrize(
    "type_to_check",
    [
        type("_", (Mixin, watch.WatchMe), {"foo": watch.builtins.Nothing}),
        type("_", (watch.WatchMe, Mixin), {"foo": watch.builtins.Nothing}),
    ]
)
def test_mixin_cooperation(type_to_check):
    """Tests, that watch works nicely with mixins
    """

    with py.test.raises(AttributeError):
        instance = type_to_check()
        instance.foo = "hello"

    assert instance.checkpoint

