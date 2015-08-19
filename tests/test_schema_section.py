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

import pytest

from common.fixtures import \
    dictionary, \
    generic_dictionary, \
    string_io, \
    simple_section_content, \
    simple_schema_content
from zirkon.section import Section
from zirkon.schema_section import SchemaSection
from zirkon.validation import Validation
from zirkon.validator import Int, Str, \
    FloatTuple, StrChoice
from zirkon.validator.ignore import Ignore
from zirkon.validator.remove import Remove
from zirkon.validator.error import \
    InvalidChoiceError, UnexpectedOptionError


def test_SchemaSection_create(generic_dictionary, string_io):
    schema_section = SchemaSection(dictionary=generic_dictionary)
    schema_section.dump(stream=string_io)
    assert string_io.getvalue() == ""

def test_SchemaSection_init(dictionary, string_io, simple_schema_content):
    schema_section = SchemaSection(dictionary=dictionary, init=simple_schema_content)
    schema_section.dump()
    schema_section.dump(stream=string_io)
    assert string_io.getvalue() == """\
a = Int(min=1)
[sub]
    sa = Float(max=10)
    sb = Int(default=3)
    sc = Str()
    [subsub]
        ssx = StrChoice(choices=['alpha', 'beta', 'gamma'])
        ssy = FloatTuple(item_max=5.5)
"""

def test_SchemaSection_err(generic_dictionary, string_io, simple_schema_content):
    init = simple_schema_content
    init['a'] = 2
    with pytest.raises(TypeError) as exc_info:
        schema_section = SchemaSection(dictionary=generic_dictionary, init=init)

def test_SchemaSection_validate_0(dictionary, generic_dictionary, string_io, simple_schema_content, simple_section_content):
    schema_section = SchemaSection(dictionary=generic_dictionary, init=simple_schema_content)
    section = Section(dictionary=dictionary, init=simple_section_content)
    validation = schema_section.validate(section)
    assert isinstance(validation, Validation)
    assert not validation

def test_SchemaSection_validate_invalid_option(dictionary, generic_dictionary, string_io, simple_schema_content, simple_section_content):
    simple_section_content['sub']['subsub']['ssx'] = "delta"
    schema_section = SchemaSection(dictionary=generic_dictionary, init=simple_schema_content)
    section = Section(dictionary=dictionary, init=simple_section_content)
    validation = schema_section.validate(section)
    assert isinstance(validation, Validation)
    assert validation
    assert len(validation) == 1
    assert len(validation['sub']) == 1
    assert len(validation['sub']['subsub']) == 1
    assert isinstance(validation['sub']['subsub']['ssx'], InvalidChoiceError)

def test_SchemaSection_validate_unexpected(dictionary, generic_dictionary, string_io, simple_schema_content, simple_section_content):
    simple_section_content['sub']['abc'] = 10
    schema_section = SchemaSection(dictionary=generic_dictionary, init=simple_schema_content)
    section = Section(dictionary=dictionary, init=simple_section_content)
    validation = schema_section.validate(section)
    assert isinstance(validation, Validation)
    assert validation
    assert len(validation) == 1
    assert len(validation['sub']) == 1
    assert isinstance(validation['sub']['abc'], UnexpectedOptionError)

def test_SchemaSection_validate_unexpected_ignored(dictionary, generic_dictionary, string_io, simple_schema_content, simple_section_content):
    simple_section_content['sub']['abc'] = 10
    schema_section = SchemaSection(dictionary=generic_dictionary, init=simple_schema_content, unexpected_option_validator=Ignore())
    section = Section(dictionary=dictionary, init=simple_section_content)
    validation = schema_section.validate(section)
    assert not validation
    assert section['sub'].has_option('abc')
    assert section['sub']['abc'] == 10

def test_SchemaSection_validate_unexpected_sub_ignored(dictionary, generic_dictionary, string_io, simple_schema_content, simple_section_content):
    simple_section_content['sub']['ssub'] = {'abc': 10}
    schema_section = SchemaSection(dictionary=generic_dictionary, init=simple_schema_content, unexpected_option_validator=Ignore())
    section = Section(dictionary=dictionary, init=simple_section_content)
    validation = schema_section.validate(section)
    assert not validation
    assert section['sub'].has_section('ssub')
    assert section['sub']['ssub'].has_option('abc')
    assert section['sub']['ssub']['abc'] == 10

def test_SchemaSection_validate_unexpected_removed(dictionary, generic_dictionary, string_io, simple_schema_content, simple_section_content):
    simple_section_content['sub']['abc'] = 10
    schema_section = SchemaSection(dictionary=generic_dictionary, init=simple_schema_content, unexpected_option_validator=Remove())
    section = Section(dictionary=dictionary, init=simple_section_content)
    assert section['sub'].has_option('abc')
    assert section['sub']['abc'] == 10
    validation = schema_section.validate(section)
    assert not validation
    assert not section['sub'].has_option('abc')

def test_SchemaSection_validate_unexpected_sub_removed(dictionary, generic_dictionary, string_io, simple_schema_content, simple_section_content):
    simple_section_content['sub']['ssub'] = {'abc': 10}
    schema_section = SchemaSection(dictionary=generic_dictionary, init=simple_schema_content, unexpected_option_validator=Remove())
    section = Section(dictionary=dictionary, init=simple_section_content)
    assert section['sub'].has_section('ssub')
    assert section['sub']['ssub'].has_option('abc')
    assert section['sub']['ssub']['abc'] == 10
    validation = schema_section.validate(section)
    assert not validation
    assert section['sub'].has_section('ssub')
    assert not section['sub']['ssub'].has_option('abc')
