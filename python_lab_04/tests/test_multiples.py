import ast
from inspect import getsource
from itertools import islice

import pytest

from lab04.core.errors import InputError
from lab04.core.multiples import multiples_of_three


def test_default_first_twenty():
    assert list(islice(multiples_of_three(), 20)) == list(range(-99, -41, 3))


@pytest.mark.parametrize("start,first", [(0, 0), (2, 3), (6, 6), (-12, -12), (-1, 0), (10**100, 10**100 + 2)])
def test_start_inclusive(start, first):
    assert list(islice(multiples_of_three(start), 3)) == [first, first + 3, first + 6]


@pytest.mark.parametrize("value", [False, "-100", -100.0])
def test_invalid_start(value):
    with pytest.raises(InputError, match="целым числом"):
        next(multiples_of_three(value))


def test_generator_uses_no_collections():
    tree = ast.parse(getsource(multiples_of_three))
    collections = (ast.List, ast.Tuple, ast.Set, ast.Dict, ast.ListComp, ast.SetComp, ast.DictComp)
    assert not any(isinstance(node, collections) for node in ast.walk(tree))
    assert any(isinstance(node, ast.Yield) for node in ast.walk(tree))
