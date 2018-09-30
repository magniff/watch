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


