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
Compose multiple function calls in a single function.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'ArgumentStore',
    'Composer',
    'compose',
]

import collections
import inspect


class ArgumentStore(object):
    """Dict-like object to store arguments and track their usage.

       Parameters
       ----------
       arguments: dict, optional
           arguments
    """

    def __init__(self, arguments=None):
        self._arguments = {}
        self._used = {}
        if arguments:
            self.update(arguments)

    def update(self, arguments):
        """Updates with new arguments.

           Parameters
           ----------
           arguments: dict
               the arguments
        """
        if arguments:
            self._arguments.update(arguments)
            for argument_name in arguments:
                if argument_name not in self._used:
                    self._used[argument_name] = False

    def __iter__(self):
        for key in self._arguments.keys():
            yield key

    def __contains__(self, key):
        return key in self._arguments

    def get_used(self, argument_name):
        """Returns True if the argument has been used.

           Parameters
           ----------
           argument_name: str
               the name of the argument

           Returns
           -------
           bool
               True if the argument has been used
        """
        return self._used[argument_name]

    def set_used(self, argument_name, used=True):
        """Sets 'used' status for 'argument_name'.

           Parameters
           ----------
           argument_name: str
               the name of the argument
           used: bool, optional
               the usage status
        """
        self._used[argument_name] = used

    def get(self, argument_name):
        """Returns argument value and tracks usage.

           Parameters
           ----------
           argument_name: str
               the name of the argument

           Returns
           -------
           |any|
               the argument value
        """
        self._used[argument_name] = True
        return self._arguments[argument_name]

    def unused_arguments(self):
        """Iterates over unused arguments.

           Returns
           -------
           iterator
               iterator over unused argument names and values
        """
        for argument_name, argument_value in self._arguments.items():
            if not self._used[argument_name]:
                yield argument_name, argument_value

    def items(self):
        """items()
           Iterates over arguments items().

           Returns
           -------
           iterator
               iterator over argument names and values
        """
        yield from self._arguments.items()

    def arguments(self):
        """Returns the internal _arguments dict.

           Returns
           -------
           dict
               the internal argument dictionary
        """
        return self._arguments

    def __eq__(self, argument_store):
        if isinstance(argument_store, ArgumentStore):
            return self._arguments == argument_store.arguments()
        else:
            return self._arguments == argument_store

    def split(self, prefix):
        """Returns a new ArgumentStore containing arguments starting with 'prefix'.

           Parameters
           ----------
           prefix: str
               a prefix for keys

           Returns
           -------
           ArgumentStore
               a new argument store
        """
        sub_arguments = {}
        for argument_name, argument_value in self._arguments.items():
            if argument_name.startswith(prefix):
                sub_argument_name = argument_name[len(prefix):]
                sub_arguments[sub_argument_name] = argument_value
        return self.__class__(sub_arguments)

    def merge(self, argument_store, prefix):
        """Merges an ArgumentStore obtained with split(prefix).

           Parameters
           ----------
           argument_store: ArgumentStore
               the argument store to be merged
           prefix: str
               the prefix used for argument_store
        """
        for sub_argument_name in argument_store.arguments():
            if argument_store.get_used(sub_argument_name):
                argument_name = prefix + sub_argument_name
                self._used[argument_name] = True

    def __repr__(self):
        vstring = ", ".join("{}={!r}[{}]".format(n, v, self._used[n]) for n, v in self._arguments.items())
        return "{}({})".format(self.__class__.__name__, vstring)


class Composer(object):
    r"""Composes multiple function calls into a single call. Given a list of functions,
         returns a callable object whose __call__ method merges all the function's arguments.
         For instance:

         >>> class Alpha(object):
         ...     def __init__(self, x, y):
         ...         self.x, self.y = x, y
         ...     def __repr__(self):
         ...         return "Alpha(x={}, y={})".format(self.x, self.y)
         >>> def f_abc(b, c, a=100):
         ...     return a + b + c
         >>> def f_bxd(b, x, d):
         ...     return [b, x, d]
         >>> composer = Composer(Alpha, f_abc, f_bxd)
         >>> actual_arguments, objects = composer(b=10, y=2, d=30, x=1, c=20)
         >>> actual_arguments
         OrderedDict([('x', 1), ('y', 2), ('b', 10), ('c', 20), ('d', 30)])
         >>> objects
         [Alpha(x=1, y=2), 130, [10, 1, 30]]
         >>>

         Parameters
         ----------
         \*functions: tuple
             tuple of callable objects
    """
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
        actual_arguments, objects = self.partial(argument_store)
        self.verify_argument_store(argument_store)
        return actual_arguments, objects

    @classmethod
    def verify_argument_store(cls, argument_store):
        """Raises a TypeError in case of unused arguments.

           Raises
           ------
           TypeError
               unexpected arguments

           Parameters
           ----------
           argument_store: ArgumentStore
               the argument store to be verified
        """
        unused_arguments = sorted(list(argument_store.unused_arguments()), key=lambda x: x[0])
        if unused_arguments:
            raise TypeError("unexpected arguments: {}".format(
                ', '.join("{}={!r}".format(a_name, a_value) for a_name, a_value in unused_arguments),
            ))

    def partial(self, argument_store, prefix=''):
        """Partial binding from argument_store with prefix.
           If prefix is given, only arguments starting with prefix are selected,
           and copied to the functions' arguments without prefix.

           Parameters
           ----------
           argument_store: ArgumentStore
               the argument store
           prefix: str, optional
               an optional key prefix

           Raises
           ------
           TypeError
               missing required argument

           Returns
           -------
           tuple
               a tuple containing the actual arguments dict and the results list
        """
        actual_arguments = collections.OrderedDict()
        objects = []
        for function, parameters_info in self._function_info:
            parameters = collections.OrderedDict()
            for parameter_name, parameter_info in parameters_info.items():
                argument_name = prefix + parameter_name
                if argument_name in argument_store:
                    parameter_value = argument_store.get(argument_name)
                    parameters[parameter_name] = parameter_value
                    actual_arguments[argument_name] = parameter_value
                else:
                    if not parameter_info.has_default:
                        raise TypeError("{}: missing required argument {}".format(function.__name__, parameter_name))
            objects.append(function(**parameters))
        return actual_arguments, objects


def compose(*functions):
    r"""Returns a Composer for the given functions.

        Parameters
        ----------
        \*functions: tuple
            tuple of callable objects

        Returns
        -------
        Composer
            the composer object
    """
    return Composer(*functions)
