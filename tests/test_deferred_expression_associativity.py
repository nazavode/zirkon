# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.deferred_expression import \
    DEBase, DEName

py_globals_d = {
    't': 10,
    'x': 4,
    'y': 5,
    'z': 6,
    'w': 7,
}

t = DEName(10)
x = DEName(4)
y = DEName(5)
z = DEName(6)
w = DEName(7)

de_globals_d = {k: DEName(k) for k in py_globals_d}


_data = [
    "x * y + z * w",
    "x * (y + z) * w",
    "x * y * z * w",
    "x * (y * z) * w",
    "x * y // z * w",
    "x * (y // z) * w",
    "x * y / z * w",
    "x * (y / z) * w",
    "x * y / z * w",
    "x * (y * (z * w))",
    "x + y + z",
    "x ** y ** z",
    #"(x ** y) ** z",
    #"x ** (y ** z)",
]

_data_no_match = [
    "(x * y) * z * w",
    "(x * y * z) * w",
]

@pytest.fixture(params=_data, ids=tuple(enumerate(_data)))
def expression(request):
    return request.param

@pytest.fixture(params=_data_no_match, ids=tuple(enumerate(_data_no_match)))
def expression_no_match(request):
    return request.param

def test_DEName(expression):
    de = eval(expression, de_globals_d)
    value = eval(expression, py_globals_d)
    de_expression = de.expression()
    assert de_expression == expression
    de_value = de.evaluate(de_globals_d)
    assert de_value == value

def test_DEName_no_match(expression_no_match):
    de = eval(expression_no_match, de_globals_d)
    value = eval(expression_no_match, py_globals_d)
    de_expression = de.expression()
    assert de_expression != expression_no_match
    de_value = de.evaluate(de_globals_d)
    assert de_value == value
