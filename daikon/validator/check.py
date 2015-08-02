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
config.validator.check
======================
Implementation of the Check base class
"""

__author__ = "Simone Campagna"
__all__ = [
    'CheckMeta',
    'Check',
]

import abc
import collections
import inspect

from .key_value import KeyValue


class CheckMeta(abc.ABCMeta):
    """CheckMeta()
    """

    ParameterInfo = collections.namedtuple('ParameterInfo', ('has_default', ))
    def __new__(mcls, class_name, class_bases, class_dict):
        cls = super().__new__(mcls, class_name, class_bases, class_dict)
        init_method = getattr(cls, '__init__', None)
        parameters_info = collections.OrderedDict()
        if init_method is not None:
           signature = inspect.signature(cls.__init__)
           parameters = signature.parameters
           for parameter_name, parameter_value in tuple(parameters.items())[1:]:
               parameter_default = parameter_value.default
               has_default = parameter_default is not parameter_value.empty
               parameters_info[parameter_name] = mcls.ParameterInfo(has_default=has_default)
        cls.PARAMETERS_INFO = parameters_info
        return cls
    
class Check(metaclass=CheckMeta):
    """Check()
       Abstract base class for cheks. Checks must implement
       check(key_value) method.
    """

    def __init__(self):
        pass

    def do_check(self, key_value, mode=None):
        if mode == 'load':
            self.on_load(key_value)
        self.check(key_value)
        if mode == 'store':
            self.on_store(key_value)

    @abc.abstractmethod
    def check(self, key_value):
        pass

    def on_load(self, key_value):
        pass

    def on_store(self, key_value):
        pass

    def auto_validate(self, validator):
        pass
