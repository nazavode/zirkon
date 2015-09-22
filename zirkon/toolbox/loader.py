# -*- coding: utf-8 -*-
#
# Copyright 2015 Simone Campagna
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
Load objects from modules.
The 'load' function can be used to load generic modules or objects.
For instance, this loads the 'load' function itself:

>>> l = load("zirkon.toolbox.loader:load")
>>> print(l.__name__)
load
>>>

"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'load_module_from_package',
    'load_module',
    'load',
    'LoaderError',
]

import collections
import importlib
import importlib.machinery
import importlib.util
import os
import sys


class LoaderError(Exception):
    """Loader error exception"""
    pass


def load_module_from_package(name, package):
    """Loads a module from the specified package. 'name' can contain dots.

       Parameters
       ----------
       name: str
           the module name
       package: package
           the python package

       Raises
       ------
       LoadError
           cannot load module

       Returns
       -------
       module
           the loaded module
    """
    subpackage_names = name.split('.')
    module = package
    for count, subpackage_name in enumerate(subpackage_names):
        fullname = '{}.{}'.format(module.__name__, subpackage_name)
        spec = importlib.util.find_spec(fullname, package=module.__name__)
        if spec is None:
            if count == len(subpackage_names) - 1:
                what = 'module'
            else:
                what = 'package'
            raise LoaderError('cannot load {} {} from {}'.format(
                what,
                subpackage_name,
                module.__name__))
        module = spec.loader.load_module(fullname)
    return module


def load_module(name, path=None):
    """load_module(name, path=None) -> module
       Load a module given an absolute module name.

       The 'name' parameter has the following format:
       [path/]absolute_module_name
       where 'absolute_module_name' can contain dots.

       If set, the 'path' parameter is a list of directories to be used to search for
       the base package/module.

       Examples:

       Loading a module/package:

       >>> m = load_module('zirkon.toolbox.loader')
       >>> print(m.__name__)
       zirkon.toolbox.loader
       >>> import inspect
       >>> print(inspect.ismodule(m))
       True
       >>>

       Loading a module/package with directory information:

       >>> m = load_module('./zirkon.toolbox.loader')
       >>> print(m.__name__)
       zirkon.toolbox.loader
       >>>

       Loading a module/package from a directory by specifying 'path':

       >>> m = load_module('zirkon.toolbox.loader', path=['.'])


       Parameters
       ----------
       name: str
           the module name [path/]absolute_module_name
       path: str-tuple, optional
           an optional list of directories to be added to the python path

       Raises
       ------
       LoadError
           cannot load package


       Returns
       -------
       module
           the loaded module
"""

    search_locations = []

    def _store_dir(dpath, search_locations):
        """Stores directory for search_locations."""
        dpath = os.path.normpath(os.path.realpath(os.path.abspath(dpath)))
        if dpath not in search_locations:
            search_locations.append(dpath)

    if os.path.sep in name:
        p_dir, module_name = os.path.split(os.path.abspath(name))
        _store_dir(p_dir, search_locations)
    else:
        module_name = name
    if path:
        for dpath in path:
            _store_dir(dpath, search_locations)
    for dpath in sys.path:
        _store_dir(dpath, search_locations)

    path_finder = importlib.machinery.PathFinder()
    plist = module_name.split('.', 1)
    if len(plist) == 1:
        package_name, subpackage_name = plist[0], ''
    else:
        package_name, subpackage_name = plist[0], plist[1]

    spec = path_finder.find_spec(package_name, search_locations)
    if spec is None:
        raise LoaderError('cannot load top-level package {}'.format(
            package_name))
    module = spec.loader.load_module()
    if subpackage_name:
        module = load_module_from_package(name=subpackage_name, package=module)

    return module


def load(name, path=None):
    """load(name, path=None) -> object
       Load an object or module given a fully qualified name.

       The 'name' parameter has the following format:
       [path/]absolute_module_name[:object_name]
       where 'absolute_module_name' can contain dots.

       If 'object_name' is not provided, this function behaves exactly as
       'load_module'.

       >>> mod = load('zirkon.toolbox.loader')
       >>> print(mod.__name__)
       zirkon.toolbox.loader
       >>>

       Otherwise, the module 'absolute_module_name' is loaded,
       and then the object named 'object_name' in it is returned.

       >>> obj = load('zirkon.toolbox.loader:load')
       >>> print(obj.__name__)
       load
       >>>

       If 'object_name' is '*', the function behaves like 'from module import *', and
       a dictionary with the full module content is returned:

       >>> obj_dict = load('zirkon.toolbox.loader:*')
       >>> for obj_name, obj in obj_dict.items():
       ...     print(obj_name)
       load_module_from_package
       load_module
       load
       LoaderError

       If set, the 'path' parameter is a list of directories to be used to search for
       the base package/module, exactly as in 'load_module'.

       Parameters
       ----------
       name: str
           the module or object name, with the form
           [path/]absolute_module_name[:object_name]
       path: str-tuple, optional
           an optional list of directories to be added to the python path

       Raises
       ------
       LoadError
           cannot load object


       Returns
       -------
       object
           the loaded object, or a dictionary if obj_name is '*'
"""
    if ':' in name:
        module_name, obj_name = name.split(':', 1)
    else:
        module_name, obj_name = name, None

    # load module
    module = load_module(module_name, path=path)

    # load object
    if obj_name:
        if obj_name == '*':
            obj_dict = collections.OrderedDict()
            if hasattr(module, '__all__'):
                obj_names = getattr(module, '__all__')
            else:
                obj_names = [oname for oname in dir(module) if not oname.startswith('_')]
            for obj_name in obj_names:
                if not hasattr(module, obj_name):
                    raise LoaderError("cannot load object {} from {}".format(
                        obj_name,
                        module.__name__))
                obj_dict[obj_name] = getattr(module, obj_name)
            return obj_dict
        else:
            if not hasattr(module, obj_name):
                raise LoaderError("cannot load object {} from {}".format(
                    obj_name,
                    module.__name__))
            return getattr(module, obj_name)
    else:
        return module
