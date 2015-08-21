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
Utility function for guessing config file type, searching config files, ...
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
    """Get the list of config classes"""
    return _CONFIG_CLASSES


def get_protocols():
    """Get the list of serialization protocols"""
    return tuple(Serializer.get_class_tags())


def get_config_class(config):
    """Get a config class

       Parameters
       ----------
       config: any
           a config object, config class or config class name

       Raises
       ------
       TypeError
           unsupported config class
       ValueError
           unsupported config class name, invalid object

       Returns
       -------
       ConfigBase
           the requested config class
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
    """Get a config class name

    Parameters
    ----------
    config_class: ConfigBase
        the config class

    Returns
    -------
    str
        the config class name

    """
    return config_class.__name__.lower()


def _set_config_classes(config_classes):
    """Setup config classes"""
    if config_classes is None:
        return get_config_classes()
    elif isinstance(config_classes, ConfigBase):
        return get_config_class(config_classes)
    else:
        return tuple(get_config_class(config_class) for config_class in config_classes)


def _set_protocols(protocols):
    """Setup protocols"""
    all_protocols = get_protocols()
    if protocols is None:
        return all_protocols
    if isinstance(protocols, str):
        protocols = (protocols, )
    for protocol in set(protocols).difference(all_protocols):
        raise ValueError("unsupported protocol {!r}".format(protocol))
    return protocols


def guess(filepath, *, config_classes=None, protocols=None):
    """Guess a Filetype from a path

       Parameters
       ----------
       filepath: str
           the file path
       config_classes: tuple, optional
           a tuple of config classes to restrict search
       protocols: tuple, optional
           a tuple of protocols to restrict search

       Raises
       ------
       ValueError
           invalid class/invalid protocol

       Yields
       ------
       FileType
           the guessed filetype
    """
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
    """Get a standard filepath for a given config/rootname/protocol

       Parameters
       ----------
       config: ConfigBase
           the config object
       rootname: str
           the path rootname
       protocol: str
           the protocol

       Returns
       -------
       str
           the standard file path
    """
    config_class = get_config_class(config)
    template = _TEMPLATES[config_class][0]
    return template.format(rootname=rootname, protocol=protocol)


def classify(directory, config_classes=None, protocols=None):
    """Classify the content of a directory

       Parameters
       ----------
       directory: str
           the directory name
       config_classes: tuple, optional
           a tuple of config classes to restrict search
       protocols: tuple, optional
           a tuple of protocols to restrict search

       Raises
       ------
       ValueError
           invalid class/invalid protocol


       Yields
       ------
       FileType
           the found filetype object
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
    """Returns the standard search paths

       Yields
       ------
       tuple
           a 2-tuple containing (directory, config_classes), where config_classes is
           a tuple of Config classes
    """
    yield os.getcwd(), _CONFIG_CLASSES
    if 'ZIRKON_CONFIG_PATH' in os.environ:
        for config_dir in os.environ['ZIRKON_CONFIG_PATH'].split(':'):
            yield config_dir, (Config,)
    if 'ZIRKON_SCHEMA_PATH' in os.environ:
        for schema_dir in os.environ['ZIRKON_SCHEMA_PATH'].split(':'):
            yield schema_dir, (Schema,)


def discover(*directories, standard_paths=True):
    r"""Discover FileTypes in directories.

        Parameters
        ----------
        \*directories: str
           each directory can be a pattern or tuple (pattern, config_classes)
        standard_paths: bool, optional
            if True, add standard search_paths

        Yields
        ------
        FileType
            the found filetype objects
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
    """Searches FileTypes matching a given rootname

       Parameters
       ----------
       rootname: str
           the rootname
       config_classes: tuple, optional
           a tuple of config classes to restrict search
       protocols: tuple, optional
           a tuple of protocols to restrict search

       Raises
       ------
       ValueError
           invalid class/invalid protocol


       Yields
       ------
       FileType
           the found filetype objects
    """
    config_classes = _set_config_classes(config_classes)
    protocols = _set_protocols(protocols)

    def search_abs_rootname(abs_rootname, config_classes, protocols):
        """Searches for an absolute rootname"""
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
    """Searches FileTypes matching a given FileType

       Parameters
       ----------
       filetype: FileType
           the filetype object
       config_classes: tuple, optional
           a tuple of config classes to restrict search
       protocols: tuple, optional
           a tuple of protocols to restrict search

       Yields
       ------
       FileType
           the found filetype objects
    """
    if filetype.config_class is None:
        config_classes = None
    else:
        config_classes = (filetype.config_class,)
    if filetype.protocol is None:
        protocols = None
    else:
        protocols = (filetype.protocol,)
    yield from search_rootname(rootname=filetype.filepath, config_classes=config_classes, protocols=protocols)
