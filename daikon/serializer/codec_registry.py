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
config.serializer.codec_registry
================================
Registry for class encoders/decoders.
"""

__author__ = "Simone Campagna"
__all__ = [
    'CodecRegistry',
]

import collections

from ..utils.class_registry import ClassRegistry


class CodecRegistry(ClassRegistry):
    """CodecRegistry(default)
       ClassRegistry for codecs.
    """
    Codec = collections.namedtuple('Codec', ('class_', 'encode', 'decode'))

    def add_codec(self, class_, encode, decode):
        self.register(class_, self.Codec(class_=class_, encode=encode, decode=decode))
