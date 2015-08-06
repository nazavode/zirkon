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
config.toolbox.plugin
=====================
Implementation of a Plugin base class
"""

__author__ = "Simone Campagna"

import collections
import inspect

from . import subclass


class Plugin(object):
    """Plugin
       Abstract base class for plugin classes
       >>> class MyPlugin(Plugin):
       ...     pass
       >>> print([cls.__name__ for cls in MyPlugin.subclasses()])
       []
       >>> class Alpha(MyPlugin):
       ...     pass
       >>> print([cls.__name__ for cls in MyPlugin.subclasses()])
       ['Alpha']
       >>> plugin_class = MyPlugin.get_plugin('Alpha')
       >>> plugin_class.__name__
       'Alpha'
       >>>
    """

    @classmethod
    def is_abstract(cls):
        """is_abstract() -> boolean
           Return True if this is an "abstract" plugin.
        """
        return inspect.isabstract(cls)

    @classmethod
    def plugin_name(cls):
        """plugin_name() -> str
           Return the plugin name.
        """
        return cls.__name__

    @classmethod
    def subclasses(cls, *, include_self=False, include_abstract=False):
        """subclasses(*, include_self=False, include_abstract=False) -> iterator
           Iterator over subclasses; cls is included only if 'include_self' is True.
           Abstract plugin classes are included only if 'include_abstract' is True.
        """
        if include_abstract:
            filter = None
        else:
            filter = lambda x: not x.is_abstract()
        return subclass.subclasses(cls, include_self=include_self, filter=filter)

    @classmethod
    def subclasses_dict(cls, *, include_self=False, include_abstract=False):
        """subclasses_dict(*, include_self=False, include_abstract=False) -> dict
           Return a dictionary plugin_name -> plugin_class
        """
        dct = collections.OrderedDict()
        for plugin_class in cls.subclasses(include_self=include_self, include_abstract=include_abstract):
            dct[plugin_class.plugin_name()] = plugin_class
        return dct

    @classmethod
    def get_plugin(cls, plugin_name, default=None, *, include_self=False, include_abstract=False):
        """get_plugin(plugin_name, default=None, *, include_self=False, include_abstract=False) -> plugin or None
           Return the plugin_class whose name is 'plugin_name', or 'default'.
        """
        return cls.subclasses_dict(include_self=include_self,
                                   include_abstract=include_abstract).get(plugin_name, default)

    @classmethod
    def get_plugin_names(cls, *, include_self=False, include_abstract=False):
        """get_plugin_names(*, include_self=False, include_abstract=False) -> plugin names iterator
           Iterator over plugin names.
        """
        for plugin_name in cls.subclasses_dict(include_self=include_self,
                                               include_abstract=include_abstract):
            yield plugin_name
