# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.deferred_expression import \
    DE_Base, \
    DE_Repr, DE_Str, DE_And, DE_Or, DE_Not, \
    DE_Const


## unary
_unary_bool_operands = [True, False]
@pytest.fixture(params=_unary_bool_operands, ids=[str(o) for o in _unary_bool_operands])
def bval1(request):
    return request.param

_unary_bool_operator = collections.OrderedDict()
_unary_bool_operator['Not'] = DE_Not
_unary_bool_operator['Str'] = DE_Str
_unary_bool_operator['Repr'] = DE_Repr
@pytest.fixture(ids=tuple(_unary_bool_operator.keys()), params=tuple(_unary_bool_operator.values()))
def bop1(request):
    return request.param

## binary
_binary_bool_operands = [(True, True), (True, False), (False, False)]
@pytest.fixture(params=_binary_bool_operands, ids=[str(o) for o in _binary_bool_operands])
def bval2(request):
    return request.param


_binary_bool_operator = collections.OrderedDict()
_binary_bool_operator['eq'] = lambda l, r: l == r
_binary_bool_operator['ne'] = lambda l, r: l != r
_binary_bool_operator['lt'] = lambda l, r: l <  r
_binary_bool_operator['le'] = lambda l, r: l <= r
_binary_bool_operator['gt'] = lambda l, r: l >  r
_binary_bool_operator['ge'] = lambda l, r: l >= r
_binary_bool_operator['And'] = DE_And
_binary_bool_operator['Or'] = DE_Or


@pytest.fixture(ids=tuple(_binary_bool_operator.keys()), params=tuple(_binary_bool_operator.values()))
def bop2(request):
    return request.param

###############################
## bool unary:
def test_bool_unary(bop1, bval1):
    e = bop1(DE_Const(bval1))
    assert isinstance(e, DE_Base)
    assert e.evaluate() == bop1(bval1)
    
## bool binary:
def test_bool_binary_vl(bop2, bval2):
    l, r = bval2
    e = bop2(DE_Const(l), r)
    assert e.evaluate() == bop2(l, r)
    
def test_bool_binary_vr(bop2, bval2):
    l, r = bval2
    e = bop2(l, DE_Const(r))
    assert e.evaluate() == bop2(l, r)
    
def test_bool_binary_vlr(bop2, bval2):
    l, r = bval2
    e = bop2(DE_Const(l), DE_Const(r))
    assert e.evaluate() == bop2(l, r)
