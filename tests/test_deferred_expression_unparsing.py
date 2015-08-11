# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.deferred_expression import \
    DE_Base, \
    DE_Repr, DE_Str, DE_And, DE_Or, DE_Not, \
    DE_Const


_data = collections.OrderedDict()

Param = collections.namedtuple('Param', ('de', 'expression'))

_data['a'] = Param(1 + 2 * DE_Const(3) - 5, "1 + 2 * 3 - 5")
_data['b'] = Param(1 + (2 * DE_Const(3)) - 5, "1 + 2 * 3 - 5")
_data['c'] = Param(1 + 2 * (DE_Const(3) - 5), "1 + 2 * (3 - 5)")
_data['d'] = Param(1 + 2 * (DE_Const([1, 2, 3, 4])[DE_Const(0) * 1 - 3] - 5), "1 + 2 * ([1, 2, 3, 4][0 * 1 - 3] - 5)")
_data['e'] = Param("abc" + DE_Str((DE_Const(2) + 3) * 5), "'abc' + str((2 + 3) * 5)")
_data['f'] = Param(DE_Const("abc ").upper() + (DE_Const("heLlo ") * 2).title(), "'abc '.upper() + ('heLlo ' * 2).title()")

@pytest.fixture(params=tuple(_data.values()), ids=tuple(_data.keys()))
def param(request):
    return request.param


def test_DeferredExpression_expression(param):
    assert isinstance(param.de, DE_Base)
    expression = param.de.expression()
    assert expression == param.expression
    value = eval(expression)
    assert param.de.evaluate() == value
