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
config.validator.option_store
=============================
Implementation of the OptionStore class
"""

__author__ = "Simone Campagna"
__all__ = [
    'OptionStore',
]


class OptionStore(object):
    def __init__(self, options=None):
        self._options = {}
        self._used = {}
        if options:
            self.update(options)

    def update(self, options):
        if options:
            self._options.update(options)
            for option_name in options:
                if not option_name in self._used:
                    self._used[option_name] = False

    def __iter__(self):
        for key in self._options.keys():
            yield key

    def get(self, option_name):
        self._used[option_name] = True
        return self._options[option_name]

    def invalid(self):
        for option_name in self._options:
            if not self._used[option_name]:
                yield option_name

    def items(self):
        yield from self._options.items()

    def __eq__(self, option_store):
        return self._options == option_store._options
