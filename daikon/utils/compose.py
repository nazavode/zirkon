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

"""
config.utils.compose
====================
Compose multiple function calls in a single function.
"""

__author__ = "Simone Campagna"
__all__ = [
    'ArgumentStore',
    'Composer',
    'compose',
]

import collections
import inspect


class ArgumentStore(object):
    def __init__(self, arguments=None):
        self._arguments = collections.OrderedDict()
        self._used = {}
        if arguments:
            self.update(arguments)

    def update(self, arguments):
        if arguments:
            self._arguments.update(arguments)
            for argument_name in arguments:
                if not argument_name in self._used:
                    self._used[argument_name] = False

    def __iter__(self):
        for key in self._arguments.keys():
            yield key

    def __contains__(self, key):
        return key in self._arguments

    def set_used(self, argument_name, used=True):
        self._used[argument_name] = used

    def get(self, argument_name):
        self._used[argument_name] = True
        return self._arguments[argument_name]

    def unexpected_arguments(self):
        for argument_name,argument_value in self._arguments.items():
            if not self._used[argument_name]:
                yield argument_name, argument_value

    def items(self):
        yield from self._arguments.items()

    def __eq__(self, argument_store):
        return self._arguments == argument_store._arguments



class Composer(object):
    ParameterInfo = collections.namedtuple('ParameterInfo', ('has_default', ))
    def __init__(self, *functions):
        self._function_info = []
        for function in functions:
            parameters_info = collections.OrderedDict()
            signature = inspect.signature(function)
            parameters = signature.parameters
            for parameter_name, parameter_value in tuple(parameters.items()):
                parameter_default = parameter_value.default
                has_default = parameter_default is not parameter_value.empty
                parameters_info[parameter_name] = self.ParameterInfo(has_default=has_default)
            self._function_info.append((function, parameters_info))

    def __call__(self, **args):
        argument_store = ArgumentStore(args)
        objects = self.partial(argument_store)
        self.verify_argument_store(argument_store)
        return objects

    @classmethod
    def verify_argument_store(cls, argument_store):
        unexpected_arguments = sorted(list(argument_store.unexpected_arguments()), key=lambda x: x[0])
        if unexpected_arguments:
            raise TypeError("unexpected arguments: {}".format(
                ', '.join("{}={!r}".format(argument_name, argument_value) for argument_name, argument_value in unexpected_arguments),
            ))

    def partial(self, argument_store, prefix=''):
        objects = []
        for function, parameters_info in self._function_info:
            parameters = collections.OrderedDict()
            for parameter_name, parameter_info in parameters_info.items():
                argument_name = prefix + parameter_name
                print(function, repr(parameter_name), repr(prefix), repr(argument_name))
                if argument_name in argument_store:
                    parameter_value = argument_store.get(argument_name)
                    parameters[parameter_name] = parameter_value
                else:
                    if not parameter_info.has_default:
                        raise TypeError("{}: missing required argument {}".format(function.__name__, parameter_name))
            objects.append(function(**parameters))
        return objects

def compose(*functions):
    return Composer(*functions)
