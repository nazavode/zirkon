# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.unrepr import unrepr


Parameters = collections.namedtuple('Parameters', ('string', 'expected'))

_data = []

for value in [
              0, 1, -3, +3,
              0., 1, -3, +3,
              "abc", ' dsaf  2 ', r"asfs\dsadf",
              True, False, None,
              [1, "abc", -0.3, False, None],
              (1, "abc", -0.3, False, None),
              [1, ["abc", (),(-0.3, [3, 5, [], False]), None], 2],
              (1, ["abc",    (), (-0.3, [3, 5, [], False]), None], 2),
             ]:
    _data.append(Parameters(string=repr(value), expected=value)),

for string in [
               "0x19a1", "-0x193A", "+0xabc3de",
               "0o123", "-0o234542", "+0o232",
               "list()", "tuple()",
              ]:
    value = eval(string)
    _data.append(Parameters(string=string, expected=value)),

@pytest.fixture(ids=[p.string for p in _data], params=_data)
def param(request):
    return request.param

_bad_data = [
    Parameters(string="-[3, 2]", expected=TypeError("bad operand type for unary -: 'list'")),
    Parameters(string="[3, -2, -()]", expected=TypeError("bad operand type for unary -: 'tuple'")),
]

@pytest.fixture(ids=[p.string for p in _bad_data], params=_bad_data)
def bad_param(request):
    return request.param

def test_unrepr(param):
    assert unrepr(param.string) == param.expected

def test_unrepr_failure(bad_param):
    with pytest.raises(type(bad_param.expected)) as exc_info:
        unrepr(bad_param.string)
    assert str(exc_info.value) == str(bad_param.expected)

def test_unrepr_globals_0():
    assert unrepr("a", globals_d={"a": 102}) == 102

def test_unrepr_globals_1():
    def myfun(x, y, l):
        return x + y + len(l)

    A_VALUE = 100
    gd = {
        'myfunction': myfun,
        'a': A_VALUE,
    }
    string = "myfunction(10, y=a, l=[1, 2, 3])"
    assert unrepr(string, globals_d=gd) == 10 + A_VALUE + len([1, 2, 3])

def test_unrepr_globals():
    def myfun(z1, z2, z3, x1, x2, x3):
        return z1 + z2 + z3 + x1 + x2 + x3

    l1 = [100, 200, 300]
    d1 = {'x1': 1000, 'x2': 2000, 'x3': 3000}
    gd = {
        'myfunction': myfun,
        'l1': l1,
        'd1': d1,
    }
    string = "myfunction(*l1, **d1)"
    assert unrepr(string, globals_d=gd) == sum(l1) + sum(d1.values())
