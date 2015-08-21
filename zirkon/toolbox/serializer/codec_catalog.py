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
Catalog for class encoders/decoders.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'CodecCatalog',
]

import collections

from ..catalog import Catalog


class CodecCatalog(Catalog):
    """Catalog for codecs.
    """
    Codec = collections.namedtuple('Codec', ('class_type', 'encode', 'decode'))

    def add_codec(self, class_type, encode, decode):
        """Adds encode/decode information for class_type.

           Parameters
           ----------
           class_type: type
               the class to register
           encode: callable
               the encoding function
           decode: callable
               the decoding function
        """
        self.register(class_type, self.Codec(class_type=class_type, encode=encode, decode=decode))
