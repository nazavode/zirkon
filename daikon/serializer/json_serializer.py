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


_JSON_CODERS = {}
_CLASS_NAME_KEY = '__class_name__'

Coder = collections.namedtuple('Coder', ('class_', 'encode', 'decode'))

def class_mapper(class_):
    return class_.__name__

def add_coder(class_, encode, decode, *, class_name=None):
    if class_name is None:
        class_name = class_mapper(class_)
    _JSON_CODERS[class_name] = Coder(class_=class_, encode=encode, decode=decode)

class JSONPluggableEncoder(json.JSONEncoder):
    """JSONPluggableEncoder()
       Implementation of JSON Pluggable encoder.
    """
    def default(self, obj):
        for class_name, coder in _JSON_CODERS.items():
            if isinstance(obj, coder.class_):
                dct = collections.OrderedDict()
                dct[_CLASS_NAME_KEY] = class_name
                dct.update(coder.encode(obj))
                return dct
        else:
            super().default(obj)

def _object_pairs_hook(pairs):
    dct = collections.OrderedDict(pairs)
    if _CLASS_NAME_KEY in dct:
        class_name = dct[_CLASS_NAME_KEY]
        coder = _JSON_CODERS[class_name]
        del dct[_CLASS_NAME_KEY]
        return coder.decode(dct)
    else:
        return dct

class JSONSerializer(Serializer):
    """JSONSerializer()
       Implementation of JSON serializer.
    """

    @classmethod
    def plugin_name(cls):
        return "JSON"

    def to_string(self, config):
        content = config.as_dict()
        return json.dumps(content, cls=JSONPluggableEncoder, indent=4) + '\n'

    def from_string(self, config_class, serialization, *, container=None):
        decode = json.JSONDecoder(object_pairs_hook=_object_pairs_hook)
        content = decode.decode(serialization)
        print("JSON:", config_class, content)
        config = config_class(init=content, container=container)
        return config

