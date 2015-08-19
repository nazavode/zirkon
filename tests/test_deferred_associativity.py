# -*- coding: utf-8 -*-

import collections

import pytest

from zirkon.toolbox.deferred import DName

py_globals_d = {
    't': 10,
    'x': 4,
    'y': 5,
    'z': 6,
    'w': 7,
}

t = DName(10)
x = DName(4)
y = DName(5)
z = DName(6)
w = DName(7)

de_globals_d = {k: DName(k) for k in py_globals_d}


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

def test_DName(expression):
    de = eval(expression, de_globals_d)
    value = eval(expression, py_globals_d)
    de_expression = de.unparse()
    assert de_expression == expression
    de_value = de.evaluate(de_globals_d)
    assert de_value == value

def test_DName_no_match(expression_no_match):
    de = eval(expression_no_match, de_globals_d)
    value = eval(expression_no_match, py_globals_d)
    de_expression = de.unparse()
    assert de_expression != expression_no_match
    de_value = de.evaluate(de_globals_d)
    assert de_value == value
