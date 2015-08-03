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
from common.fixtures import simple_content, \
                            tmp_text_file
from common.test_scenarios import pytest_generate_tests

from daikon.config import Config

class TestConfigWithScenarios(object):
    scenarios = [
                 ('JSON', {'protocol': 'JSON'}),
                 ('ConfigObj', {'protocol': 'ConfigObj'}),
                 ('Pickle', {'protocol': 'Pickle'}),
    ]
    def test_Config_read_write(self, simple_content, tmp_text_file, protocol):
        prefix = 'www.'
        config = Config(simple_content, prefix=prefix)
        config.write(tmp_text_file.name, protocol)
        config2 = Config(prefix=prefix)
        config2.read(tmp_text_file.name, protocol)
        assert compare_dicts(config, config2)
