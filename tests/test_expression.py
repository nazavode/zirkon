# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.expression.expression import \
    Expression, \
    Value


## unary
_unary_int_operands = [1, 2, -3, -4, 0]
@pytest.fixture(params=_unary_int_operands, ids=[str(o) for o in _unary_int_operands])
def ival1(request):
    return request.param

_unary_float_operands = [1.3, 2.34, -3.4, -4.0, 0.0]
@pytest.fixture(params=_unary_float_operands, ids=[str(o) for o in _unary_float_operands])
def fval1(request):
    return request.param

_unary_int_operator = collections.OrderedDict()
_unary_int_operator['abs'] = abs
_unary_int_operator['pos'] = lambda x: +x
_unary_int_operator['neg'] = lambda x: -x
@pytest.fixture(ids=tuple(_unary_int_operator.keys()), params=tuple(_unary_int_operator.values()))
def iop1(request):
    return request.param

## binary
_unary_float_operator = _unary_int_operator
@pytest.fixture(ids=tuple(_unary_float_operator.keys()), params=tuple(_unary_float_operator.values()))
def fop1(request):
    return request.param

_binary_int_operands = [(1, 3), (2, 1), (-3, -3), (-4, 100), (10, 1)]
@pytest.fixture(params=_binary_int_operands, ids=[str(o) for o in _binary_int_operands])
def ival2(request):
    return request.param

_binary_float_operands = [(1.3, 0.5), (2.34, -3.24), (-3.4, -3.4), (-4.0, 0.4), (10.1, 0.1)]
@pytest.fixture(params=_binary_float_operands, ids=[str(o) for o in _binary_float_operands])
def fval2(request):
    return request.param

_binary_num_operator = collections.OrderedDict()
_binary_num_operator['add'] = lambda l, r: l + r
_binary_num_operator['sub'] = lambda l, r: l - r
_binary_num_operator['mul'] = lambda l, r: l * r
_binary_num_operator['div'] = lambda l, r: l / r
_binary_num_operator['floordiv'] = lambda l, r: l // r
_binary_num_operator['mod'] = lambda l, r: l % r
_binary_num_operator['divmod'] = lambda l, r: divmod(l, r)
_binary_num_operator['pow'] = lambda l, r: l ** r
_binary_num_operator['eq'] = lambda l, r: l == r
_binary_num_operator['ne'] = lambda l, r: l != r
_binary_num_operator['lt'] = lambda l, r: l <  r
_binary_num_operator['le'] = lambda l, r: l <= r
_binary_num_operator['gt'] = lambda l, r: l >  r
_binary_num_operator['ge'] = lambda l, r: l >= r


_binary_int_operator = collections.OrderedDict()
_binary_int_operator.update(_binary_num_operator)
@pytest.fixture(ids=tuple(_binary_int_operator.keys()), params=tuple(_binary_int_operator.values()))
def iop2(request):
    return request.param

_binary_float_operator = collections.OrderedDict()
_binary_float_operator.update(_binary_num_operator)

###############################
def test_int_unary(iop1, ival1):
    e = iop1(Value(ival1))
    assert isinstance(e, Expression)
    assert e.evaluate() == iop1(ival1)
    
def test_float_unary(fop1, fval1):
    e = fop1(Value(fval1))
    assert isinstance(e, Expression)
    assert e.evaluate() == fop1(fval1)
  
def test_int_binary_vl(iop2, ival2):
    l, r = ival2
    e = iop2(Value(l), r)
    assert e.evaluate() == iop2(l, r)
    
def test_int_binary_vr(iop2, ival2):
    l, r = ival2
    e = iop2(l, Value(r))
    assert e.evaluate() == iop2(l, r)
    
def test_int_binary_vlr(iop2, ival2):
    l, r = ival2
    e = iop2(Value(l), Value(r))
    assert e.evaluate() == iop2(l, r)
    
