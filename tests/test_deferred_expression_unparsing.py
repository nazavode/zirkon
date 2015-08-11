# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.deferred_expression import \
    DEBase, \
    DERepr, DEStr, DEAnd, DEOr, DENot, \
    DEConst


_data = collections.OrderedDict()

Param = collections.namedtuple('Param', ('de', 'expression'))

_data['a'] = Param(1 + 2 * DEConst(3) - 5, "1 + 2 * 3 - 5")
_data['b'] = Param(1 + (2 * DEConst(3)) - 5, "1 + 2 * 3 - 5")
_data['c'] = Param(1 + 2 * (DEConst(3) - 5), "1 + 2 * (3 - 5)")
_data['d'] = Param(1 + 2 * (DEConst([1, 2, 3, 4])[DEConst(0) * 1 - 3] - 5), "1 + 2 * ([1, 2, 3, 4][0 * 1 - 3] - 5)")
_data['e'] = Param("abc" + DEStr((DEConst(2) + 3) * 5), "'abc' + str((2 + 3) * 5)")
_data['f'] = Param(DEConst("abc ").upper() + (DEConst("heLlo ") * 2).title(), "'abc '.upper() + ('heLlo ' * 2).title()")

@pytest.fixture(params=tuple(_data.values()), ids=tuple(_data.keys()))
def param(request):
    return request.param


def test_DeferredExpression_expression(param):
    assert isinstance(param.de, DEBase)
    expression = param.de.expression()
    assert expression == param.expression
    value = eval(expression)
    assert param.de.evaluate() == value
