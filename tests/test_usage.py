import py.test


import watch


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


def test_mixin_cooperation_mixin_at_start():
    """Tests, that watch works nicely with mixins
    """

    class SomeMixin:
        def __setattr__(self, attr, value):
            super().__setattr__("checkpoint", True)
            super().__setattr__(attr, value)

    class WatchedClass(SomeMixin, watch.WatchMe):
        foo = watch.builtins.Nothing

    with py.test.raises(AttributeError):
        instance = WatchedClass()
        instance.foo = "hello"

    assert instance.checkpoint


def test_mixin_cooperation_mixin_at_the_end():
    """Tests, that AttributeError is not broken by introducing watch lib.
    """

    class SomeMixin:
        def __setattr__(self, attr, value):
            super().__setattr__("checkpoint", True)
            super().__setattr__(attr, value)


    class WatchedClass(watch.WatchMe, SomeMixin):
        foo = watch.builtins.Nothing

    with py.test.raises(AttributeError):
        instance = WatchedClass()
        instance.foo = "hello"

    assert instance.checkpoint

