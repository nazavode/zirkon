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

from common.fixtures import string_io, late_evaluation

from daikon.schema import Schema
from daikon.config import ROOT, SECTION, Config
from daikon.validator import Int, Float, Str
from daikon.utils import create_template_from_schema

def test_create_template_from_schema(string_io):
    schema = Schema()
    schema['m0'] = Int(default=3)
    schema['m1'] = Int()
    schema['alpha'] = Float(default=0.5)
    schema['input_file'] = Str(min_len=1)
    schema['data'] = {}
    schema['data']['i'] = Int(max=10)
    schema['data']['isub'] = {}
    schema['data']['isub']['a'] = Str()
    schema['data']['isub']['b'] = Str(default='bc')
    schema['data']['isub']['c'] = Str(default=SECTION['b'] * ROOT['m0'])
    schema['data']['isub']['d'] = Str(default=SECTION['b'] * ROOT['m1'])
    schema['data']['j'] = Int(default=2)
    config = create_template_from_schema(schema)
    config.dump(stream=string_io)
    assert string_io.getvalue() == """\
m0 = 3
m1 = '# Int()'
alpha = 0.5
input_file = '# Str(min_len=1)'
[data]
    i = '# Int(max=10)'
    [isub]
        a = '# Str()'
        b = 'bc'
        c = SECTION['b'] * ROOT['m0']
        d = SECTION['b'] * ROOT['m1']
    j = 2
"""

def test_create_template_from_schema_late_evaluation(string_io, late_evaluation):
    schema = Schema()
    schema['m0'] = Int(default=3)
    schema['m1'] = Int(default=ROOT['m0'] + 1)
    config = Config(late_evaluation=late_evaluation)
    create_template_from_schema(schema, config=config)
    
    config.dump(stream=string_io)
    if late_evaluation:
        assert string_io.getvalue() == """\
m0 = 3
m1 = ROOT['m0'] + 1
"""
    else:
        assert string_io.getvalue() == """\
m0 = 3
m1 = 4
"""

