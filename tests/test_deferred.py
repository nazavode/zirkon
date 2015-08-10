# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.deferred import deferred


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

def test_unrepr(param):
    d = deferred(param.string, globals_d=param.globals_d)
    assert d() == param.expected

