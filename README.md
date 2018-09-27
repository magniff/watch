# Watch ๏_๏
[![Build Status](https://api.travis-ci.org/magniff/watch.svg?branch=master)](https://travis-ci.org/magniff/watch)

This very basic library I found myself reimplementing over and over again in different projects, so I finaly decided to put an end to such thankless monkey job, duuuuh. Long story short, this piece of code represents a tiny framework aimed to build object's attributes validators.

### Motivation
The main goal of that library is to get rid of pesky validation code:
```python
class MyClass:
    def __init__(self, some_mappings):
       assert isinstance(foo, (tuple, list)) and all(isinstance(item, int) for item in foo)
       assert isinstance(bar, str)
       self.this_should_list_of_ints = foo
       self.and_this_should_be_string = bar
```
Note, that you should perform these assertions each time you set attributes foo and bar in order to keep your state consistent.
From my point of view it would be way claner to have the validation expressed like this (pseudocode):
```python
class MyClass:
     foo = List(Int)
     bar = String

     def __init__(self, foo, bar):
        self.foo = foo
        self.bar = bar
```
If that makes sense to you, have a look on `watch` library. Here is a little example:
```python
import watch
class MyClass(watch.WatchMe):
    foo = watch.ArrayOf(watch.builtins.InstanceOf(int)) 

instance = MyClass()
instance.foo = [10, 20]  # allowed
instance.foo = "sup"  # will rise AttributeError
```
henceforth attribute `foo` of `MyClass` objects owned by `ArrayOf` descriptor. If value doesnt meet requirements of controller, then `complain(self, field_name, value)` method of `MyClass` takes control, by default there is an implementation located in `WatchMe` base class, that simply raises `AttribureError`.

### Installation
You can clone this repo and perform installation by running `setup.py` script. This code also available in `pypi` by name `watch`, so to get it from there just run `pip install watch`.

### Main validators
Each validator is represented as a class extending base `PredicateController` type, which main method `predicate` get recursively invoked through nested data. Currently the most expressive validators are following.
```python
from watch import Pred, ArrayOf, MappingOf, SomeOf, CombineFrom
```
lets have a look on them realy fast:
* `Pred` defines a simple function-based validator
```python
class MyClass(WatchMe):
    foo = Pred(lambda value: isinstance(value, int) and value > 5)
```
* `ArrayOf` allows to set a tuple or list of items, that pass some additonal validation
```python
Integer = Pred(lambda item: isinstance(item, int))
class MyClass(WatchMe):
    foo = ArrayOf(Integer)
    tar = ArrayOf(ArrayOf(Integer))
```
* `MappingOf` allows to set an object that has some notion of `items()`
```python
class MyClass(WatchMe):
    # some mapping, which keys allowed to be palindromic strings; valid values are lists
    # of even numbers
    foo = MappingOf(
        keys_type=Pred(lambda item: isinstance(item, str) and item == item[::-1])),
        values_type=ArrayOf(Pred(lambda item: isinstance(item, int) and not item % 2))
    )
```

* `SomeOf` basicaly represents `or` operator for validators
```python
class MyClass(WatchMe):
    foo = SomeOf(ArrayOf(Integer), Pred(...))
```
* `CombineFrom` just a sequential validation, it takes value and validates it against Validator0 -> ... -> ValidatorN, and only if every single one is happy about the value validation considered to be complete
```python
String = Pred(lambda item: isinstance(item, str))
class MyClass(WatchMe):
    # only palindromic strings are allowed
    foo = CombineFrom(String, Pred(lambda string: string == string[::-1]))
```
Note that all of them and each validator, presenting in `watch.builtins` are self-validate, thus you can't construct `watch.builtins.InstanceOf` with non-class.

### Secondary validators
Find more stuff in `watch.builtins`.

### Limitations
Note, that the actual validation is based on `__set__` method of attribute descriptor object (see descriptor protocol documentation on python.org web site). Having that said it should be rather clear, that validation of mutable data is (in general) impossible. Condsider following example:
```python
class CouldNotBreak(watch.WatchMe):
   # only lists or tuples of ints are allowed, right?
   attribute = watch.ArrayOf(watch.builtins.InstanceOf(int))

instance = CouldNotBreak()

# that works, as expected
instance.attribute = [1,2,3]

# `Watch` is kind of OK with following
instance.attribute.append('hello world')
```
Sure you coud revalidate attribute by simply reseting it, like:
```python
instance.attribute = instance.attribute
```
But this looks weird indeed.

### How to handle an attribute error
You can customize validation failure handler by overriding `complain` method in your class, say:
```python
class MyClass(WatchMe):
    # only palindromic strings are allowed
    foo = CombineFrom(String, Pred(lambda string: string == string[::-1]))

    def complain(self, attr_name, value):
        print(attr_name, value)
```
this will print attribute name and corresponding value on screen instead of raising error.

