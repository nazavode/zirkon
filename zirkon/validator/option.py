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
Implementation of the Option class. It is used to store information about an option:
the name, the value, and if it is defined.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'Option',
]


class Option(object):
    """Stores option information: the option name, the value and if it has been defined.

       Parameters
       ----------
       name: str
           the option name
       value: any
           the option value

       Attributes
       ----------
       name: str
           the option name
       value: any
           the option value
       defined: bool
           True if option is defined in config
    """
    def __init__(self, name, value, *, defined=True):
        self.name = name
        self.value = value
        self.defined = defined

    def is_defined(self):
        """Returns defined attribute.

           Returns
           -------
           bool
               the 'defined' attribute
        """
        return self.defined

    def copy(self):
        """Returns a copy of the Option object.

           Returns
           -------
           Option
               the copy
        """
        return self.__class__(name=self.name, value=self.value, defined=self.defined)

    def __repr__(self):
        if self.defined:
            dstring = ""
        else:
            dstring = ", defined=False"
        return "{}({!r}, {!r}{})".format(
            self.__class__.__name__,
            self.name,
            self.value,
            dstring)

    def __str__(self):
        if self.defined:
            vstring = "={!r}".format(self.value)
        else:
            vstring = ""
        return "{}{}".format(self.name, vstring)

