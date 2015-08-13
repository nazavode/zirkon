# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.deferred import \
    Deferred, \
    DRepr, DStr, DAnd, DOr, DNot, \
    DConst


_data = collections.OrderedDict()

Param = collections.namedtuple('Param', ('de', 'expression'))

_data['a'] = Param(1 + 2 * DConst(3) - 5, "1 + 2 * 3 - 5")
_data['b'] = Param(1 + (2 * DConst(3)) - 5, "1 + 2 * 3 - 5")
_data['c'] = Param(1 + 2 * (DConst(3) - 5), "1 + 2 * (3 - 5)")
_data['d'] = Param(1 + 2 * (DConst([1, 2, 3, 4])[DConst(0) * 1 - 3] - 5), "1 + 2 * ([1, 2, 3, 4][0 * 1 - 3] - 5)")
_data['e'] = Param("abc" + DStr((DConst(2) + 3) * 5), "'abc' + str((2 + 3) * 5)")
_data['f'] = Param(DConst("abc ").upper() + (DConst("heLlo ") * 2).title(), "'abc '.upper() + ('heLlo ' * 2).title()")

@pytest.fixture(params=tuple(_data.values()), ids=tuple(_data.keys()))
def param(request):
    return request.param


def test_DeferredExpression_expression(param):
    assert isinstance(param.de, Deferred)
    expression = param.de.expression()
    assert expression == param.expression
    value = eval(expression)
    assert param.de.evaluate() == value
