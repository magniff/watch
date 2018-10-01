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
       # "mappings" value is expected to be a list of any mappings from
       # int numbers to strings. Mind how noisy the code becomes.
       assert isinstance(mappings, list)
       for mapping in mappings:
           assert isinstance(mapping, Mapping)
           for key, value in mapping.items():
               assert isinstance(key, int)
               assert isinstance(value, str)
       self.mappings = mappings
```
Also, mind that you will have to perform these assertions each time this `mappings` attribute is set.
`watch` provides a much cleaner way to define an attribute validator:
```python3
import watch
from watch.builtins import Container, InstanceOf

class MyClass(watch.WatchMe):
     mappings = Container(InstanceOf(int) >> InstanceOf(str), container=list)

     def __init__(self, mappings):
        # now self.mappings is guaranteed to comply a given spec at
        # program runtime, atleast at __setattr__ time
        self.mappings = mappings
```
Here `Container` invocation defines a validator for surrounding `list` object and `>>` constructs a validator for a dict like object, that maps ints to strings. Looks straightforward enough, right?

If that makes sense to you, have a look on `watch` library.

### Installation
You are very welcome to clone this repo and perform installation by running `setup.py` script. This code also available in `pypi` and goes by name `watch`, so to get it from there just run `pip install watch`.

### How it is done
Nothing special, really, just a pinch of good old metaprogramming and attribute's descriptor magic, namely `watch` is comprised out of:
- the `core` module, where a bunch of base classes like `WatchMe` and `PredicateController` got defined.
- and the `builtins` module, that defines a set of handy validators like `Just`, `Container`, `Mapping`, etc.
Each validator provides a callable method `predicate(value) -> True/False`. This callable gets invoked at validation time to decide whether the value complies the spec.

### Validators
Did I tell you that `watch` is a microframework? No? So, it is, meaning that you should be able to quickly hack together a set of useful checkers without any external help. Nevertherless, `watch` comes with a set of predefined validators, that are written in a "monadic" style.
Here are some:
```
from watch.builtins import *
```
- `Predicate` is an unary constructor, that takes an unary function as its single argument and returns function's result interpreted in a boolean context:
```python3
>>> Predicate(lambda value: value > 0).predicate(10)
True
>>> Predicate(lambda value: value > 0).predicate(-10)
False
```
- `Just` is an unary constructor, that is super trivial:
```python3
>>> Just("hello").predicate("hello")
True
>>> Just("hello").predicate(10)
False
```
It also can take a list of values as an initialization set:
```python3
>>> Just("hello", "world").predicate("hello")
True
>>> Just("hello", "world").predicate("world")
True
>>> Just("hello", "world").predicate("more")
False
```
- `InstanceOf` and `SubclassOf` are nary constructors that do exactly what you expect. The nice thing about builtin validators is that they are also controlled by `watch` on their own, e.g.
```python3
>>> InstanceOf(int).predicate(10)
True
>>> InstanceOf(10)
AttributeError: It is not allowed to initialize InstanceOf object with a value of (10,).
```
- `Container` is an unary constructor that wraps an arbitrary validator and yields a validator for iterable, each element of which will be validated with this inner validator, e.g.
```python3
>>> Container(InstanceOf(int, str)).predicate(["hello", 1])
True
>>> Container(InstanceOf(int, str)).predicate(["hello", 1.0])
False
```
You can also provide an exact type of the container, e.g.
```python3
>>> Container(InstanceOf(int, str), container=list).predicate([1,2])
True
>>> Container(InstanceOf(int, str), container=tuple).predicate([1,2])
False
```
- `Mapping` is a binary constructor that is very similar to the `Container` one, yet taylored for mappings instead of iterables, e.g.
```python3
>>> Mapping(InstanceOf(int), InstanceOf(str)).predicate({1: "hello"})
True
>>> Mapping(InstanceOf(int), InstanceOf(str)).predicate({1: 1})
False
```
Also there is a magic method based syntax available:
```python3
>>> (InstanceOf(int) >> InstanceOf(str)).predicate({1: "hello"})
```
- `Not` is an unary constructor that wraps an arbitrary validator and negates its result, e.g.
```python3
>>> Not(InstanceOf(int)).predicate(10)
False
>>> Not(InstanceOf(int)).predicate("hello")
True
```
Also there is a magic method based syntax available:
```python3
>>> (~InstanceOf(int)).predicate(10)
False
>>> (~InstanceOf(int)).predicate("hello")
True
```
- `And`, `Or`, `Xor` are nary constructors, that runs inner validators and performs corresponding logical operation.
Magic method based syntax available:
```python3
>>> (InstanceOf(int) | Just("hello")).predicate(10)
True
>>> (InstanceOf(int) | Just("hello")).predicate("hello")
True
>>> (InstanceOf(int) | Just("hello")).predicate("world")
False
>>> # And so on
```
- `GtThen`, `GtEqThen`, `LtThen`, `LtEqThen` are unary constructors, e.g.
```python3
>>> GtThen(10).predicate(2)
False
>>> GtThen(10).predicate(20)
True
```
This validators are usually combined with other validators, e.g.
```python3
>>> And(InstanceOf(int), GtThen(10)).predicate(20)
True
```
or, using magic syntax:
```python3
>>> (InstanceOf(int) > 10).predicate(20)
True
>>> (InstanceOf(int) > 10).predicate(20.0)
False
```

### Disabling `watch`
You can disable validation for a particular set of types and even instances. It is done via manipulation of `keep_eye_on_me` attribute of pretty much any `watch` instance.
```python3
>>> import watch
>>> # foo accept no value whatsoever
>>> class SomeClass(watch.WatchMe):
...     foo = watch.builtins.Nothing
... 
>>> s = SomeClass()
>>> s.foo = 10
AttributeError: Failed to set attribute 'foo' of object <SomeClass object at 0x7f...> to be 10.
>>> # Disable validation for this particular instance
>>> s.keep_eye_on_me = False
>>> # Now foo accepts values
>>> s.foo = 10
>>> # Note, that the flag value does not leak to other instances
>>> s1 = SomeClass()
>>> s1.foo = 10
AttributeError: Failed to set attribute 'foo' of object <SomeClass object at 0x7f...> to be 10.
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
