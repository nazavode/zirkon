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
config.toolbox.deferred
=======================
The Deferred class implements a deferred evaluation of string
expressions.

The deferred function builds a Deferred instance.
"""

__author__ = "Simone Campagna"
__all__ = [
    'Deferred',
    'deferred',
]

from .unrepr import unrepr
from . import serializer


class Deferred(object):
    """Deferred(expression, *, globals_d=None)
       Deferred evaluation of expression. For instance:
       >>> lst = []
       >>> d = Deferred("10 + len(x)", globals_d={'x': lst, 'len': len})
       >>> lst.extend((1, 2, 3))
       >>> d()
       13
       >>> lst.append(10)
       >>> d()
       14
       >>>
    """

    def __init__(self, expression, *, globals_d=None):
        self.expression = expression
        if globals_d is None:
            globals_d = {}
        else:
            globals_d = globals_d.copy()
        self.globals_d = globals_d

    def __call__(self, globals_d=None):
        gd = self.globals_d.copy()
        if globals_d:
            gd.update(globals_d)
        return unrepr(self.expression, globals_d=gd)

    def __repr__(self):
        if self.globals_d is None:
            g = ""
        else:
            g = ", globals_d={!r}".format(self.globals_d)
        return "{}({!r}{})".format(self.__class__.__name__, self.expression, g)

    def __str__(self):
        return "{}({!r})".format(self.__class__.__name__, self.expression)


def deferred(expression, *, globals_d=None):
    """deferred(expression, *, globals_d=None) -> Deferred instance"""
    return Deferred(expression=expression, globals_d=globals_d)


### Deferred codecs:
json_serializer_module = getattr(serializer, 'json_serializer', None)
if json_serializer_module is not None:
    def _deferred_json_encode(deferred_object):
        """_deferred_json_encode(deferred)
           JSON encoder for Validator instances
        """
        return {'expression': deferred_object.expression,
                'globals_d': deferred_object.globals_d}


    def _deferred_json_decode(deferred_class_name, arguments):
        """_deferred_json_decode(deferred_class_name, arguments)
           JSON decoder for Deferred instances
        """
        assert deferred_class_name == Deferred.__name__
        return Deferred(**arguments)


    json_serializer_module.JSONSerializer.codec_catalog().add_codec(
        class_=Deferred,
        encode=_deferred_json_encode,
        decode=_deferred_json_decode,
    )


text_serializer_module = getattr(serializer, 'text_serializer', None)
if text_serializer_module is not None:
    def _deferred_text_encode(deferred):
        """_deferred_text_encode(deferred)
           ConfigObj/Daikon encoder for Validator instances
        """
        return repr(deferred)


    def _deferred_text_decode(type_name, repr_data):  # pylint: disable=W0613
        """_deferred_text_decode(deferred_name, arguments)
           ConfigObj/Daikon decoder for Validator instances
        """
        return unrepr(repr_data, {'Deferred': Deferred})


    text_serializer_module.TextSerializer.codec_catalog().add_codec(
        class_=Deferred,
        encode=_deferred_text_encode,
        decode=_deferred_text_decode,
    )

