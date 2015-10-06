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
Implementation of a Registry base class, providing methods to find
subclasses by name.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'Registry',
]

import collections
import inspect

from . import subclass


class Registry(object):
    """Abstract base class for registry classes. A registry class provides easy
       access to its subclasses. Each subclass is tagged by a class_tag, usually
       the class name, which can be used to retrieve it.

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
        """Returns True if this is an "abstract" registry. By default, a class
           is considered abstract in the usual way (inspect.isabstract(...)
           returns True), but this method can be overwritten to define a different
           behavior.

           Returns
           -------
           bool
               True if class is "abstract"
        """
        return inspect.isabstract(cls)

    @classmethod
    def class_tag(cls):
        """Returns the class tag (by default cls.__name__, but it can be overwritten).

           Returns
           -------
           str
               the class tag (usually, but not necessarily, a string)
        """
        return cls.__name__

    @classmethod
    def classes(cls, *, include_self=False, include_abstract=False):
        """Iterates over classes; cls is included only if 'include_self' is True.

           Parameters
           ----------
           include_self: bool, optional
               if True, includes the calling class cls itself
           include_abstract: bool, optional
               if True, includes also "abstract" classes

           Returns
           -------
           iterator
               iterator over subclasses
        """
        if include_abstract:
            filter = None  # pylint: disable=redefined-builtin
        else:
            filter = lambda x: not x.is_abstract()  # pylint: disable=redefined-builtin
        return subclass.subclasses(cls, include_self=include_self, filter=filter)

    @classmethod
    def class_dict(cls, *, include_self=False, include_abstract=False):
        """Returns a dictionary class_tag -> registered_class.

           Parameters
           ----------
           include_self: bool, optional
               if True, includes the calling class cls itself
           include_abstract: bool, optional
               if True, includes also "abstract" classes

           Returns
           -------
           dict
               class-by-tag dictionary
        """
        dct = collections.OrderedDict()
        for registered_class in cls.classes(include_self=include_self, include_abstract=include_abstract):
            dct[registered_class.class_tag()] = registered_class
        return dct

    @classmethod
    def get_class(cls, class_tag, default=None, *, include_self=False, include_abstract=False):
        """Returns the registered class whose tag is 'class_tag', or 'default'.

           Parameters
           ----------
           class_tag: str
               the class tag
           default: type, optional
               the default value if no match is found
           include_self: bool, optional
               if True, includes the calling class cls itself
           include_abstract: bool, optional
               if True, includes also "abstract" classes

           Returns
           -------
           class
               the found class, or default
        """
        return cls.class_dict(include_self=include_self,
                              include_abstract=include_abstract).get(class_tag, default)

    @classmethod
    def get_class_tags(cls, *, include_self=False, include_abstract=False):
        """Iterates over class tags.

           Parameters
           ----------
           include_self: bool, optional
               if True, includes the calling class cls itself
           include_abstract: bool, optional
               if True, includes also "abstract" classes

           Yields
           ------
           str
               the found class tags
        """
        for class_tag in cls.class_dict(include_self=include_self,
                                        include_abstract=include_abstract):
            yield class_tag
