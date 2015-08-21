# -*- coding: utf-8 -*-

import collections

import pickle

import pytest

from zirkon.toolbox.macro import \
    MName, MConst, MCall, MContains

Param = collections.namedtuple('Param', ('de', 'expression', 'globals_d'))

def myfun1(a, b, c):
    return a + b // c

def myfun2(a, b, c):
    return a - b + c

y_20 = 20
y_10 = 10


MYFUN = MName("myfun")
X = MConst(10)
Y = MName('y')
Z = MConst(4)

Param = collections.namedtuple('Param', ('globals_d', 'expression'))
_data = [
    Param(globals_d={'myfun': myfun1, 'y': y_20}, expression="myfun(10, c=4, b=y)"),
    Param(globals_d={'myfun': myfun2, 'y': y_20}, expression="myfun(10, c=4, b=y)"),
]

@pytest.fixture(params=_data, ids=tuple(enumerate(_data)))
def param(request):
    return request.param

def test_MCall(param):
    p_args = (X,)
    n_args = collections.OrderedDict()
    n_args['c'] = Z
    n_args['b'] = Y
    de = MCall(MYFUN, p_args, n_args)
    expression = param.expression
    globals_d = param.globals_d
    assert de.unparse() == expression
    value = eval(expression, globals_d)
    assert de.evaluate(globals_d) == value

ParamString = collections.namedtuple('ParamString', ('expression', 'string'))
_data = [
    ParamString(expression=(Y + -X) * -15, string="MMul(MAdd(MName('y'), MNeg(MConst(10))), -15)"),
    ParamString(expression=Y(X), string='MCall(y, (10,), {})'),
    ParamString(expression=(MName('y', {'y': 10}) + -X) * -15, string="MMul(MAdd(MName('y', {'y': 10}), MNeg(MConst(10))), -15)"),
]

@pytest.fixture(params=_data, ids=list(enumerate(_data)))
def pstring(request):
    return request.param

def test_str(pstring):
    assert str(pstring.expression) == pstring.string

def test_contains():
    l = [1, 2, 3]
    L = MName('l')
    d = MContains(X, L)
    print(type(X), type(L))
    print(type(d))
    dv = d.evaluate({'l': l})
    assert isinstance(dv, bool)
    assert not dv
    l.append(X.value)
    dv = d.evaluate({'l': l})
    assert isinstance(dv, bool)
    assert dv
    assert d.unparse() == "10 in l"

_data = [
    X,
    X + Y,
    -X + Y,
    X(Y),
    MName('fff'),
]

@pytest.fixture(params=_data, ids=list(enumerate(_data)))
def pexpr(request):
    return request.param

def test_pickle(pexpr):
    ds = pickle.dumps(pexpr)
    d = pickle.loads(ds)
    assert d == pexpr
