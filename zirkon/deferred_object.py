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
Definition of the deferred objects used by zirkon (ROOT and SECTION).
"""

__author__ = "Simone Campagna"
__all__ = [
    'SECTION',
    'ROOT',
]


from .toolbox.deferred import DName


class DProperty(DName):
    """DProperty - call 'name' as a function without arguments
       >>> dprop = DProperty('foo')
       >>> foo_function = lambda: 123
       >>> dprop.evaluate({'foo': foo_function})
       123
       >>> dprop.unparse()
       'foo'

    """
    def evaluate(self, globals_d=None):
        return super().evaluate(globals_d=globals_d)()


SECTION = DProperty('SECTION')
ROOT = DName('ROOT')
