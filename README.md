# Watch 👁

This very basic library I found myself reimplementing over and over again in different projects, so I finaly decided to put an end to such thankless monkey job, duuuuh. Long story short, this peace of code represents a tiny framework aimed to build object's attributes validators. Usage is fairly straight forward, check out:

``` python
from watch import WatchMe, Pred
class MyClass(WatchMe):
    foo = Pred(lambda item: isinstance(item, int))
```
henceforth attribute `foo` of `MyClass` objects owned by `Pred` descriptor, that basically does `isinstance(value, int)` every time you are setting `value` into `foo`. If `value` doesnt meet requirements of controller, then `complain(self, field_name, value)` method of `MyClass` takes control, by default there is an implementation in `WatchMe` base class, that simply raises `AttribureError`.

### Installation
You can clone this repo and perform installation by running `setup.py` script. This code also available in `pypi` by name `watch`, so to get it from there just run `pip install watch`.

### Main dudes
Currently the main figures on the validation field are:
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

### How to control function arguments and result
There is a thing, known as `PEP 0484`, that proposes a very abstract way of validation of functions arguments and result via annotations. Current library have some support for this pep:
```python
from watch import Pred, watch_this
PositiveInteger = Pred(lambda item: isinstance(item, int) and item > 0)
String = Pred(lambda item: isinstance(item, str))

@watch_this
def factorial(value: PositiveInteger) -> PositiveInteger:
    return 1 if value == 1 else value * factorial(value-1)

# following will raise watch.ArgumentCheckError
>>> factorial("this is sparta")
>>> factorial(0)
# and
@watch_this
def ident_function(value) -> String:
    return value
>>> ident_function(10) # will raise watch.ResultCheckError
```

### How to create custom validator
Even though you can build rather reach validators using only stuff described above, you are welcome to create your own one. The base class of each validator is `watch.PredicateController`, that has method `predicate(value)`, that should return `True` if value fits to object and `False` otherwise. The following example demonstrates how to build validator, that checks whether this value been set earlier:
```python
class Unique(watch.PredicateController):
    def __init__(self):
        self.already_seen = set()

    def predicate(self, value):
        if value in self.already_seen:
            return False
    
        self.already_seen.add(value)
        return True
```
thus
```python
class MyAwesomeClass(watch.WatchMe):
    foo = Unique # yes, you dont really need to instantiate your validators

awesomness = MyAwesomeClass()
>>> awesomness.foo = 1
>>> # lets do it again, validator should catch this
>>> awesomness.foo = 1
AttributeError: Cant set attribute 'foo' of object...
```

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
