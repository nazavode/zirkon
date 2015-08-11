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
import os
import shelve

import pytest

from common.fixtures import string_io

from daikon.toolbox.flatmap import FlatMap

from daikon.config import Config


#@pytest.fixture
#def shelf(tmpdir):
#    return shelve.open(os.path.join(tmpdir.strpath, 'x.shelve'))


def test_Config_on_shelf(tmpdir):
    with shelve.open(os.path.join(tmpdir.strpath, 'x.shelve')) as shelf:
        flatshelf = FlatMap(dictionary=shelf)
        config = Config(dictionary=flatshelf)
        config['x'] = 10
        config['y'] = {}
        config['y']['a'] = 'aaa'
        config['y']['b'] = 111
        config['y']['c'] = {'v': 10}
        config['y']['c']['w'] = 20
        config['y']['d'] = 888
        config['z'] = 999
        config_stream = string_io()
        config.dump(stream=config_stream)
        config_dump = config_stream.getvalue()
        assert config_dump == """\
z = 999
x = 10
[y]
    b = 111
    [c]
        v = 10
        w = 20
    a = 'aaa'
    d = 888
"""
    with shelve.open(os.path.join(tmpdir.strpath, 'x.shelve')) as shelf2:
        flatshelf2 = FlatMap(dictionary=shelf2)
        config2 = Config(dictionary=flatshelf2)
        config2_stream = string_io()
        config2.dump(stream=config2_stream)
        config2_dump = config2_stream.getvalue()
        print(config_dump)
        print("---")
        print(config2_dump)
        assert config2_dump == config_dump
    
