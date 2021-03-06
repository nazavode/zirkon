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
Implementation of the 'json' Serializer.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'JSONSerializer',
]

import collections
import json

from .serializer import Serializer
from .codec_catalog import CodecCatalog


_CODEC_CATALOG = CodecCatalog()
_CLASS_NAME_KEY = "__class_name__"


class JSONPluggableEncoder(json.JSONEncoder):
    """Implementation of JSON Pluggable encoder.
    """

    def default(self, obj):  # pylint: disable=method-hidden
        class_ = type(obj)
        codec = _CODEC_CATALOG.get_by_class(class_)
        if codec is None:
            return super().default(obj)
        else:
            dct = collections.OrderedDict()
            dct[_CLASS_NAME_KEY] = class_.__name__
            dct.update(codec.encode(obj))
            return dct


def _object_pairs_hook(pairs):
    """Hook to manage a list of pairs (a dict serialization).

       Parameters
       ----------
       pairs: list
           a list of pais

       Returns
       -------
       dict
           encoded dictionary
    """

    dct = collections.OrderedDict(pairs)
    if _CLASS_NAME_KEY in dct:
        class_tag = dct[_CLASS_NAME_KEY]
        codec = _CODEC_CATALOG.get_by_name(class_tag)
        del dct[_CLASS_NAME_KEY]
        return codec.decode(class_tag, dct)
    else:
        return dct


class JSONSerializer(Serializer):
    """Implementation of JSON serializer.
    """
    CODEC_CATALOG = _CODEC_CATALOG

    @classmethod
    def class_tag(cls):
        return "json"

    def to_string(self, obj):
        return json.dumps(obj, cls=JSONPluggableEncoder, indent=4) + '\n'

    def from_string(self, serialization, *, filename=None):
        dummy = filename
        decoder = json.JSONDecoder(object_pairs_hook=_object_pairs_hook)
        return decoder.decode(serialization)

