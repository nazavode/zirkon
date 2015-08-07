# -*- coding: utf-8 -*-
#
# Copyright 2013 Simone Campagna
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__author__ = "Simone Campagna"

import collections
import io

import pytest

from daikon.toolbox.flatmap import FlatMap

@pytest.fixture
def content():
    return collections.OrderedDict([
        ('a', 10),
        ('b', 20),
        ('sub', collections.OrderedDict([
            ('x', 1),
            ('y', 2),
        ])),
        ('c', 30),
    ])

@pytest.fixture
def flat_content():
    return collections.OrderedDict([
        ('a', 10),
        ('b', 20),
        ('c', 30),
    ])

def flatten(d, prefix=''):
    r = collections.OrderedDict()
    for key, value in d.items():
        if isinstance(value, collections.Mapping):
            sub_prefix = prefix + key + '.'
            r[sub_prefix] = None
            sub_value = flatten(value, prefix=sub_prefix)
            r.update(sub_value)
        else:
            r[prefix + key] = value
    return r

@pytest.fixture
def flatmap(content):
    return FlatMap(init=content)

_key_errors = [
    (10, TypeError),
    (1.0, TypeError),
    ("9z", ValueError),
    ("", ValueError),
    ("a.b", ValueError),
]
@pytest.fixture(params=_key_errors, ids=[p[0] for p in _key_errors])
def key_error(request):
    return request.param

def test_FlatMap_create():
    flatmap = FlatMap()
    assert len(flatmap) == 0
    assert isinstance(flatmap.dictionary, collections.OrderedDict)
    assert len(flatmap.dictionary) == 0

def test_FlatMap_create_init_flat(flat_content):
    flatmap = FlatMap(init=flat_content)
    assert len(flatmap) == len(flat_content)
    assert flatmap.dictionary == flat_content
    assert flatmap.dictionary is not flat_content
    assert isinstance(flatmap['a'], int)

def test_FlatMap_create_init(content):
    flatmap = FlatMap(init=content)
    assert len(flatmap) == len(content)
    assert flatmap.dictionary != content
    flattened_content = flatten(content)
    assert flatmap.dictionary == flattened_content
    assert flatmap.dictionary is not content
    assert isinstance(flatmap['a'], int)
    assert isinstance(flatmap['sub'], FlatMap)
    assert flatmap.dictionary == flatmap['sub'].dictionary
    assert flatmap.prefix != flatmap['sub'].prefix

def test_FlatMap_create_init_pos(content):
    flatmap = FlatMap(content)
    assert len(flatmap) == len(content)
    assert flatmap.dictionary != content
    flattened_content = flatten(content)
    assert flatmap.dictionary == flattened_content
    assert flatmap.dictionary is not content
    assert isinstance(flatmap['a'], int)
    assert isinstance(flatmap['sub'], FlatMap)
    assert flatmap.dictionary == flatmap['sub'].dictionary
    assert flatmap.prefix != flatmap['sub'].prefix

def test_FlatMap_create_dictionary_flat(flat_content):
    flatmap = FlatMap(dictionary=flat_content)
    assert len(flatmap) == len(flat_content)
    assert flatmap.dictionary == flat_content
    assert flatmap.dictionary is flat_content
    assert isinstance(flatmap['a'], int)

def test_FlatMap_get(content):
    flatmap = FlatMap(content)
    value = flatmap.get('a', 123)
    assert value == 10
    value = flatmap.get('A', 123)
    assert value == 123
    value = flatmap.get('sub', 123)
    assert isinstance(value, FlatMap)
    assert value.dictionary == flatmap.dictionary
    assert value.dictionary is flatmap.dictionary
    assert value.prefix != flatmap.prefix
    assert value == FlatMap(init=content['sub'])

def test_FlatMap_set(content):
    flatmap = FlatMap(content)
    flatmap['b'] = 100
    flatmap['sub'] = {'z': 888}
    assert flatmap == collections.OrderedDict([
        ('a', 10),
        ('b', 100),
        ('sub', collections.OrderedDict([
            ('z', 888),
        ])),
        ('c', 30),
    ])

def test_FlatMap_set_par_err(content):
    flatmap = FlatMap(content)
    with pytest.raises(ValueError) as exc_info:
        flatmap['b'] = {}
    assert str(exc_info.value) == "cannot replace parameter b with submap"
    with pytest.raises(ValueError) as exc_info:
        flatmap['sub']['x'] = {}
    assert str(exc_info.value) == "cannot replace parameter sub.x with submap"

def test_FlatMap_set_sub_err(content):
    flatmap = FlatMap(content)
    with pytest.raises(ValueError) as exc_info:
        flatmap['sub'] = 'alpha'
    assert str(exc_info.value) == "cannot replace submap sub with parameter"

def test_FlatMap_has_key(content):
    flatmap = FlatMap(content)
    assert flatmap.has_key('a')
    assert flatmap.has_key('sub')
    assert not flatmap.has_key('d')

def test_FlatMap_same_dict(content):
    flatmap = FlatMap(content)
    flatmap2 = FlatMap(dictionary=flatmap.dictionary)
    assert flatmap2 == flatmap

def test_FlatMap_same_dict_prefix(content):
    flatmap = FlatMap(content)
    flatmap2 = FlatMap(dictionary=flatmap.dictionary, prefix='sub.')
    assert flatmap2 != flatmap
    assert flatmap2 == flatmap['sub']

def test_FlatMap_clear(content):
    flatmap = FlatMap(content)
    flatmap.clear()
    assert len(flatmap) == 0
    assert len(flatmap.dictionary) == 0

def test_FlatMap_sub_clear(content):
    flatmap = FlatMap(content)
    lf = len(flatmap)
    ld = len(flatmap.dictionary)
    lfs = len(flatmap['sub'])
    flatmap['sub'].clear()
    assert len(flatmap) == lf
    assert len(flatmap.dictionary) == ld - lfs
    assert len(flatmap['sub'].dictionary) == len(flatmap.dictionary)

def test_FlatMap_key_type_err(content, key_error):
    flatmap = FlatMap(content)
    key, error = key_error
    with pytest.raises(error):
        flatmap[key] = 1
    with pytest.raises(error):
        a = flatmap[key]
    with pytest.raises(error):
        del flatmap[key]
    with pytest.raises(error):
        flatmap.has_key(key)
    with pytest.raises(error):
        flatmap.update({key: 'anything'})
