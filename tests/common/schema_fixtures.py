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
__all__ = [
    'simple_schema',
    'simple_schema_content',
    'simple_section_content',
    'SIMPLE_SCHEMA_DUMP',
    'SIMPLE_SCHEMA_JSON_SERIALIZATION',
    'SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION',
]

import collections

import pytest

from daikon.validator import Int, Str, StrOption
from daikon.schema import Schema

from .fixtures import simple_container

@pytest.fixture
def simple_schema_content():
    return collections.OrderedDict((
        ('a', 'Int(min=1)'),
        ('sub', collections.OrderedDict((
            ('sa', 'Float(max=10)'),
            ('sb', Int(default=3)),
            ('sc', Str()),
            ('subsub', collections.OrderedDict((
                           ('ssx', StrOption(values=("alpha", "beta", "gamma"))),
                           ('ssy', 'FloatTuple(item_max=5.5)'),
            ))),
        ))),
    ))

SIMPLE_SCHEMA_DUMP = """\
a = Int(min=1)
[sub]
    sa = Float(max=10)
    sb = Int(default=3)
    sc = Str()
    [subsub]
        ssx = StrOption(values=('alpha', 'beta', 'gamma'))
        ssy = FloatTuple(item_max=5.5)
"""

@pytest.fixture
def simple_section_content():
    return collections.OrderedDict((
        ('a', 10),
        ('sub', collections.OrderedDict((
            ('sa', 0.4),
            ('sb', 10),
            ('sc', "a.dat"),
            ('subsub', collections.OrderedDict((
                ('ssx', "beta"),
                ('ssy', (0.3, 0.4, 0.5, 0.6)),
            ))),
        ))),
    ))

@pytest.fixture
def simple_schema(simple_container, simple_schema_content):
    schema = Schema(container=simple_container, init=simple_schema_content)
    return schema

SIMPLE_SCHEMA_JSON_SERIALIZATION = """\
{
    "a": {
        "__class_name__": "ValidatorBase",
        "__repr__": "Int(min=1)"
    },
    "sub": {
        "sa": {
            "__class_name__": "ValidatorBase",
            "__repr__": "Float(max=10)"
        },
        "sb": {
            "__class_name__": "ValidatorBase",
            "__repr__": "Int(default=3)"
        },
        "sc": {
            "__class_name__": "ValidatorBase",
            "__repr__": "Str()"
        },
        "subsub": {
            "ssx": {
                "__class_name__": "ValidatorBase",
                "__repr__": "StrOption(values=('alpha', 'beta', 'gamma'))"
            },
            "ssy": {
                "__class_name__": "ValidatorBase",
                "__repr__": "FloatTuple(item_max=5.5)"
            }
        }
    }
}
"""

SIMPLE_SCHEMA_CONFIGOBJ_SERIALIZATION = """\
a = Int(min=1)
[sub]
    sa = Float(max=10)
    sb = Int(default=3)
    sc = Str()
    [[subsub]]
        ssx = StrOption(values=('alpha', 'beta', 'gamma'))
        ssy = FloatTuple(item_max=5.5)
"""
