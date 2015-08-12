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
from .deferred_expression import DEBase
from . import serializer
from .subclass import find_subclass


class Deferred(object):  # pylint: disable=R0903
    """Deferred(expression, globals_d=None)
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

    def __init__(self, expression, globals_d=None):
        if isinstance(expression, DEBase):
            expression = expression.expression()
        self.expression = expression
        if globals_d is None:
            globals_d = {}
        else:
            globals_d = globals_d.copy()
        self.globals_d = globals_d

    def __call__(self, globals_d=None):
        gdct = self.globals_d.copy()
        if globals_d:
            gdct.update(globals_d)
        return unrepr(self.expression, globals_d=gdct)

    def __repr__(self):
        if self.globals_d is None:
            gtext = ""
        else:
            gtext = ", globals_d={!r}".format(self.globals_d)
        return "{}({!r}{})".format(self.__class__.__name__, self.expression, gtext)

    def __str__(self):
        return "{}({!r})".format(self.__class__.__name__, self.expression)


def deferred(expression, globals_d=None):
    """deferred(expression, globals_d=None) -> Deferred instance"""
    return Deferred(expression=expression, globals_d=globals_d)


# Deferred codecs:
def _setup_codecs():
    """_setup_codecs()
       Setup codecs for validators.
    """
    _json_serializer_module = getattr(serializer, 'json_serializer', None)
    if _json_serializer_module is not None:
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
            deferred_class = find_subclass(Deferred, deferred_class_name, include_self=True)
            if deferred_class is None:
                raise NameError("undefined Deferred class {}".format(deferred_class_name))
            return deferred_class(**arguments)

        _json_serializer_module.JSONSerializer.codec_catalog().add_codec(
            class_=Deferred,
            encode=_deferred_json_encode,
            decode=_deferred_json_decode,
        )

    _text_serializer_module = getattr(serializer, 'text_serializer', None)
    if _text_serializer_module is not None:
        def _deferred_text_encode(deferred_object):
            """_deferred_text_encode(deferred)
               ConfigObj/Daikon encoder for Validator instances
            """
            return repr(deferred_object)

        def _deferred_text_decode(type_name, repr_data):  # pylint: disable=W0613
            """_deferred_text_decode(deferred_name, arguments)
               ConfigObj/Daikon decoder for Validator instances
            """
            return unrepr(repr_data, {'Deferred': Deferred})

        _text_serializer_module.TextSerializer.codec_catalog().add_codec(
            class_=Deferred,
            encode=_deferred_text_encode,
            decode=_deferred_text_decode,
        )

_setup_codecs()
