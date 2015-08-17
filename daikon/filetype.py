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
toolbox.filetype
================
Utility function for guessing file type.
"""

__author__ = "Simone Campagna"
__all__ = [
    'FileType',
    'guess',
    'standard_filepath',
    'classify',
    'search_paths',
    'discover',
    'search_rootname',
    'search_filetype',
    'get_config_class',
    'get_config_class_name',
    'get_config_classes',
    'get_protocols',
]

import collections
import fnmatch
import glob
import os

from .toolbox.serializer import Serializer
from .config_base import ConfigBase
from .config import Config
from .schema import Schema
from .validation import Validation


FileType = collections.namedtuple('FileType', ('filepath', 'protocol', 'config_class'))

_CONFIG_CLASSES = (
    Config,
    Schema,
    Validation,
)

_TEMPLATES = {
    Config: ('{rootname}.{protocol}', '{rootname}.{protocol}-config', '{rootname}.c-{protocol}'),
    Schema: ('{rootname}.{protocol}-schema', '{rootname}.s-{protocol}'),
    Validation: ('{rootname}.{protocol}-validation', '{rootname}.v-{protocol}'),
}


def get_config_classes():
    """get_config_classes() -> tuple of available config classes"""
    return _CONFIG_CLASSES


def get_protocols():
    """get_protocols() -> tuple of available class names"""
    return tuple(Serializer.get_class_tags())


def get_config_class(config):
    """get_config_class(config) -> config class name
       'config' can be a config object, a config class or a config class name.
    """
    if isinstance(config, type):
        for config_class in _CONFIG_CLASSES:
            if issubclass(config, config_class):
                return config_class
        raise TypeError("unsupported config_class {!r}".format(config))
    elif isinstance(config, ConfigBase):
        for config_class in _CONFIG_CLASSES:
            if isinstance(config, config_class):
                return config_class
        raise ValueError("invalid object {!r} of type {}: not a config[_class]".format(
            config, type(config).__name__))
    elif isinstance(config, str):
        for config_class in _CONFIG_CLASSES:
            if config in {get_config_class_name(config_class), config_class.__name__}:
                return config_class
        raise ValueError("unsupported config_class name {!r}".format(config))
    else:
        raise ValueError("invalid object {!r} of type {}: not a config[_class]".format(
            config, type(config).__name__))


def get_config_class_name(config_class):
    """get_config_class_name(config_class)"""
    return config_class.__name__.lower()


def _set_config_classes(config_classes):
    """_set_config_classes(...)"""
    if config_classes is None:
        return get_config_classes()
    elif isinstance(config_classes, ConfigBase):
        return get_config_class(config_classes)
    else:
        return tuple(get_config_class(config_class) for config_class in config_classes)


def _set_protocols(protocols):
    """_set_protocols(...)"""
    all_protocols = get_protocols()
    if protocols is None:
        return all_protocols
    if isinstance(protocols, str):
        protocols = (protocols, )
    for protocol in set(protocols).difference(all_protocols):
        raise ValueError("unsupported protocol {!r}".format(protocol))
    return protocols


def guess(filepath, *, config_classes=None, protocols=None):
    """guess_filetypes(filepath, *, config_classes=None, protocols=None) -> FileType objects"""
    config_classes = _set_config_classes(config_classes)
    protocols = _set_protocols(protocols)
    for config_class in config_classes:
        config_class_name = get_config_class_name(config_class)
        for template in _TEMPLATES[config_class]:
            for protocol in protocols:
                pattern = template.format(rootname='*', protocol=protocol, config_class=config_class_name)
                s_filepath = filepath.format(config_class=config_class_name, protocol=protocol)
                s_filename = os.path.basename(s_filepath)
                if fnmatch.fnmatchcase(s_filename, pattern):
                    yield FileType(filepath=s_filepath, protocol=protocol, config_class=config_class)


def standard_filepath(config, rootname, protocol):
    """standard_filepath(config, rootname, protocol) -> filepath
       Return a standard file path for the given obj/rootname/protocol.
       'obj' can be a config object or class.
    """
    config_class = get_config_class(config)
    template = _TEMPLATES[config_class][0]
    return template.format(rootname=rootname, protocol=protocol)


def classify(directory, config_classes=None, protocols=None):
    """classify(directory, *config_classes)
       Iterates on FileTypes for all the files in 'directory'.
       'directory' it can be a pattern for any directory path.
       Any 'config_class' in 'config_classes' can be a config class
       (Config, Schema, Validation) or its name.
    """
    config_classes = _set_config_classes(config_classes)
    protocols = _set_protocols(protocols)
    for config_class in config_classes:
        for template in _TEMPLATES[config_class]:
            for protocol in protocols:
                pattern = template.format(rootname='*', protocol=protocol)
                for filepath in glob.glob(os.path.join(directory, pattern)):
                    yield FileType(filepath=filepath, protocol=protocol, config_class=config_class)


def search_paths():
    """search_paths()
       Iterates on (search_paths, classes)
    """
    yield os.getcwd(), _CONFIG_CLASSES
    if 'DAIKON_CONFIG_PATH' in os.environ:
        for config_dir in os.environ['DAIKON_CONFIG_PATH'].split(':'):
            yield config_dir, (Config,)
    if 'DAIKON_SCHEMA_PATH' in os.environ:
        for schema_dir in os.environ['DAIKON_SCHEMA_PATH'].split(':'):
            yield schema_dir, (Schema,)


def discover(*directories, standard_paths=True):
    """discover(*directories)
       Discover FileTypes in directories. Each directory can be
        * a pattern
        * a tuple (pattern, config_classes)
       If standard_paths is True adds:
        * os.getcwd()
        * (os.environ['DAIKON_CONFIG_PATH'].split(':'), (Config,))
        * (os.environ['DAIKON_SCHEMA_PATH'].split(':'), (Schema,))
    """
    directory_d = collections.OrderedDict()
    if standard_paths:
        directories += tuple(search_paths())

    for entry in directories:
        if isinstance(entry, (tuple, list)):
            pattern, config_classes = entry
            config_classes = tuple(get_config_class(config_class) for config_class in config_classes)
        else:
            pattern = entry
            config_classes = _CONFIG_CLASSES
        for directory in glob.glob(pattern):
            if os.path.isdir(directory):
                directory = os.path.normpath(os.path.abspath(os.path.realpath(directory)))
                directory_d.setdefault(directory, set()).update(config_classes)

    for directory, config_classes in directory_d.items():
        for filetype in classify(directory, config_classes):
            yield filetype


def search_rootname(rootname, *, config_classes=None, protocols=None):
    """search(rootname, *, config_classes=None, protocols=None)
       Search for a file matching 'rootname' in filetypes. Return None
       if not found.
    """
    config_classes = _set_config_classes(config_classes)
    protocols = _set_protocols(protocols)

    def search_abs_rootname(abs_rootname, config_classes, protocols):
        """search_abs_rootname(abs_rootname, config_classes, protocols)"""
        if os.path.exists(abs_rootname):
            yield from guess(abs_rootname)
        for config_class in config_classes:
            for template in _TEMPLATES[config_class]:
                for protocol in protocols:
                    filepath = template.format(rootname=abs_rootname, protocol=protocol)
                    if os.path.exists(filepath):
                        yield FileType(filepath=filepath, config_class=config_class, protocol=protocol)

    if os.path.isabs(rootname):
        rootname = os.path.normpath(rootname)
        yield search_abs_rootname(rootname, config_classes, protocols)
    else:
        for directory, search_config_classes in search_paths():
            s_config_classes = [c_class for c_class in config_classes if c_class in search_config_classes]
            if os.path.isdir(directory):
                abs_rootname = os.path.normpath(os.path.join(directory, rootname))
                yield from search_abs_rootname(abs_rootname, s_config_classes, protocols)


def search_filetype(filetype):
    """search_filetype(filetype)"""
    if filetype.config_class is None:
        config_classes = None
    else:
        config_classes = (filetype.config_class,)
    if filetype.protocol is None:
        protocols = None
    else:
        protocols = (filetype.protocol,)
    yield from search_rootname(rootname=filetype.filepath, config_classes=config_classes, protocols=protocols)
