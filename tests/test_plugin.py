# -*- coding: utf-8 -*-

import inspect
import os

import pytest

from daikon.toolbox.plugin import Plugin


@pytest.fixture
def base_plugin_class():
    class BasePlugin(Plugin):
        pass
    return BasePlugin

def test_Plugin_subclasses(base_plugin_class):
    l0 = list(base_plugin_class.subclasses())
    assert len(l0) == 0

def test_Plugin_subclasses_include_self(base_plugin_class):
    ls = list(base_plugin_class.subclasses(include_self=True))
    assert len(ls) == 1
    assert ls[0] is base_plugin_class

def test_Plugin_subclasses_include_abstract(base_plugin_class):
    la = list(base_plugin_class.subclasses(include_abstract=True))
    assert len(la) == 0

def test_Plugin_subclasses_dict(base_plugin_class):
    class APlugin(base_plugin_class): pass
    class CPlugin(base_plugin_class): pass
    class BPlugin(base_plugin_class): pass
    sd = base_plugin_class.subclasses_dict()
    assert len(sd) == 3
    sl = list(sd.keys())
    assert sl == ['APlugin', 'CPlugin', 'BPlugin']

def test_Plugin_get_plugin(base_plugin_class):
    class APlugin(base_plugin_class): pass
    class CPlugin(base_plugin_class): pass
    class BPlugin(base_plugin_class): pass
    assert base_plugin_class.get_plugin('CPlugin') is CPlugin

def test_Plugin_get_plugin(base_plugin_class):
    class APlugin(base_plugin_class): pass
    class CPlugin(base_plugin_class):
        @classmethod
        def plugin_name(cls):
            return 'C'
    class BPlugin(base_plugin_class): pass
    sd = base_plugin_class.subclasses_dict()
    assert len(sd) == 3
    sl = list(sd.keys())
    assert sl == ['APlugin', 'C', 'BPlugin']
    assert base_plugin_class.get_plugin('C') is CPlugin
    assert base_plugin_class.get_plugin('CPlugin') is None
    assert base_plugin_class.get_plugin('CPlugin', APlugin) is APlugin

def test_Plugin_get_plugin_names(base_plugin_class):
    class XPlugin(base_plugin_class):
        @classmethod
        def plugin_name(cls):
            return cls.__name__[:-len("Plugin")]
    class APlugin(XPlugin): pass
    class CPlugin(XPlugin): pass
    class BPlugin(XPlugin): pass
    assert list(base_plugin_class.get_plugin_names()) == ['X', 'A', 'C', 'B']
    assert list(XPlugin.get_plugin_names()) == ['A', 'C', 'B']
