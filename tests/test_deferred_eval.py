# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.deferred_eval import deferred_eval

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

def test_deferred_eval_no_globals():
    d = deferred_eval("2 * 5")
    assert d() == 10

def test_deferred_eval(param):
    d = deferred_eval(param.string, globals_d=param.globals_d)
    assert d() == param.expected
    assert str(d) == "DeferredEval({!r})".format(param.string)

def test_deferred_eval_late_evaluation():
    xlist = []
    d = deferred_eval("len(x)", {'x': xlist, 'len': len})
    assert d() == 0
    xlist.append(10)
    assert d() == 1
    xlist.append(20)
    xlist.append(30)
    xlist.append(40)
    assert d() == 4
    del xlist[1:-1]
    assert d() == 2

