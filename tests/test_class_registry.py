# -*- coding: utf-8 -*-

import pytest

from daikon.utils.class_registry import ClassRegistry


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


@pytest.fixture
def class_registry():
    cr = ClassRegistry(default_factory=lambda : 123)
    cr.register(A1, 'a1')
    cr.register(A2, 'a2')
    cr.register(C, 'c')
    return cr

def test_ClassRegistry_A2(class_registry):
    assert class_registry.get(A2) == 'a2'

def test_ClassRegistry_A2_exact(class_registry):
    assert class_registry.get(A2, exact=True) == 'a2'

def test_ClassRegistry_DA2(class_registry):
    assert class_registry.get(DA2) == 'a2'

def test_ClassRegistry_DA2_exact(class_registry):
    assert class_registry.get(DA2, exact=True) == 123

def test_ClassRegistry_A1(class_registry):
    assert class_registry.get(A1) == 'a1'

def test_ClassRegistry_DA1(class_registry):
    assert class_registry.get(DA1) == 'a1'

def test_ClassRegistry_DA0(class_registry):
    assert class_registry.get(DC) == 'c'

def test_ClassRegistry_DC(class_registry):
    assert class_registry.get(DC) == 'c'

def test_ClassRegistry_D(class_registry):
    assert class_registry.get(D) == 123


