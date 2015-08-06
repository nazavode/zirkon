# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from daikon.toolbox.registry import Registry


@pytest.fixture
def base_registry_class():
    class BaseRegistry(Registry):
        pass
    return BaseRegistry

def test_Registry_classes(base_registry_class):
    l0 = list(base_registry_class.classes())
    assert len(l0) == 0

def test_Registry_classes_include_self(base_registry_class):
    ls = list(base_registry_class.classes(include_self=True))
    assert len(ls) == 1
    assert ls[0] is base_registry_class

def test_Registry_classes_include_abstract(base_registry_class):
    la = list(base_registry_class.classes(include_abstract=True))
    assert len(la) == 0

def test_Registry_class_dict(base_registry_class):
    class ARegistry(base_registry_class): pass
    class CRegistry(base_registry_class): pass
    class BRegistry(base_registry_class): pass
    sd = base_registry_class.class_dict()
    assert len(sd) == 3
    sl = list(sd.keys())
    assert sl == ['ARegistry', 'CRegistry', 'BRegistry']

def test_Registry_get_class(base_registry_class):
    class ARegistry(base_registry_class): pass
    class CRegistry(base_registry_class): pass
    class BRegistry(base_registry_class): pass
    assert base_registry_class.get_class('CRegistry') is CRegistry

def test_Registry_get_class(base_registry_class):
    class ARegistry(base_registry_class): pass
    class CRegistry(base_registry_class):
        @classmethod
        def class_tag(cls):
            return 'C'
    class BRegistry(base_registry_class): pass
    sd = base_registry_class.class_dict()
    assert len(sd) == 3
    sl = list(sd.keys())
    assert sl == ['ARegistry', 'C', 'BRegistry']
    assert base_registry_class.get_class('C') is CRegistry
    assert base_registry_class.get_class('CRegistry') is None
    assert base_registry_class.get_class('CRegistry', ARegistry) is ARegistry

def test_Registry_get_class_tags(base_registry_class):
    class XRegistry(base_registry_class):
        @classmethod
        def class_tag(cls):
            return cls.__name__[:-len("Registry")]
    class ARegistry(XRegistry): pass
    class CRegistry(XRegistry): pass
    class BRegistry(XRegistry): pass
    assert list(base_registry_class.get_class_tags()) == ['X', 'A', 'C', 'B']
    assert list(XRegistry.get_class_tags()) == ['A', 'C', 'B']
