import perf


from watch import WatchMe, ArrayOf, MappingOf
from watch.builtins import InstanceOf


class MyClass(WatchMe):
    foo = ArrayOf(MappingOf(InstanceOf(str), InstanceOf(int)))


my_obj = MyClass()
foo = [{'a': 1, 'b': 2, 'c': 3, 'd': 4}]
my_obj.foo = foo


def bench_get():
    return my_obj.foo


def bench_set():
    my_obj.foo = foo


runner = perf.Runner()
runner.bench_func("__get__", bench_get)
runner.bench_func("__set__", bench_set)
