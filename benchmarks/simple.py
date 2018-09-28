import perf


from watch.builtins import InstanceOf, Container, Mapping
from watch import WatchMe


class MyClass(WatchMe):
    foo = Container(InstanceOf(str) >> InstanceOf(int))


instance = MyClass()
foo = [{'a': 1, 'b': 2, 'c': 3, 'd': 4}]


def bench_set():
    instance.foo = foo


runner = perf.Runner()


WatchMe.active = True
runner.bench_func("set: valve open", bench_set)


WatchMe.active = False
runner.bench_func("set: valve close", bench_set)

