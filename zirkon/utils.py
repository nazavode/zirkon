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
Some utilities for config objects.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'create_template_from_schema',
    'replace_macros',
    'get_key',
    'set_key',
    'del_key',
]

import collections

from .config import Config
from .config_section import ConfigSection
from .schema_section import SchemaSection


def _get_validator_default(validator):
    """Returns the default value for a validator"""
    for argument_name, argument_value in validator.actual_arguments.items():
        if argument_name == "default":
            return True, argument_value
    return False, None


def create_template_from_schema(schema, *, config=None):
    """Creates a template file from a schema.

       >>> from zirkon.schema import Schema
       >>> from zirkon.validator import Float, Int, Str
       >>> schema = Schema()
       >>> schema['alpha'] = Float(default=0.5)
       >>> schema['input_file'] = Str(min_len=1)
       >>> schema['data'] = {}
       >>> schema['data']['i'] = Int(max=10)
       >>> schema['data']['j'] = Int(default=2)
       >>> config = create_template_from_schema(schema)
       >>> config.dump()
       alpha = 0.5
       input_file = '# Str(min_len=1)'
       [data]
           i = '# Int(max=10)'
           j = 2

       Parameters
       ----------
       schema: |Schema|
           the validating schema
       config: |Config|, optional
           the config object to be filled in

       Returns
       -------
       |Config|
           the filled config object

       Raises
       ------
       ValueError
           invalid schema

    """
    if config is None:
        config = Config()
    if not isinstance(schema, SchemaSection):
        raise ValueError("invalid argument {!r} of type {}: not a Schema".format(
            schema, type(schema).__name__))

    for key, value in schema.items():
        if isinstance(value, collections.Mapping):
            section = config.add_section(key)
            create_template_from_schema(value, config=section)
        else:
            has_default, default = _get_validator_default(value)
            if has_default:
                config[key] = default
            else:
                config[key] = "# {!r}".format(value)
    return config


def replace_macros(config):
    """Replaces all macros with their current value.
       Parameters
       ----------
       config: |Config|, optional
           the config object
    """
    for key, value in config.items():
        if isinstance(value, collections.Mapping):
            replace_macros(value)
        else:
            value = config[key]
            config[key] = value
    if isinstance(config, ConfigSection) and config.defaults is not None:
        with config.defaults.referencing(config):
            replace_macros(config.defaults)


def _get_key_tuple(key):
    """Returns a keys tuple from a key name: "k0.k2" -> ("k0", "k1")"""
    if isinstance(key, (list, tuple)):
        return key
    elif isinstance(key, str):
        key = key.strip()
        if key:
            return key.split(".")
        else:
            return ()
    else:
        raise TypeError("invalid object {!r} of type {}".format(key, type(key).__name__))


def get_key(config, key):
    """Returns the value for a key from config. Key can be
       * a dot-separated list of keys, or
       * a tuple of keys.

       >>> from zirkon.config import Config
       >>> config = Config()
       >>> config["x"] = 10
       >>> config["sub"] = {"y": 20}
       >>> get_key(config, "x")
       10
       >>> get_key(config, "sub.y")
       20
       >>> get_key(config, ("sub", "y"))
       20
       >>> get_key(config, "sub")
       ConfigSection(dictionary=OrderedDict([('y', 20)]))
       >>>

       Parameters
       ----------
       config: |Config|, optional
           the config object
       key: str, tuple
           a string like "k0.k1..." or a tuple ("k0", "k1", ...)

       Raises
       ------
       KeyError
           key not found

       Returns
       -------
       |any|
           the value
    """
    key_tuple = _get_key_tuple(key)
    section = config
    for key in key_tuple:
        section = section[key]
    return section


def set_key(config, key, value, *, parents=False):
    """Sets a key value from config. Key can be
       * a dot-separated list of keys, or
       * a tuple of keys.

       >>> config = Config()
       >>> set_key(config, "x", 10)
       >>> set_key(config, "sub", {'y': 20})
       >>> set_key(config, "sub.z", 30)
       >>> config.dump()
       x = 10
       [sub]
           y = 20
           z = 30
       >>>

       Parameters
       ----------
       config: |Config|, optional
           the config object
       key: str, tuple
           a string like "k0.k1..." or a tuple ("k0", "k1", ...)
       parents: bool, optional
           if True, creates missing intermediate sections

       Raises
       ------
       KeyError
           key not found
    """
    key_tuple = _get_key_tuple(key)
    if len(key_tuple) == 0:
        raise KeyError(key)
    section = config
    for key in key_tuple[:-1]:
        if parents and not section.has_section(key):
            section = section.add_section(key)
        else:
            section = section[key]
    section[key_tuple[-1]] = value


def del_key(config, key, *, ignore_errors=False):
    """Deletes a key value from config. Key can be
       * a dot-separated list of keys, or
       * a tuple of keys.

       >>> config = Config()
       >>> config["x"] = 10
       >>> config["sub1"] = {"y": 20, "z": 30}
       >>> config["sub2"] = {"y": 20, "z": 30}
       >>> del_key(config, "x")
       >>> del_key(config, "sub1")
       >>> del_key(config, "sub2.y")
       >>> config.dump()
       [sub2]
           z = 30
       >>>

       Parameters
       ----------
       config: |Config|, optional
           the config object
       key: str, tuple
           a string like "k0.k1..." or a tuple ("k0", "k1", ...)
       ignore_errors: bool, optional
           if True, ignore errors about missing intermediate sections

       Raises
       ------
       KeyError
           key not found
    """
    key_tuple = _get_key_tuple(key)
    if len(key_tuple) == 0:
        config.clear()
    else:
        section = config
        for key in key_tuple[:-1]:
            if ignore_errors and not section.has_section(key):
                return
            section = section[key]
        key = key_tuple[-1]
        if ignore_errors and key not in section:
            return
        del section[key]

