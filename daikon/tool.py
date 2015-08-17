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
toolbox.tool
============
Main Daikon tool program.
"""

__author__ = "Simone Campagna"

__all__ = [
    'main',
]

import argparse
import collections
import logging
import os
import sys

from .filetype import guess, get_protocols, FileType, discover, search_filetype
from .config import Config
from .schema import Schema
from .validation import Validation


def _filetype(config_class, filearg):
    """_filetype(...)"""
    if ':' in filearg:
        filepath, protocol = filearg.rsplit(':', 1)
        if filepath == '-':
            filepath = ''
        if protocol not in get_protocols():
            raise ValueError("invalid protocol {}".format(protocol))
        filetype = FileType(filepath=filepath, protocol=protocol, config_class=config_class)
    else:
        if filearg == '-':
            filepath = ''
        else:
            filepath = filearg
        filetype = guess(filepath)
        replace_d = {}
        if filetype.config_class != config_class:
            replace_d['config_class'] = config_class
        if replace_d:
            filetype = filetype._replace(**replace_d)
    return filetype


def _config_filetype(filearg):
    """_config_filetype(...)"""
    return _filetype(Config, filearg)


def _schema_filetype(filearg):
    """_schema_filetype(...)"""
    return _filetype(Schema, filearg)


def _validation_filetype(filearg):
    """_validation_filetype(...)"""
    return _filetype(Validation, filearg)


class _IoManager(object):
    """_IoManager: read/write daikon config objects"""

    def __init__(self, printer, logger):
        self.printer = printer
        self.logger = logger

    def read_obj(self, obj, filetype):
        """read_obj(obj, filetype)"""
        if filetype:
            config_class_name = filetype.config_class.__name__.lower()
            actual_filetype = search_filetype(filetype)
            if actual_filetype is None:
                self.logger.error("cannot find {} {}".format(config_class_name, filetype.filepath))
                sys.exit(2)
            elif actual_filetype.protocol is None:
                self.logger.error("cannot guess protocol for {} {}".format(config_class_name, filetype.filepath))
                sys.exit(2)
            filepath = actual_filetype.filepath
            protocol = filetype.protocol
            filepath.format(config_class=config_class_name, protocol=protocol)
            self.logger.debug("reading {} from file {} using protocol {}...".format(
                config_class_name, filepath, protocol))
            if not os.path.exists(filepath):
                self.logger.error("{} file {!r} does not exist".format(config_class_name, filepath))
                sys.exit(1)
            obj.read(filepath, protocol=protocol)

    def dump_obj(self, obj):
        """dump_obj(obj)"""
        for line in obj.to_string(protocol="daikon").split('\n'):
            self.printer(line)

    def write_obj(self, obj, filetype):
        """write_obj(obj, input_filepath=None)"""
        if filetype is None:
            self.dump_obj(obj)
            return
        filepath = filetype.filepath
        config_class_name = filetype.config_class.__name__.lower()
        protocol = filetype.protocol
        if filepath:
            filepath = filepath.format(config_class=config_class_name, protocol=protocol)
            self.logger.debug("writing {} to file {} using protocol {}...".format(
                config_class_name, filepath, protocol))
            filedir = os.path.dirname(os.path.abspath(filepath))
            if not os.path.exists(filedir):
                self.logger.debug("creating dir {}...".format(filedir))
                os.makedirs(filedir)
            obj.write(filepath, protocol=protocol)
        else:
            self.printer(obj.to_string(protocol=protocol))


def _set_missing_args(args):
    """_set_missing_args(args)"""
    for arg in "config", "schema":
        i_arg = "input_" + arg
        o_arg = "output_" + arg
        o_filetype = getattr(args, o_arg)
        if o_filetype is not None and o_filetype.protocol is None:
            i_filetype = getattr(args, i_arg)
            if i_filetype is not None:
                o_filetype = o_filetype._replace(protocol=i_filetype.protocol)
                setattr(args, o_arg, o_filetype)


def list_files(printer, *data):
    """list_files(printer, *data)"""
    files = []
    for filetype in discover(*data, standard_paths=True):
        files.append((filetype.filepath, filetype.config_class.__name__, filetype.protocol))
    files.sort(key=lambda x: x[0])
    files.sort(key=lambda x: x[1])
    files.sort(key=lambda x: x[2])
    rows = [("filename", "type", "protocol")]
    rows.extend(files)
    col_indices = tuple(range(len(rows[0])))
    lengths = tuple(max(len(row[col_index]) for row in rows) for col_index in col_indices)
    hdr = tuple(('-' * length) for length in lengths)
    rows.insert(1, hdr)
    fmt = ' '.join("{{{i}:{{lengths[{i}]}}}}".format(i=col_index) for col_index in col_indices)
    for row in rows:
        printer(fmt.format(*row, lengths=lengths))


def _create_logger(stream, verbose_level):
    """_create_logger() -> logger"""
    logger = logging.getLogger("DAIKON-LOG")
    if verbose_level == 0:
        log_level = logging.WARNING
    elif verbose_level == 1:
        log_level = logging.INFO
    elif verbose_level >= 2:
        log_level = logging.DEBUG
    log_handler = logging.StreamHandler(stream=stream)
    log_formatter = logging.Formatter("{levelname:8s} {message}", style="{")
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    logger.setLevel(log_level)
    return logger


def main(log_stream=sys.stderr, out_stream=sys.stdout, args=None):  # pylint: disable=R0912,R0914,R0915
    """main()
       Daikon tool main program.
    """
    if args is None:  # pragma: no cover
        args = sys.argv[1:]

    defaults = collections.OrderedDict()
    defaults['True'] = lambda: True
    defaults['False'] = lambda: False

    default_config_dirs = []
    default_schema_dirs = []
    default_verbose_level = 0
    default_defaults = 'False'

    parser = argparse.ArgumentParser(
        description="""\
Daikon tool - read/write/validate config files

Environment variables
---------------------
* DAIKON_CONFIG_PATH : colon-separated list of directories for config files
* DAIKON_SCHEMA_PATH : colon-separated list of directories for schema files
""",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--list", "-l",
                        action="store_true",
                        default=False,
                        help="list available files")

    parser.add_argument("--input-config", "-c",
                        metavar="IC",
                        default=None,
                        type=_config_filetype,
                        help="input config file")

    parser.add_argument("--output-config", "-co",
                        metavar="OC",
                        default=None,
                        type=_config_filetype,
                        help="output config file")

    parser.add_argument("--config-dir", "-cd",
                        dest="config_dirs",
                        metavar="CD",
                        action="append",
                        default=default_config_dirs,
                        type=str,
                        help="add config dir")

    parser.add_argument("--input-schema", "-s",
                        metavar="IS",
                        default=None,
                        type=_schema_filetype,
                        help="input schema file")

    parser.add_argument("--output-schema", "-so",
                        metavar="OS",
                        default=None,
                        type=_schema_filetype,
                        help="output schema file")

    parser.add_argument("--schema-dir", "-sd",
                        dest="schema_dirs",
                        metavar="SD",
                        action="append",
                        default=default_schema_dirs,
                        type=str,
                        help="add config dir")

    parser.add_argument("--output-validation", "-vo",
                        metavar="OV",
                        default=None,
                        type=_validation_filetype,
                        help="output validation file")

    parser.add_argument("--defaults", "-d",
                        metavar="D",
                        choices=tuple(defaults.keys()),
                        default=default_defaults,
                        help="set defaults mode")

    parser.add_argument("--verbose", "-v",
                        dest="verbose_level",
                        action="count",
                        default=default_verbose_level,
                        help="increase verbosity")

    parser.add_argument("--debug",
                        action="store_true",
                        default=False,
                        help="debug mode")

    args = parser.parse_args(args)
    _set_missing_args(args)

    logger = _create_logger(log_stream, args.verbose_level)
    printer = lambda x: print(x, file=out_stream, flush=True)

    if args.output_validation is not None and args.output_validation.protocol is None:
        if args.input_config is not None:
            args.output_validation = args.output_validation._replace(
                protocol=args.input_config.protocol)

    if args.list:
        paths = []
        for config_dir in args.config_dirs:
            paths.append((config_dir, (Config,)))
        for schema_dir in args.schema_dirs:
            paths.append((schema_dir, (Schema,)))
        list_files(printer, *paths)
        return

    io_manager = _IoManager(printer=printer, logger=logger)

    defaults_factory = defaults[args.defaults]

    try:
        if args.input_schema:
            schema = Schema()
            io_manager.read_obj(schema, args.input_schema)
            if args.output_schema is not None:
                io_manager.write_obj(schema, args.output_schema)
        else:
            schema = None

        if args.input_config:
            config = Config(defaults=defaults_factory())
            io_manager.read_obj(config, args.input_config)
            if schema is not None:
                validation = schema.validate(config)
                if validation:
                    logger.warning("validation failed for config %s", args.input_config.filepath)
                    io_manager.write_obj(validation, args.output_validation)
            io_manager.write_obj(config, args.output_config)
    except Exception as err:  # pylint: disable=W0703
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.stderr.write("ERR: {}: {}\n".format(type(err).__name__, err))
        sys.exit(1)


