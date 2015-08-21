# -*- coding: utf-8 -*-

import collections

import pytest

from zirkon.toolbox.macro import MName

py_globals_d = {
    't': 10,
    'x': 4,
    'y': 5,
    'z': 6,
    'w': 7,
}

t = MName(10)
x = MName(4)
y = MName(5)
z = MName(6)
w = MName(7)

de_globals_d = {k: MName(k) for k in py_globals_d}


_data = [
    "x + z // y",
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

def test_MName(expression):
    de = eval(expression, de_globals_d)
    value = eval(expression, py_globals_d)
    de_expression = de.unparse()
    assert de_expression == expression
    de_value = de.evaluate(de_globals_d)
    assert de_value == value

def test_MName_no_match(expression_no_match):
    de = eval(expression_no_match, de_globals_d)
    value = eval(expression_no_match, py_globals_d)
    de_expression = de.unparse()
    assert de_expression != expression_no_match
    de_value = de.evaluate(de_globals_d)
    assert de_value == value
