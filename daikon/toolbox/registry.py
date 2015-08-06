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
config.toolbox.registry
=======================
Implementation of a Registry base class
"""

__author__ = "Simone Campagna"

import collections
import inspect

from . import subclass


class Registry(object):
    """Registry
       Abstract base class for registry classes
       >>> class MyRegistry(Registry):
       ...     pass
       >>> print([cls.__name__ for cls in MyRegistry.classes()])
       []
       >>> class Alpha(MyRegistry):
       ...     pass
       >>> print([cls.__name__ for cls in MyRegistry.classes()])
       ['Alpha']
       >>> registered_class = MyRegistry.get_class('Alpha')
       >>> registered_class.__name__
       'Alpha'
       >>>
    """

    @classmethod
    def is_abstract(cls):
        """is_abstract() -> boolean
           Return True if this is an "abstract" registry.
        """
        return inspect.isabstract(cls)

    @classmethod
    def class_tag(cls):
        """class_tag() -> str
           Return the class tag (by default cls.__name__, but it can be overwritten).
        """
        return cls.__name__

    @classmethod
    def classes(cls, *, include_self=False, include_abstract=False):
        """classes(*, include_self=False, include_abstract=False) -> iterator
           Iterator over classes; cls is included only if 'include_self' is True.
           Abstract classes are included only if 'include_abstract' is True.
        """
        if include_abstract:
            filter = None
        else:
            filter = lambda x: not x.is_abstract()
        return subclass.subclasses(cls, include_self=include_self, filter=filter)

    @classmethod
    def class_dict(cls, *, include_self=False, include_abstract=False):
        """class_dict(*, include_self=False, include_abstract=False) -> dict
           Return a dictionary class_tag -> registered_class
        """
        dct = collections.OrderedDict()
        for registered_class in cls.classes(include_self=include_self, include_abstract=include_abstract):
            dct[registered_class.class_tag()] = registered_class
        return dct

    @classmethod
    def get_class(cls, class_tag, default=None, *, include_self=False, include_abstract=False):
        """get_class(class_tag, default=None, *, include_self=False, include_abstract=False) -> class or None
           Return the registered class whose tag is 'class_tag', or 'default'.
        """
        return cls.class_dict(include_self=include_self,
                                   include_abstract=include_abstract).get(class_tag, default)

    @classmethod
    def get_class_tags(cls, *, include_self=False, include_abstract=False):
        """get_class_tags(*, include_self=False, include_abstract=False) -> class tags iterator
           Iterator over class tags.
        """
        for class_tag in cls.class_dict(include_self=include_self,
                                               include_abstract=include_abstract):
            yield class_tag
