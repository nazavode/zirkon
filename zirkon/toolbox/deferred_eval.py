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
The DeferredEval class implements a deferred evaluation of string
expressions.

The deferred_eval function builds a DeferredEval instance.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'DeferredEval',
    'deferred_eval',
]

from .unrepr import unrepr
from . import serializer
from .subclass import find_subclass


class DeferredEval(object):  # pylint: disable=R0903
    """Defers evaluation of expression. For instance:

       >>> lst = []
       >>> d = DeferredEval("10 + len(x)", globals_d={'x': lst, 'len': len})
       >>> lst.extend((1, 2, 3))
       >>> d()
       13
       >>> lst.append(10)
       >>> d()
       14
       >>>

       Parameters
       ----------
       expression: str
           the expression to be evaluated
       globals_d: dict, optional
           the globals dictionary for name lookup

    """

    def __init__(self, expression, globals_d=None):
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


def deferred_eval(expression, globals_d=None):
    """Returns a DeferredEval object.

       Parameters
       ----------
       expression: str
           the expression to be evaluated
       globals_d: dict, optional
           the globals dictionary for name lookup
    """
    return DeferredEval(expression=expression, globals_d=globals_d)


# DeferredEval codecs:
def _setup_codecs():  # pragma: no cover
    """Setup codecs for validators.
    """
    _json_serializer_module = getattr(serializer, 'json_serializer', None)
    if _json_serializer_module is not None:
        def _deferred_json_encode(deferred_object):
            """Encodes DeferredEval objects for json serializer.

               Parameters
               ----------
               deferred_object: DeferredEval
                   the object to be encoded

               Returns
               -------
               dict
                   the encoded dictionary
            """
            return {'expression': deferred_object.expression,
                    'globals_d': deferred_object.globals_d}

        def _deferred_json_decode(deferred_class_name, arguments):
            """Decodes DeferredEvan object from json serializer.

               Parameters
               ----------
               deferred_class_name: str
                   the name of the class
               arguments: dict
                   the arguments dict

               Raises
               -------
               NameError
                   class not found

               Returns
               -------
               DeferredEval
                   the decoded object
            """
            deferred_class = find_subclass(DeferredEval, deferred_class_name, include_self=True)
            if deferred_class is None:
                raise NameError("undefined DeferredEval class {}".format(deferred_class_name))
            return deferred_class(**arguments)

        _json_serializer_module.JSONSerializer.codec_catalog().add_codec(
            class_type=DeferredEval,
            encode=_deferred_json_encode,
            decode=_deferred_json_decode,
        )

    _text_serializer_module = getattr(serializer, 'text_serializer', None)
    if _text_serializer_module is not None:
        def _deferred_text_encode(deferred_object):
            """Encodes DeferredEval object for configobj/zirkon serializers.

               Parameters
               ----------
               deferred_object: DeferredEval
                   the object to be encoded

               Returns
               -------
               str
                   the representation of the object
            """
            return repr(deferred_object)

        def _deferred_text_decode(type_name, repr_data):  # pylint: disable=W0613
            """Decodes DeferredEval objects from configobj/zirkon serializers.

               Parameters
               ----------
               deferred_class_name: str
                   the name of the class
               repr: str
                   the object representation

               Returns
               -------
               DeferredEval
                   the decoded object
            """
            return unrepr(repr_data, {'DeferredEval': DeferredEval})

        _text_serializer_module.TextSerializer.codec_catalog().add_codec(
            class_type=DeferredEval,
            encode=_deferred_text_encode,
            decode=_deferred_text_decode,
        )

_setup_codecs()  # pragma: no cover
