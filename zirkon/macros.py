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
Definition of the macro objects used by zirkon (ROOT and SECTION).
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'SECTION',
    'ROOT',
]


from .toolbox.macro import MName


class MNameCall(MName):
    """Macro for name lookup and function call: MNameCall('foo') evaluates to 'foo()'.

       >>> dprop = MNameCall('foo')
       >>> foo_function = lambda: 123
       >>> dprop.evaluate({'foo': foo_function})
       123
       >>> dprop.unparse()
       'foo'

       Parameters
       ----------
       name: str
           the name of the function
       globals_d: dict, optional
           the globals dictionary

       Attributes
       ----------
       name: str
           the name of the function
       globals_d: dict, optional
           the globals dictionary

    """
    def evaluate(self, globals_d=None):
        return super().evaluate(globals_d=globals_d)()


SECTION = MNameCall('SECTION')
ROOT = MName('ROOT')
