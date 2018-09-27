from collections.abc import Iterable


import py.test


from watch import WatchMe, Predicate
from watch.builtins import Not, Any, All, Container, InstanceOf, Choose


CASES = [
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
        Any(
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
        Choose(
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
        All(
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
            items=Predicate(lambda value: value > 0),
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
                (value for value in range(10)), False
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
    # OR
    (
        Predicate(lambda value: value > 0) | Predicate(lambda value: value < 0),
        [
            (1, True),
            (-1, True),
            (0, False),
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
    assert validator.predicate(value_to_test) == expected_result


@py.test.mark.parametrize(
    "validator,value_to_test,expected_result", cases(MAGIC_CASES)
)
def test_magics(validator, value_to_test, expected_result):
    assert validator.predicate(value_to_test) == expected_result

