from collections.abc import Iterable
from numbers import Number


import py.test


from watch import WatchMe, Predicate
from watch.builtins import (
    Not, Or, And, Xor, Whatever, Nothing, Container, InstanceOf, SubclassOf,
    Mapping, Just, GtThen, LtThen, LtEqThen, GtEqThen, Nullable
)


CASES = [
    # simple Just
    (
        Just(5),
        [
            (5, True),
            (6, False),
            ("hello", False),
        ]
    ),
    # Nullable + Just
    (
        Nullable(Just(5)),
        [
            (5, True),
            (6, False),
            (None, True),
        ]
    ),
    # Greater
    (
        GtThen(5),
        [
            (4, False),
            (5, False),
            (6, True),
            (6.0, True),
        ]
    ),
    # Greater or Equal
    (
        GtEqThen(5),
        [
            (4, False),
            (5, True),
            (6, True),
            (6.0, True),
        ]
    ),
    # Lesser
    (
        LtThen(5),
        [
            (10, False),
            (5, False),
            (4, True),
            (4.0, True),
        ]
    ),
    # Lesser or Equal
    (
        LtEqThen(5),
        [
            (10, False),
            (5, True),
            (4, True),
            (4.0, True),
        ]
    ),
    # InstanceOf(int)
    (
        InstanceOf(int),
        [
            (10, True),
            (1.1, False),
            ("helloworld", False),
            (True, True),
            (False, True),
        ]
    ),
    # InstanceOf(int, str)
    (
        InstanceOf(int, str),
        [
            (10, True),
            (1.1, False),
            ("helloworld", True),
            (True, True),
            (False, True),
        ]
    ),
    # SubclassOf(Number) but not bool
    (
        SubclassOf(Number) & ~Just(bool),
        [
            (int, True),
            (float, True),
            (complex, True),
            (str, False),
            (bool, False),
        ]
    ),
    # simple predicate
    (
        Predicate(lambda value: value > 0),
        [
            (1, True),
            (-1, False),
        ]
    ),
    # simple negation
    (
        Not(Predicate(lambda value: value > 0)),
        [
            (1, False),
            (-1, True),
        ]
    ),
    # double negation
    (
        Not(Not(Predicate(lambda value: value > 0))),
        [
            (1, True),
            (-1, False),
        ]
    ),
    # simple OR validator: ints or strings
    (
        Or(
            Predicate(
                lambda value: isinstance(value, str)
            ),
            Predicate(
                lambda value: isinstance(value, int)
            ),
        ),
        [
            (1, True),
            (1.0, False),
            ("hello", True),
        ]
    ),
    # basic XOR validator
    (
        Xor(
            Predicate(lambda value: value > 10),
            Predicate(lambda value: value < 20),
        ),
        [
            (5, True),
            (25, True),
            (15, False),
        ]
    ),
    # simple AND: palindromic strings with len > 0
    (
        And(
            Predicate(lambda value: isinstance(value, str)),
            Predicate(lambda value: len(value) > 0),
            Predicate(lambda value: value == value[::-1]),
        ),
        [
            ("kayak", True),
            ("anna", True),
            ("", False),
            ("hello world", False),
            ([1,0,1], False),
            (10, False),
        ]
    ),
    # simple Container
    (
        Container(
            items=And(InstanceOf(int), GtThen(0)),
            container=Iterable
        ),
        [
            (
                (1,2,3), True
            ),
            # mappings are also considered to be containers
            (
                {1: "hello"}, True
            ),
            # WARNING: validation messes up generators
            (
                (value for value in range(-10, 10)), False
            ),
            (
                (value for value in range(1,10)), True
            ),
            ((1,2,3), True),
        ]
    ),
    # nested container: list of tuples of ints
    (
        Container(
            items=Container(items=InstanceOf(int), container=tuple),
            container=list,
        ),
        [
            ([(1,2,3)], True),
            ([(1,2,3), (4,5,6)], True),
            ([(1,2,3), (4,5,"hello")], False),
            ([(1,2,3), [4,5,6]], False),
            ([1,2,3,4], False),
        ]
    ),
]


MAGIC_CASES = [
    # Not
    (
        ~Just("helloworld"),
        [
            ("helloworld", False),
            (10, True),
        ]
    ),
    # Not Not
    (
        ~~Just("helloworld"),
        [
            ("helloworld", True),
            (10, False),
        ]
    ),
    # OR
    (
        Predicate(lambda value: value > 0) | Predicate(lambda value: value < 0),
        [
            (1, True),
            (-1, True),
            (0, False),
        ]
    ),
    # multiple XOR operands are not allowed to be True at the same time
    # meaning that value does not belong to corresponding set intersection
    (
        InstanceOf(int) & (GtThen(10) ^ LtThen(20)),
        [
            (1, True),
            (30, True),
            (15, False),
        ]
    ),
    # OR(Just)
    (
        Just(5) | Just(6),
        [
            (0, False),
            (6, True),
            (5, True),
        ]
    ),
    # OR(Just, Whatever): should falldback to Whatever
    (
        Just(5) | Just(6) | Whatever,
        [
            (6, True),
            (5, True),
            ("hello", True),
        ]
    ),
    # And(Just, Nothing): should falldback to Nothing
    (
        (Just(5) | Just(6)) & Nothing,
        [
            (6, False),
            (5, False),
            ("hello", False),
        ]
    ),
    # Greater
    (
        InstanceOf(int) < 100,
        [
            (10, True),
            (10.1, False),
            (200, False),
            (-10, True),
            (0, True),
        ]
    ),
    # Ints > 0 but not 100
    (
        (InstanceOf(int) > 0) & ~Just(100),
        [
            (10, True),
            (90, True),
            (200, True),
            (100, False),
        ]
    ),
    # Mapping + Just
    (
        Mapping(
            keys=InstanceOf(int),
            values=Just(True)|Just(False),
            container=dict
        ),
        [
            (
                # maps ints to bools
                {value: value % 2 for value in range(10)}, True
            ),
            (
                # maps ints to ints
                {value: value ** 2 for value in range(10)}, False
            ),
        ]
    ),
    # This is the same Mapping + Just case, yet even more magical
    (
        InstanceOf(int) >> Just(True, False),
        # or simply InstanceOf(int) >> InstanceOf(bool)
        [
            (
                # sanity check
                "helloworld", False
            ),
            (
                # maps ints to bools
                {value: value % 2 for value in range(10)}, True
            ),
            (
                # maps ints to ints
                {value: value ** 2 for value in range(10)}, False
            ),
        ]
    ),
    # Container of ints + GT/LT
    (
        Container(
            items=(
                Just("hello") | InstanceOf(int) & (LtThen(0) | GtThen(10))
            ),
            container=list,
        ),
        [
            ([-1, -2, 20], True),
            ([-1, "hello", 20], True),
            ([-1, -2.0, 20], False),
            ([-1, 4, 20], False),
        ]
    ),
    # Mappings + GT
    (
        (InstanceOf(int) > 0) >> InstanceOf(str),
        [
            ("hello", False),
            ({value: str(value) for value in range(1, 10)}, True),
            ({value: str(value) for value in range(-10, 0)}, False),
        ]
    ),
    # Mappings + GT, same good old taste, new experience
    (
        (
            (InstanceOf(int) > 0) >> (InstanceOf(str) >> Just(True, False))
        ),
        [
            ("hello", False),
            ({value: str(value) for value in range(1, 10)}, False),
            ({value: str(value) for value in range(-10, 0)}, False),
            (
                {
                    1: {"hello": True},
                    2: {
                        "more": False,
                        "this": True,
                    },
                },
                True
            ),
        ]
    ),
]


def cases(case_spec):

    for case in case_spec:
        validator, examples = case
        for (test_value, test_result) in examples:
            yield (validator, test_value, test_result)

    return None


@py.test.mark.parametrize(
    "validator,value_to_test,expected_result", cases(CASES)
)
def test_validators(validator, value_to_test, expected_result):
    assert validator().predicate(value_to_test) == expected_result


@py.test.mark.parametrize(
    "validator,value_to_test,expected_result", cases(MAGIC_CASES)
)
def test_magics(validator, value_to_test, expected_result):
    assert validator().predicate(value_to_test) == expected_result

