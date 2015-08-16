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
    'get_config_class',
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


def guess(filepath):
    """guess(filepath) -> FileType object"""
    filename = os.path.basename(filepath)
    protocols = get_protocols()
    for config_class, templates in _TEMPLATES.items():
        for template in templates:
            for protocol in protocols:
                pattern = template.format(rootname='*', protocol=protocol, config_class=config_class.__name__.lower())
                if fnmatch.fnmatchcase(filename, pattern):
                    return FileType(filepath=filepath, protocol=protocol, config_class=config_class)
    return FileType(filepath=filepath, protocol=None, config_class=None)


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
            if config_class.__name__ == config:
                return config_class
        raise ValueError("unsupported config_class name {!r}".format(config))
    else:
        raise ValueError("invalid object {!r} of type {}: not a config[_class]".format(
            config, type(config).__name__))


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
    if config_classes is None:
        config_classes = _CONFIG_CLASSES
    else:
        config_classes = (get_config_class(config) for config in config_classes)
    all_protocols = get_protocols()
    if protocols is None:
        protocols = all_protocols
    else:
        for protocol in set(protocols).difference(all_protocols):
            raise ValueError("unsupported protocol {!r}".format(protocol))
    for config_class in config_classes:
        for template in _TEMPLATES[config_class]:
            for protocol in protocols:
                pattern = template.format(rootname='*', protocol=protocol)
                for filepath in glob.glob(os.path.join(directory, pattern)):
                    yield FileType(filepath=filepath, protocol=protocol, config_class=config_class)



