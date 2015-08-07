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

from common.fixtures import string_io

from daikon.toolbox.flatmap import FlatMap
from daikon.section import Section

@pytest.fixture
def content():
    return collections.OrderedDict([
        ('a', 10),
        ('b', 20),
        ('sub', collections.OrderedDict([
            ('x', 1.0),
            ('y', collections.OrderedDict([
                ('ystart', -0.5),
                ('ystop', +0.5),
                ('ystep', +0.1),
            ])),
            ('z', 3.0),
        ])),
        ('c', 30),
    ])

SECTION_DUMP = """\
a = 10
b = 20
[sub]
    x = 1.0
    [y]
        ystart = -0.5
        ystop = 0.5
        ystep = 0.1
    z = 3.0
c = 30
"""

def test_Section_create(content, string_io):
    section = Section(dictionary=FlatMap(), init=content)
    section.dump(stream=string_io)
    assert string_io.getvalue() == SECTION_DUMP

def test_Section_2(content):
    section = Section(dictionary=FlatMap(), init=content)
    section2 = Section(dictionary=FlatMap(), init=content)
    s_io = string_io()
    section.dump(stream=s_io)
    assert s_io.getvalue() == SECTION_DUMP
    section['sub']['y']['yfilename'] = 'y.dat'
    s_io1 = string_io()
    section.dump(stream=s_io1)
    assert s_io1.getvalue() != SECTION_DUMP
    s_io2 = string_io()
    section2.dump(stream=s_io2)
    assert s_io2.getvalue() == SECTION_DUMP

