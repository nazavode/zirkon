# -*- coding: utf-8 -*-

import collections

import pytest

from zirkon.toolbox.catalog import Catalog


class A0(object):
    pass


class A1(A0):
    pass


class A2(A1):
    pass


class B(A0):
    pass


class C(object):
    pass


class DA2(B, A2, C):
    pass


class DA1(B, A1, C):
    pass


class DA0(B, A0, C):
    pass


class DC(B, C):
    pass


class D(B):
    pass


class E0(object):
    pass

class E1(E0):
    pass

class E2(E1):
    pass

class E3(E2):
    pass


_default = 123
@pytest.fixture
def class_registry():
    cr = Catalog(default_factory=lambda : _default)
    cr.register(A1, 'a1')
    cr.register(A2, 'a2')
    cr.register(C, 'c')
    cr.register(E0, 'e0')
    return cr

Parameters = collections.namedtuple('Parameters', ('class_', 'exact', 'expected'))
_data = [
    Parameters(class_=A2,  exact=True,  expected='a2'),
    Parameters(class_=A2,  exact=False, expected='a2'),
    Parameters(class_=DA2, exact=True,  expected=_default),
    Parameters(class_=DA2, exact=False, expected='a2'),
    Parameters(class_=A1,  exact=True,  expected='a1'),
    Parameters(class_=A1,  exact=False, expected='a1'),
    Parameters(class_=DA1, exact=True,  expected=_default),
    Parameters(class_=DA1, exact=False, expected='a1'),
    Parameters(class_=A0,  exact=True,  expected=_default),
    Parameters(class_=A0,  exact=False, expected=_default),
    Parameters(class_=DA0, exact=True,  expected=_default),
    Parameters(class_=DA0, exact=False, expected='c'),
    Parameters(class_=DC,  exact=True,  expected=_default),
    Parameters(class_=DC,  exact=False, expected='c'),
    Parameters(class_=D,   exact=True,  expected=_default),
    Parameters(class_=D,   exact=False, expected=_default),
    Parameters(class_=E3,  exact=False, expected='e0'),
]

@pytest.fixture(params=_data, ids=["{}-{}".format(p.class_.__name__, p.exact) for p in _data])
def param(request):
    return request.param

def test_Catalog_get_t(class_registry, param):
    assert class_registry.get(param.class_, exact=param.exact) == param.expected

def test_Catalog_get_n(class_registry, param):
    assert class_registry.get(param.class_.__name__, exact=param.exact) == param.expected

def test_Catalog_get_by_class(class_registry, param):
    assert class_registry.get_by_class(param.class_, exact=param.exact) == param.expected

def test_Catalog_get_by_name(class_registry, param):
    assert class_registry.get_by_name(param.class_.__name__, exact=param.exact) == param.expected

