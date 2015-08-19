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

from zirkon.config import Config, ROOT, SECTION
from zirkon.defaults_section import DefaultsSection

@pytest.fixture
def defaults_section():
    defaults = DefaultsSection()
    defaults['x'] = ROOT['n'] + 10
    defaults['sub'] = {}
    defaults['sub']['x'] = ROOT['n'] * 2 + SECTION['y']
    defaults['sub']['y'] = 10000
    defaults['sub']['sub'] = {}
    defaults['sub']['sub']['x'] = ROOT['n'] * 5
    return defaults

def test_DefaultsSection0(defaults_section):
    config = Config()
    config['n'] = 4
    with defaults_section.referencing(config):
        defaults_section.dump()
        assert defaults_section['x'] == 14
        with pytest.raises(KeyError) as exc_info:
            assert defaults_section['sub']['x'] == 10008
        assert str(exc_info.value) == "'sub'"
        assert defaults_section['sub']['sub']['x'] == 20

def test_DefaultsSection1(defaults_section):
    config = Config()
    config['n'] = 5
    config['sub'] = {'y': 100}
    with defaults_section.referencing(config):
        assert defaults_section['x'] == 15
        assert defaults_section['sub']['x'] == 110
        assert defaults_section['sub']['sub']['x'] == 25
