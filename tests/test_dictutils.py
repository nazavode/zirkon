# -*- coding: utf-8 -*-

import collections
import os

import pytest

from daikon.toolbox import dictutils


def test_as_dict():
    dct = {}
    stddct = dictutils.as_dict(dct)
    assert stddct == dct
    assert stddct is not dct

def test_as_dict_content():
    dct = {'a': 10, 'b': {'x': 1, 'y': {'r': 222}, 'z': 3}, 'c': 3}
    stddct = dictutils.as_dict(dct)
    assert stddct == dct
    assert stddct is not dct

def test_as_dict_content_conv():
    dct = {'a': 10, 'b': collections.OrderedDict([('x', 1), ('y', collections.OrderedDict([('r', 222)])), ('z', 3)]), 'c': 3}
    stddct = dictutils.as_dict(dct)
    assert stddct == dct
    assert stddct is not dct
    assert type(stddct['b']) == dict
    assert type(stddct['b']['y']) == dict

def test_as_dict_content_conv_depth():
    dct = {'a': 10, 'b': collections.OrderedDict([('x', 1), ('y', collections.OrderedDict([('r', 222)])), ('z', 3)]), 'c': 3}
    stddct = dictutils.as_dict(dct, depth=1)
    assert stddct == dct
    assert stddct is not dct
    assert type(stddct['b']) == dict
    assert type(stddct['b']['y']) == collections.OrderedDict

def test_as_dict_content_class():
    dct = {'a': 10, 'b': {'x': 1, 'y': {'r': 222}, 'z': 3}, 'c': 3}
    stddct = dictutils.as_dict(dct, dict_factory=collections.OrderedDict)
    assert type(stddct) == collections.OrderedDict
    assert type(stddct['b']) == collections.OrderedDict
    assert type(stddct['b']['y']) == collections.OrderedDict

def test_compare_dicts():
    dct0 = {'a': 10, 'b': collections.OrderedDict([('x', 1), ('y', collections.OrderedDict([('r', 222)])), ('z', 3)]), 'c': 3}
    dct1 = {'a': 10, 'b': {'x': 1, 'y': {'r': 222}, 'z': 3}, 'c': 3}
    assert dictutils.compare_dicts(dct0, dct1)

def test_compare_dicts_no_0():
    dct0 = {'a': 10, 'b': collections.OrderedDict([('x', 1), ('y', collections.OrderedDict([('r', 221)])), ('z', 3)]), 'c': 3}
    dct1 = {'a': 10, 'b': {'x': 1, 'y': {'r': 222}, 'z': 3}, 'c': 3}
    assert not dictutils.compare_dicts(dct0, dct1)
    assert not dictutils.compare_dicts(dct1, dct0)

def test_compare_dicts_no_1():
    dct0 = {'a': 10, 'b': collections.OrderedDict([('x', 1), ('z', 3)]), 'c': 3}
    dct1 = {'a': 10, 'b': {'x': 1, 'y': {'r': 222}, 'z': 3}, 'c': 3}
    assert not dictutils.compare_dicts(dct0, dct1)
    assert not dictutils.compare_dicts(dct1, dct0)

def test_transform_0():
    dct0 = {'a': 10, 'b': collections.OrderedDict([('x', 1), ('z', 3)]), 'c': 3}
    dctr = dictutils.transform(dct0, value_transform=str, key_transform=lambda x: '_' + x)
    assert type(dct0) is type(dctr)
    assert type(dct0['b']) is type(dctr['_b'])
    assert str(dct0['a']) == dctr['_a']
    assert str(dct0['b']['x']) == dctr['_b']['_x']
