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

from common.fixtures import protocol, \
    simple_config_content, simple_schema_content, \
    simple_section_content, simple_validation, tmp_text_file

from daikon.config import Config
from daikon.schema import Schema
from daikon.validation import Validation
from daikon.toolbox.dictutils import compare_dicts, transform
from daikon.toolbox.serializer import Serializer

Parameters = collections.namedtuple('Parameters', ('config_class', 'config_content'))

validation = simple_validation(
    simple_schema_content=simple_schema_content(),
    simple_section_content=simple_section_content(),
)

_config_parameters = [
    Parameters(config_class=Config, config_content=simple_config_content()),
    Parameters(config_class=Schema, config_content=simple_schema_content()),
    Parameters(config_class=Validation, config_content=validation),
]
@pytest.fixture(params=_config_parameters, ids=[c.config_class.__name__ for c in _config_parameters])
def parameters(request):
    return request.param

def test_read_write(protocol, parameters, tmp_text_file):
    config_class = parameters.config_class
    config_content = parameters.config_content
    cs = config_class(config_content)

    print(":::", config_class)
    cs.dump()

    cs.write(tmp_text_file.name, protocol)
    cs2 = config_class()
    cs2.read(tmp_text_file.name, protocol)

    print("::: reloaded:")
    cs2.dump()

    if config_class == Validation:
        tcs = transform(cs, value_transform=str, dict_factory=dict)
        tcs2 = transform(cs2, value_transform=str, dict_factory=dict)
        print("===", type(tcs), type(tcs2))
        assert tcs == tcs2
    else:
        assert compare_dicts(cs, cs2)
