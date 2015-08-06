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
config.serializer.pickle_serializer
===================================
Implementation of the pickle serializer
"""

__author__ = "Simone Campagna"

import pickle

from .serializer import Serializer


class PickleSerializer(Serializer):
    """PickleSerializer()
       Implementation of pickle serializer.
    """

    @classmethod
    def class_tag(cls):
        return "Pickle"

    @classmethod
    def is_binary(cls):
        return True

    def to_string(self, config):
        content = config.as_dict()
        return pickle.dumps(content)

    def from_string(self, config_class, serialization, *, container=None, prefix='', filename=None):
        dummy = filename
        content = pickle.loads(serialization)
        config = config_class(init=content, container=container, prefix=prefix)
        return config

