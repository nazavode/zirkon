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

from common.fixtures import simple_container, \
                            string_io

from daikon.section import Section
from daikon.section_schema import SectionSchema
from daikon.validation_section import ValidationSection
from daikon.validator import IntValidator, StrValidator, \
    FloatTupleValidator, StrOptionValidator
from daikon.validator.error import TypeValidationError


@pytest.fixture
def simple_schema_content():
    return collections.OrderedDict((
        ('a', 'Int(min=1)'),
        ('sub', collections.OrderedDict((
            ('sa', 'Float(max=10)'),
            ('sb', IntValidator(default=3)),
            ('sc', StrValidator()),
            ('subsub', collections.OrderedDict((
                           ('ssx', StrOptionValidator(values=("alpha", "beta", "gamma"))),
                           ('ssy', 'FloatTuple(item_max=5.5)'),
            ))),
        ))),
    ))

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

def test_SectionSchema_create(simple_container, string_io):
    section_schema = SectionSchema(container=simple_container)
    section_schema.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_SectionSchema_init(simple_container, string_io, simple_schema_content):
    section_schema = SectionSchema(container=simple_container, init=simple_schema_content)
    section_schema.dump()
    section_schema.dump(stream=string_io)
    assert string_io.getvalue() == """\
a = IntValidator(min=1)
[sub]
    sa = FloatValidator(max=10)
    sb = IntValidator(default=3)
    sc = StrValidator()
    [subsub]
        ssx = StrOptionValidator(values=('alpha', 'beta', 'gamma'))
        ssy = FloatTupleValidator(item_max=5.5)
"""

def test_SectionSchema_err(simple_container, string_io, simple_schema_content):
    init = simple_schema_content
    init['a'] = 2
    with pytest.raises(TypeError) as exc_info:
        section_schema = SectionSchema(container=simple_container, init=init)

def test_SectionSchema_err(simple_container, string_io, simple_schema_content):
    init = simple_schema_content
    init['a'] = 'Int('
    with pytest.raises(TypeValidationError) as exc_info:
        section_schema = SectionSchema(container=simple_container, init=init)
    assert str(exc_info.value) == """a='Int(': cannot create a validator from string 'Int(': SyntaxError: unexpected EOF while parsing (<string>, line 1)"""

def test_SectionSchema_validate_0(simple_container, string_io, simple_schema_content, simple_section_content):
    section_schema = SectionSchema(container=simple_container, init=simple_schema_content)
    section = Section(container=collections.OrderedDict(), init=simple_section_content)
    validation_section = section_schema.validate(section)
    assert isinstance(validation_section, ValidationSection)
    assert not validation_section
