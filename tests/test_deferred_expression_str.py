# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox.deferred_expression import \
    DE_Base, \
    DE_Repr, DE_Str, DE_And, DE_Or, DE_Not, \
    DE_Const, DE_Len



## unary
_unary_str_operands = ["alpha", "", " a BC d "]
@pytest.fixture(params=_unary_str_operands, ids=[str(o) for o in _unary_str_operands])
def sval1(request):
    return request.param

_unary_str_operator = collections.OrderedDict()
_unary_str_operator['Len'] = DE_Len
_unary_str_operator['Str'] = DE_Str
_unary_str_operator['Repr'] = DE_Repr
_unary_str_operator['Not'] = DE_Not
@pytest.fixture(ids=tuple(_unary_str_operator.keys()), params=tuple(_unary_str_operator.values()))
def sop1(request):
    return request.param

## binary
_binary_str_operands = [("alpha", "beta"), ("", ".dot"), ("a", "")]
@pytest.fixture(params=_binary_str_operands, ids=[str(o) for o in _binary_str_operands])
def sval2(request):
    return request.param


_binary_str_operator = collections.OrderedDict()
_binary_str_operator['add'] = lambda l, r: l + r
_binary_str_operator['eq'] = lambda l, r: l == r
_binary_str_operator['ne'] = lambda l, r: l != r
_binary_str_operator['lt'] = lambda l, r: l <  r
_binary_str_operator['le'] = lambda l, r: l <= r
_binary_str_operator['gt'] = lambda l, r: l >  r
_binary_str_operator['ge'] = lambda l, r: l >= r


@pytest.fixture(ids=tuple(_binary_str_operator.keys()), params=tuple(_binary_str_operator.values()))
def sop2(request):
    return request.param

_binary_str_method0 = [
    'lower',
    'upper',
    'title',
    'split',
    'strip',
]
@pytest.fixture(params=_binary_str_method0)
def smethod0(request):
    return request.param

###############################
## str unary:
def test_str_unary(sop1, sval1):
    e = sop1(DE_Const(sval1))
    assert isinstance(e, DE_Base)
    assert e.evaluate() == sop1(sval1)
    
## str binary:
def test_str_binary_vl(sop2, sval2):
    l, r = sval2
    e = sop2(DE_Const(l), r)
    assert e.evaluate() == sop2(l, r)
    
def test_str_binary_vr(sop2, sval2):
    l, r = sval2
    e = sop2(l, DE_Const(r))
    assert e.evaluate() == sop2(l, r)
    
def test_str_binary_vlr(sop2, sval2):
    l, r = sval2
    e = sop2(DE_Const(l), DE_Const(r))
    assert e.evaluate() == sop2(l, r)

###############################
def test_str_method0(smethod0, sval1):
    vm = getattr(sval1, smethod0)
    e = DE_Const(sval1)
    em = getattr(e, smethod0)
    assert vm is not em
    emv = em().evaluate()
    assert vm() == emv
    
def test_str_method_join():
    s = ', '
    l = ['a', ' b ', 'cde', '12']
    e = DE_Const(s)
    em = e.join(l)
    assert s.join(l) == em.evaluate()
