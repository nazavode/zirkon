# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.deferred_expression import \
    DEBase, DEName, DEConst, DECall

Param = collections.namedtuple('Param', ('de', 'expression', 'globals_d'))

def myfun1(a, b, c):
    return a + b // c

def myfun2(a, b, c):
    return a - b + c

y_20 = 20
y_10 = 10


MYFUN = DEName("myfun")
X = DEConst(10)
Y = DEName('y')
Z = DEConst(4)

Param = collections.namedtuple('Param', ('globals_d', 'expression'))
_data = [
    Param(globals_d={'myfun': myfun1, 'y': y_20}, expression="myfun(10, c=4, b=y)"),
    Param(globals_d={'myfun': myfun2, 'y': y_20}, expression="myfun(10, c=4, b=y)"),
]

@pytest.fixture(params=_data, ids=tuple(enumerate(_data)))
def param(request):
    return request.param

def test_DECall(param):
    p_args = (X,)
    n_args = collections.OrderedDict()
    n_args['c'] = Z
    n_args['b'] = Y
    de = DECall(MYFUN, p_args, n_args)
    expression = param.expression
    globals_d = param.globals_d
    assert de.expression() == expression
    value = eval(expression, globals_d)
    assert de.evaluate(globals_d) == value
