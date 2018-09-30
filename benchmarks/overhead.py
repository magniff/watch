import perf


from watch.builtins import InstanceOf, Container, Mapping
from watch import WatchMe


class MyClass(WatchMe):
    value = Container(InstanceOf(str) >> InstanceOf(int))


class MyClassNoWatch:
    pass


controlled_instance = MyClass()
simple_instance = MyClassNoWatch()


value = [{'a': 1, 'b': 2, 'c': 3, 'd': 4}]


def bench_set():
    controlled_instance.value = value


def pivot_bench_set():
    simple_instance.value = value


runner = perf.Runner()


# Check with validation enabled
WatchMe.keep_eye_on_me = True
runner.bench_func("set: validation enabled", bench_set)

# Check with validation disabled
WatchMe.keep_eye_on_me = False
runner.bench_func("set: validation disabled", bench_set)

# Check with a plain type with no watch at all
runner.bench_func("set: no watch at all", pivot_bench_set)

