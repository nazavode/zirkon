# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.deferred_expression import \
    DEBase, DEName

Param = collections.namedtuple('Param', ('de', 'expression', 'globals_d'))

_data = [
    Param(de=3 * DEName('x') - 5,
           expression="3 * x - 5",
           globals_d={'x': 5}),
    Param(de=3 * (DEName('x') - 5),
           expression="3 * (x - 5)",
           globals_d={'x': 4}),
    Param(de=DEName('t') + 3 * (DEName('x') *(DEName('z')- DEName('y'))//DEName('w')),
           expression="t + 3 * (x * (z - y) // w)",
           globals_d={'t': 10, 'x': 4, 'y': 5, 'z': 6, 'w': 7}),
]

@pytest.fixture(params=_data, ids=tuple(enumerate(_data)))
def param(request):
    return request.param

def test_DEName(param):
    de = param.de
    assert isinstance(de, DEBase)
    expression = param.expression
    assert de.expression() == expression
    assert de.evaluate(param.globals_d) == eval(expression, param.globals_d)
