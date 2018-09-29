# Watch ๏_๏
[![Build Status](https://api.travis-ci.org/magniff/watch.svg?branch=master)](https://travis-ci.org/magniff/watch)
[![codecov](https://codecov.io/gh/magniff/watch/branch/master/graph/badge.svg)](https://codecov.io/gh/magniff/watch)
----
[![PyPI version](https://badge.fury.io/py/watch.png)](https://badge.fury.io/py/watch)

This very basic library I found myself reimplementing over and over again for different projects, so I finaly decided to put an end to such thankless monkey job, duuuuh. Long story short, this piece of code represents a tiny framework aimed to build object's attributes validators.

### Motivation
The main goal of that library is to get rid of pesky validation code:
```python3
from collections.abc import Mapping

class MyClass:
    def __init__(self, mappings):
       assert isinstance(mappings, list)
       for mapping in mappings:
           assert isinstance(mapping, Mapping)
           for key, value in mapping.items():
               assert isinstance(key, int)
               assert isinstance(value, str)
       self.mappings = mappings
```
Note, that you should perform these assertions each time you set `mappings` attribute to keep your state consistent.
`watch` provides a much cleaner way to define an attribute validator:
```python3
import watch
from watch.builtins import Container, InstanceOf

class MyClass(watch.WatchMe):
     mappings = Container(InstanceOf(int) >> InstanceOf(str), container=list)

     def __init__(self, mappings):
        self.mappings = mappings
```
Here `Container` invocation defines a validator for surrounding `list` object and `>>` constructs a validator for a dict like object, that maps ints to strings. Looks straightforward enough, right?

If that makes sense to you, have a look on `watch` library.

### Installation
You are very welcome to clone this repo and perform installation by running `setup.py` script. This code also available in `pypi` and goes by name `watch`, so to get it from there just run `pip install watch`.

### Validators
Actual list of available validators being significantly reworked for a recent release, so stay tuned for this section. 

### Disabling `watch`
You can disable validation for a particular set of types and even instances. It is done via manipulation of `is_active` attribute of pretty much any `watch` instance.
```python3
>>> import watch
>>> # foo accept no value whatsoever
>>> class SomeClass(watch.WatchMe):
...     foo = watch.builtins.Nothing
... 
>>> s = SomeClass()
>>> s.foo = 10
AttributeError: Failed to set attribute 'foo' of object <__main__.SomeClass object at 0x7fa477d7ef98> to be 10.
>>> # Disable validation for this particular instance
>>> s.is_active = False
>>> # Now foo accepts values
>>> s.foo = 10
>>> # Note, that the flag value does not leak to other instances
>>> s1 = SomeClass()
>>> s1.foo = 10
AttributeError: Failed to set attribute 'foo' of object <__main__.SomeClass object at 0x7fa478491358> to be 10.
```

### Limitations
Note, that the actual validation is based on `__set__` method of attribute descriptor object (see descriptor protocol documentation on python.org web site). Having that said it should be rather clear, that validation of mutable data is (in general) impossible. Condsider following example:
```python3
from watch import WatchMe
from watch.builtins import Container, InstanceOf

class CouldNotBreak(watch.WatchMe):
   # only iterables of ints are allowed, right?
   attribute = Container(InstanceOf(int))

instance = CouldNotBreak()

# that works, as expected
instance.attribute = [1,2,3]

# `watch` is kind of OK with following
instance.attribute.append('hello world')
```
Sure you could revalidate attribute by simply reseting it, just like:
```python3
instance.attribute = instance.attribute
```
But that looks weird indeed.
