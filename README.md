# Watch

This very basic library I found myself reimplementing over and over again in different projects, so I finaly decided to put an end to such thankless monkey job, duuuuh. Long story short, this peace of code represents a tiny framework aimed to build object's attributes validators. Usage is fairly straight forward, check out:

``` python
from watch import WatchMe, Pred
class MyClass(WatchMe):
    foo = primitives.Pred(lambda item: isinstance(item, int))
```
henceforth attribute `foo` of `MyClass` objects owned by `Pred` descriptor, that basically does `isinstance(value, int)` every time you are setting `value` into `foo`. If `value` doesnt meet requirements of controller, then `complain(self, field_name, value)` method of `MyClass` takes control, by default there is an implementation in `WatchMe` base class, that simply raises `AttribureError`.

### Main dudes
Currently the main figures on the validation field are:
```python
from watch import Pred, ArrayOf, SomeOf, CombineFrom
```
lets have a look on them realy fast:
* `Pred` defines a simple function-based validator
```python
class MyClass(WatchMe):
    foo = Pred(lambda value: isinstance(value, int) and value > 5)
```
* `ArrayOf` allows to set a tuple or list of items, that pass some additonal validation
```python
Integer = primitives.Pred(lambda item: isinstance(item, int))
class MyClass(WatchMe):
    foo = ArrayOf(Integer)
    tar = ArrayOf(ArrayOf(Integer))
```
* `SomeOf` basicaly represents `or` operator for validators
```python
class MyClass(WatchMe):
    foo = SomeOf(ArrayOf(Integer), Pred(...))
```
* `CombineFrom` just a sequential validation, it takes value and validates it against Validator0 -> ... -> ValidatorN, and only if every single one is happy about the value validation considered to be complete
```python
String = primitives.Pred(lambda item: isinstance(item, str))
class MyClass(WatchMe):
    # only palindromic strings are allowed
    foo = CombineFrom(String, Pred(lambda string: string == string[::-1]))
```

### How to catch attribute error
You can customize validation failure handler by overriding `complain` method in your class, say:
```python
class MyClass(WatchMe):
    # only palindromic strings are allowed
    foo = CombineFrom(String, Pred(lambda string: string == string[::-1]))
    
    def complain(self, attr_name, value):
        print(attr_name, value)
```
this will print attribute name and corresponding value on screen instead of raising error.