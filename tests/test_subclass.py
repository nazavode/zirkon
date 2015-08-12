# -*- coding: utf-8 -*-

import collections

import pytest

from daikon.toolbox import subclass


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


class E(object):
    pass


Parameters = collections.namedtuple('Parameters', ('class_', 'include_self', 'filter', 'expected'))
_data = collections.OrderedDict()
_data['A2-isT-fN'] = Parameters(class_=A2,  include_self=True, filter=None, expected=[A2, DA2])
_data['A2-isF-fN'] = Parameters(class_=A2,  include_self=False, filter=None, expected=[DA2])
_data['A2-isT-f^A'] = Parameters(class_=A2,  include_self=True, filter=lambda x: x.__name__.startswith('A'), expected=[A2])
_data['A2-isF-f^A'] = Parameters(class_=A2,  include_self=False, filter=lambda x: x.__name__.startswith('A'), expected=[])
_data['B-isT-fN'] = Parameters(class_=B,  include_self=True, filter=None, expected=[B, DA2, DA1, DA0, DC, D])

@pytest.fixture(params=tuple(_data.values()), ids=tuple(_data.keys()))
def param(request):
    return request.param

def _sorted_classes(classes):
    return tuple(sorted(classes, key=lambda c: c.__name__))

def test_subclasses(param):
    assert _sorted_classes(subclass.subclasses(param.class_, include_self=param.include_self, filter=param.filter)) == _sorted_classes(param.expected)

def test_find_subclass_found():
    assert subclass.find_subclass(A1, DA1.__name__) is DA1
    assert subclass.find_subclass(A1, DA2.__name__) is DA2

def test_find_subclass_not_found():
    assert subclass.find_subclass(A1, 'DC1') is None

def test_find_subclass_not_found():
    assert subclass.find_subclass(A1, A0.__name__) is None
