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

"""\
config.serializer.json_serializer
=================================
Implementation of the JSON Serializer
"""

__author__ = "Simone Campagna"

import collections
import json

from .serializer import Serializer


class JSONSerializer(Serializer):
    """JSONSerializer()
       Implementation of JSON serializer.
    """

    @classmethod
    def plugin_name(cls):
        return "JSON"

    def to_string(self, config):
        content = config.as_dict()
        return json.dumps(content, indent=4) + '\n'

    def from_string(self, config_class, serialization, *, container=None):
        decoder = json.JSONDecoder(object_pairs_hook=collections.OrderedDict)
        content = decoder.decode(serialization)
        config = config_class(init=content, container=container)
        return config

