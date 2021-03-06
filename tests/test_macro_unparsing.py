# -*- coding: utf-8 -*-

import collections

import pytest

from zirkon.toolbox.macro import *

_data = collections.OrderedDict()

Param = collections.namedtuple('Param', ('de', 'expression', 'globals_d'))

def FOO(a, x):
    return a + x

BVALUE = 100
CVALUE = -100


_data['a'] = Param(1 + 2 * MConst(3) - 5, "1 + 2 * 3 - 5", None)
_data['b'] = Param(1 + (2 * MConst(3)) - 5, "1 + 2 * 3 - 5", None)
_data['c'] = Param(1 + 2 * (MConst(3) - 5), "1 + 2 * (3 - 5)", None)
_data['d'] = Param(1 + 2 * (MConst([1, 2, 3, 4])[MConst(0) * 1 - 3] - 5), "1 + 2 * ([1, 2, 3, 4][0 * 1 - 3] - 5)", None)
_data['e'] = Param("abc" + MStr((MConst(2) + 3) * 5), "'abc' + str((2 + 3) * 5)", None)
_data['f'] = Param(MConst("abc ").upper() + (MConst("heLlo ") * 2).title(), "'abc '.upper() + ('heLlo ' * 2).title()", None)
_data['g'] = Param(MName('foo')(MConst(9), x=MName('b')), "foo(9, x=b)", {'foo': FOO, 'b': BVALUE})
_data['h'] = Param(abs(MName('c')), "abs(c)", {'c': BVALUE})
_data['i'] = Param(+MConst(2) * -MConst(2), "+2 * -2", None)
_data['j'] = Param(MLen(MConst([1, 2])), "len([1, 2])", None)
_data['k'] = Param(MNot(MConst(2)), "not 2", None)

@pytest.fixture(params=tuple(_data.values()), ids=tuple(_data.keys()))
def param(request):
    return request.param


def test_Macro_expression(param):
    assert isinstance(param.de, Macro)
    expression = param.de.unparse()
    assert expression == param.expression
    globals_d = param.globals_d
    print(globals_d)
    value = eval(expression, globals_d)
    assert param.de.evaluate(globals_d) == value
    s = str(param.de)
    if globals_d:
        gd = globals().copy()
        gd.update(globals_d)
    else:
        gd = globals()
    es = eval(s, gd)
    assert es.evaluate(globals_d) == value
