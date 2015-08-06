# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.utils.unrepr import unrepr


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
    Parameters(string="-[3, 2]", expected=SyntaxError("cannot unrepr string '-[3, 2]': col 0: invalid operator UnaryOp followed by [3, 2]")),
    Parameters(string="[3, -2, -()]", expected=SyntaxError("cannot unrepr string '[3, -2, -()]': col 8: invalid operator UnaryOp followed by ()")),
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

def test_unrepr_globals():
    def myfun(x, y, l, *a, **d):
        return x + y + len(l) + len(a) + len(d)

    A_VALUE = 100
    gd = {
        'myfunction': myfun,
        'a': A_VALUE,
        'l1': (1, 2, 3, 4, 5),
        'd1': {'a':1, 'b':2},
    }
    string = "myfunction(10, a, [1, 2, 3], *l1, **d1)"
    assert unrepr(string, globals=gd) == 10 + A_VALUE + len([1, 2, 3]) + len(gd['l1']) + len(gd['d1'])
    string = "a"
    assert unrepr(string, globals=gd) == A_VALUE
