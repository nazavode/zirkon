# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.deferred import deferred
from daikon.toolbox.deferred_expression import DEConst


Parameters = collections.namedtuple('Parameters', ('string', 'globals_d', 'expected'))

_data = []

_globals_d = {'list': list, 'tuple': tuple}
for string in [
              "-10.0 * 2**8",
               "0x19a1", "-0x193A", "+0xabc3de",
               "0o123", "-0o234542", "+0o232",
               "list([1, 2, 3])[-1]", "tuple([1, 2])",
              ]:
    value = eval(string)
    _data.append(Parameters(string=string, globals_d=_globals_d, expected=value)),

@pytest.fixture(ids=[p.string for p in _data], params=_data)
def param(request):
    return request.param

def test_deferred(param):
    d = deferred(param.string, globals_d=param.globals_d)
    assert d() == param.expected

def test_deferred_late_evaluation():
    xlist = []
    d = deferred("len(x)", {'x': xlist, 'len': len})
    assert d() == 0
    xlist.append(10)
    assert d() == 1
    xlist.append(20)
    xlist.append(30)
    xlist.append(40)
    assert d() == 4
    del xlist[1:-1]
    assert d() == 2

def test_deferred_DeferredExpression():
    de = (2 + DEConst(4)) * 5
    defer = deferred(de)
    assert defer.expression == "(2 + 4) * 5"
    assert defer() == 30
