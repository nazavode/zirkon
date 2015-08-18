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
daikon._tool.utils
==================
Utilities.
"""

__author__ = "Simone Campagna"

__all__ = [
    'create_template_from_schema',
    'replace_deferred',
]

import collections

from .config import Config
from .config_section import ConfigSection
from .schema_section import SchemaSection
from .toolbox.deferred import Deferred


def _get_validator_default(validator):
    """_get_validator_default(validator) -> has_default, default"""
    for argument_name, argument_value in validator.actual_arguments.items():
        if argument_name == "default":
            return True, argument_value
    return False, None


def create_template_from_schema(schema, *, config=None):
    """create_template_from_schema(schema, *, config=None)
       Create a template file from a schema.

       >>> from daikon.schema import Schema
       >>> from daikon.validator import Float, Int, Str
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
    """
    if config is None:
        config = Config(late_evaluation=True)
    late_evaluation = config.late_evaluation
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
                if late_evaluation:
                    config[key] = default
                else:
                    if isinstance(default, Deferred):
                        try:
                            default_value = default.evaluate()
                        except:  # pylint: disable=W0702
                            default_value = "# default: {}".format(default.unparse())
                        config[key] = default_value
                    else:
                        config[key] = default
                config[key] = default
            else:
                config[key] = "# {!r}".format(value)
    return config


def replace_deferred(config, *, ref_section=None):
    """replace_deferred(config, *, ref_section=None)
       Replace all deferred expressions with their current value.
    """
    if ref_section is None:
        ref_section = config
    for key, value in config.items():
        if isinstance(value, collections.Mapping):
            replace_deferred(value, ref_section=ref_section[key])
        else:
            if isinstance(value, Deferred):
                config[key] = value.evaluate({'SECTION': ref_section, 'ROOT': ref_section.root})
    if isinstance(config, ConfigSection) and config.defaults() is not None:
        replace_deferred(config.defaults(), ref_section=config)
