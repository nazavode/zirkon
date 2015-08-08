# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.deferred import \
    Deferred, \
    Len, Str, Repr, Not, \
    Const


## unary
_unary_str_operands = ["alpha", "", " a BC d "]
@pytest.fixture(params=_unary_str_operands, ids=[str(o) for o in _unary_str_operands])
def sval1(request):
    return request.param

_unary_str_operator = collections.OrderedDict()
_unary_str_operator['Len'] = Len
_unary_str_operator['Str'] = Str
_unary_str_operator['Repr'] = Repr
_unary_str_operator['Not'] = Not
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
    e = sop1(Const(sval1))
    assert isinstance(e, Deferred)
    assert e.evaluate() == sop1(sval1)
    
## str binary:
def test_str_binary_vl(sop2, sval2):
    l, r = sval2
    e = sop2(Const(l), r)
    assert e.evaluate() == sop2(l, r)
    
def test_str_binary_vr(sop2, sval2):
    l, r = sval2
    e = sop2(l, Const(r))
    assert e.evaluate() == sop2(l, r)
    
def test_str_binary_vlr(sop2, sval2):
    l, r = sval2
    e = sop2(Const(l), Const(r))
    assert e.evaluate() == sop2(l, r)

###############################
def test_str_method0(smethod0, sval1):
    vm = getattr(sval1, smethod0)
    e = Const(sval1)
    em = getattr(e, smethod0)
    assert vm is not em
    emv = em().evaluate()
    assert vm() == emv
    
def test_str_method_join():
    s = ', '
    l = ['a', ' b ', 'cde', '12']
    e = Const(s)
    em = e.join(l)
    assert s.join(l) == em.evaluate()
