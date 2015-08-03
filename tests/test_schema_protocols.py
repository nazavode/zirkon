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

from common.utils import compare_dicts
from common.schema_fixtures import simple_schema_content
from common.fixtures import tmp_text_file
from common.test_scenarios import pytest_generate_tests

from daikon.schema import Schema

class TestSchemaWithScenarios(object):
    scenarios = [
                 ('JSON', {'protocol': 'JSON'}),
                 ('ConfigObj', {'protocol': 'ConfigObj'}),
                 ('Pickle', {'protocol': 'Pickle'}),
    ]
    def test_Schema_read_write(self, simple_schema_content, tmp_text_file, protocol):
        prefix = 'www.'
        schema = Schema(simple_schema_content, prefix=prefix)
        schema.write(tmp_text_file.name, protocol)
        schema2 = Schema(prefix=prefix)
        schema2.read(tmp_text_file.name, protocol)
        assert compare_dicts(schema, schema2)
