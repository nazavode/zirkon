# -*- coding: utf-8 -*-

import collections

import pytest

from zirkon.toolbox.macro import \
    Macro, \
    MRepr, MStr, MAnd, MOr, MNot, \
    MConst


## unary
_unary_bool_operands = [True, False]
@pytest.fixture(params=_unary_bool_operands, ids=[str(o) for o in _unary_bool_operands])
def bval1(request):
    return request.param

_unary_bool_operator = collections.OrderedDict()
_unary_bool_operator['Not'] = MNot
_unary_bool_operator['Str'] = MStr
_unary_bool_operator['Repr'] = MRepr
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
_binary_bool_operator['And'] = MAnd
_binary_bool_operator['Or'] = MOr


@pytest.fixture(ids=tuple(_binary_bool_operator.keys()), params=tuple(_binary_bool_operator.values()))
def bop2(request):
    return request.param

###############################
## bool unary:
def test_bool_unary(bop1, bval1):
    e = bop1(MConst(bval1))
    assert isinstance(e, Macro)
    assert e.evaluate() == bop1(bval1)
    
## bool binary:
def test_bool_binary_vl(bop2, bval2):
    l, r = bval2
    e = bop2(MConst(l), r)
    assert e.evaluate() == bop2(l, r)
    
def test_bool_binary_vr(bop2, bval2):
    l, r = bval2
    e = bop2(l, MConst(r))
    assert e.evaluate() == bop2(l, r)
    
def test_bool_binary_vlr(bop2, bval2):
    l, r = bval2
    e = bop2(MConst(l), MConst(r))
    assert e.evaluate() == bop2(l, r)
