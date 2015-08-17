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

from .filetype import guess, get_protocols, \
    FileType, discover, search_filetype, \
    get_protocols, get_config_classes, \
    get_config_class, get_config_class_name
from .config import Config
from .schema import Schema
from .validation import Validation


_DEFAULTS = collections.OrderedDict()
_DEFAULTS['True'] = lambda: True
_DEFAULTS['False'] = lambda: False

class _IoManager(object):
    """_IoManager: read/write daikon config objects"""

    def __init__(self, printer, logger):
        self.printer = printer
        self.logger = logger

    def read_obj(self, obj, filetype):
        """read_obj(obj, filetype)"""
        if filetype:
            config_class_name = get_config_class_name(filetype.config_class)
            filepath = filetype.filepath
            protocol = filetype.protocol
            filepath.format(config_class=config_class_name, protocol=protocol)
            self.logger.info("reading {} from file {} using protocol {}...".format(
                config_class_name, filepath, protocol))
            if not os.path.exists(filepath):
                self.logger.error("{} file {!r} does not exist".format(config_class_name, filepath))
                sys.exit(1)
            obj.read(filepath, protocol=protocol)

    def dump_obj(self, obj, *, protocol="daikon", print_function=None):
        """dump_obj(obj, *, protocol="daikon", print_function=None)"""
        if print_function is None:
            print_function = self.printer
        for line in obj.to_string(protocol=protocol).split('\n'):
            print_function(line)

    def write_obj(self, obj, filetype, overwrite=False):
        """write_obj(obj, input_filepath=None, overwrite=False)"""
        filepath = filetype.filepath
        config_class_name = get_config_class_name(filetype.config_class)
        protocol = filetype.protocol
        if filepath:
            filepath = filepath.format(config_class=config_class_name, protocol=protocol)
            if os.path.exists(filepath) and not overwrite:
                _die(self.logger, "cannot overwrite existing file {!r}".format(filepath))
            self.logger.info("writing {} to file {} using protocol {}...".format(
                config_class_name, filepath, protocol))
            filedir = os.path.dirname(os.path.abspath(filepath))
            if not os.path.exists(filedir):
                self.logger.info("creating dir {}...".format(filedir))
                os.makedirs(filedir)
            obj.write(filepath, protocol=protocol)
        else:
            self.printer(obj.to_string(protocol=protocol))


def tabulate_filetypes(filetypes, header=True):
    """tabulate_filetypes(filetypes, header=True)"""
    files = []
    for filetype in filetypes:
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
        yield fmt.format(*row, lengths=lengths)


def list_files(printer, *data, header=True):
    """list_files(printer, *data, header=True)"""
    filetypes = discover(*data, standard_paths=True)
    for line in tabulate_filetypes(filetypes, header=header):
        printer(line)

def _create_logger(stream, verbose_level):
    """_create_logger() -> logger"""
    logger = logging.getLogger("DAIKON-LOG")
    if verbose_level == 0:
        log_level = logging.ERROR
    elif verbose_level == 1:
        log_level = logging.WARNING
    elif verbose_level == 2:
        log_level = logging.INFO
    elif verbose_level >= 3:
        log_level = logging.DEBUG
    log_handler = logging.StreamHandler(stream=stream)
    log_formatter = logging.Formatter("{levelname:8s} {message}", style="{")
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)
    logger.setLevel(log_level)
    return logger


def _die(logger, message, exit_code=1):
    """_die(logger, message, exit_code=1)"""
    print("DIE[{}]> {}".format(exit_code, message))
    logger.error(message)
    sys.exit(exit_code)


def _filetype(logger, filearg, config_class=None, protocol=None):
    """_filetype(...)"""
    if filearg is None:
        return None
    tokens = filearg.rsplit(':', 2)
    config_class_name = None
    protocol_name = None
    if len(tokens) == 3:
        filepath, protocol, config_class_name = tokens
    elif len(tokens) == 2:
        filepath, protocol = tokens
    elif len(tokens) == 1:
        filepath, = tokens
    if config_class_name is not None:
        config_class = get_config_class(config_class_name)
    if protocol_name is not None:
        protocol = get_protocol(protocol_name)
    if filepath == '-':
        filepath = ''
    if protocol is None or config_class is None:
        if config_class is None:
            config_classes = None
        else:
            config_classes = (config_class,)
        if protocol is None:
            protocols = None
        else:
            protocols = (protocol,)
        guessed_filetypes = list(guess(filepath, config_classes=config_classes, protocols=protocols))
        if len(guessed_filetypes) == 1:
            guessed_filetype = guessed_filetypes[0]
            replace_d = {}
            if protocol is None:
                protocol = guessed_filetype.protocol
            if config_class is None:
                config_class = guessed_filetype.config_class
    #if config_class is None:
    #    config_class_name = str(None)
    #else:
    #    config_class_name = get_config_class_name(config_class)
    #filepath = filepath.format(protocol=protocol, config_class=config_class_name)
    filetype = FileType(filepath=filepath, protocol=protocol, config_class=config_class)
    return filetype


def _input_filetype(logger, filearg, config_class=None):
    """_input_filetype(...)"""
    if filearg is None:
        return None
    filetype = _filetype(logger, filearg, config_class=config_class)
    found_filetypes = tuple(search_filetype(filetype))
    if len(found_filetypes) == 0:
        if not os.path.exists(filetype.filepath):
            _die(logger, "invalid value {}: input file not found".format(
                filearg))
    elif len(found_filetypes) > 1:
        logger.warning("{!r}: multiple matches: found {} matches:".format(filearg, len(found_filetypes)))
        for line in tabulate_filetypes(found_filetypes):
            logger.warning(" * {}".format(line))
        _die(logger, "invalid value {!r}: multiple matches".format(
            filearg, len(found_filetypes)))
    else:
        pass #filetype = found_filetypes[0]
    undetected_attributes = []
    for attribute in 'config_class', 'protocol':
        if getattr(filetype, attribute) is None:
            undetected_attributes.append(attribute)
    if undetected_attributes:
        _die(logger, "invalid value {}: cannot detect {}".format(
            filearg, ', '.join(undetected_attributes)))
    return filetype


def _input_schema_filetype(logger, filearg):
    """_input_schema_filetype(...)"""
    return _input_filetype(logger, filearg, config_class=Schema)


def _output_filetype(logger, filearg):
    """_output_filetype(...)"""
    return _filetype(logger, filearg)


def _validation_filetype(logger, filearg):
    """_validation_filetype(...)"""
    return _filetype(logger, filearg, config_class=Validation)


def _validate_args(logger, args):
    """_validate_args(logger, args)"""
    input_filetype = args.input_filetype
    output_filetype = args.output_filetype
    if output_filetype is not None:
        replace_d = {}
        if output_filetype.protocol is None:
            replace_d['protocol'] = input_filetype.protocol
        if output_filetype.config_class is None:
            replace_d['config_class'] = input_filetype.config_class
        elif output_filetype.config_class != input_filetype.config_class:
            logger.warning("output filename {}: config_class mismatch: {} or {}?".format(
                output_filetype.filepath,
                input_filetype.config_class.__name__,
                output_filetype.config_class.__name__))
            replace_d['config_class'] = input_filetype.config_class
        if replace_d:
            args.output_filetype = output_filetype._replace(**replace_d)
    validation_filetype = args.validation_filetype
    if validation_filetype is not None:
        if validation_filetype.protocol is None:
            args.validation_filetype = validation_filetype._replace(protocol=input_filetype.protocol)


def main_parse_args(log_stream=sys.stderr, out_stream=sys.stdout, argv=None):
    """main_parse_args(...)
    """
    if argv is None:  # pragma: no cover
        argv = sys.argv[1:]

    default_config_dirs = []
    default_schema_dirs = []
    default_verbose_level = 1
    default_defaults = 'False'

    config_class_names = [get_config_class_name(config_class) for config_class in get_config_classes()]
    description="""\
Daikon tool - read/write/validate config files.

The FILE values can be specified with the following syntax:

    filepath[:protocol[:config_class]]

where protocol can be any of the available protocols:

    {protocols}

and config_class any of the available classes:

    {config_classes}

Environment variables
---------------------
* DAIKON_CONFIG_PATH colon-separated list of directories for config files search
* DAIKON_SCHEMA_PATH colon-separated list of directories for schema files search
""".format(protocols=', '.join(get_protocols()),
    config_classes=', '.join(config_class_names))

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("--list", "-l",
                        action="store_true",
                        default=False,
                        help="list available files")

    parser.add_argument("--input", "-i",
                        dest="input_filetype",
                        metavar="FILE",
                        default=None,
                        type=str,
                        help="input file")

    parser.add_argument("--output", "-o",
                        dest="output_filetype",
                        metavar="OC",
                        default=None,
                        type=str,
                        help="output file")

    parser.add_argument("--schema", "-s",
                        dest="schema_filetype",
                        metavar="FILE",
                        default=None,
                        type=str,
                        help="schema input file")

    parser.add_argument("--validation", "-V",
                        dest="validation_filetype",
                        metavar="FILE",
                        default=None,
                        type=str,
                        help="validation output file")

    parser.add_argument("--config-dir", "-cd",
                        dest="config_dirs",
                        metavar="CD",
                        action="append",
                        default=default_config_dirs,
                        type=str,
                        help="add config dir")

    parser.add_argument("--schema-dir", "-sd",
                        dest="schema_dirs",
                        metavar="SD",
                        action="append",
                        default=default_schema_dirs,
                        type=str,
                        help="add config dir")

    parser.add_argument("--defaults", "-d",
                        metavar="D",
                        choices=tuple(_DEFAULTS.keys()),
                        default=default_defaults,
                        help="set defaults mode")

    parser.add_argument("--verbose", "-v",
                        dest="verbose_level",
                        action="count",
                        default=default_verbose_level,
                        help="increase verbosity")

    parser.add_argument("--quiet", "-q",
                        dest="verbose_level",
                        action="store_const",
                        const=0,
                        default=default_verbose_level,
                        help="quiet mode (only errors are shown)")

    parser.add_argument("--debug",
                        action="store_true",
                        default=False,
                        help="debug mode")

    parser.add_argument("--force", "-f",
                        action="store_true",
                        default=False,
                        help="force overwriting existing output files")

    args = parser.parse_args(argv)

    logger = _create_logger(log_stream, args.verbose_level)
    printer = lambda x: print(x, file=out_stream, flush=True)

    input_filetype = _input_filetype(logger, args.input_filetype)
    #print("input: {!r} -> {!r}".format(args.input_filetype, input_filetype))
    args.input_filetype = input_filetype

    schema_filetype = _input_schema_filetype(logger, args.schema_filetype)
    #print("schema: {!r} -> {!r}".format(args.schema_filetype, schema_filetype))
    args.schema_filetype = schema_filetype

    output_filetype = _output_filetype(logger, args.output_filetype)
    #print("output: {!r} -> {!r}".format(args.output_filetype, output_filetype))
    args.output_filetype = output_filetype

    validation_filetype = _validation_filetype(logger, args.validation_filetype)
    #print("validation: {!r} -> {!r}".format(args.output_filetype, validation_filetype))
    args.validation_filetype = validation_filetype

    _validate_args(logger, args)
    logger.debug("input_filetype:      %s", args.input_filetype)
    logger.debug("schema_filetype:     %s", args.schema_filetype)
    logger.debug("output_filetype:     %s", args.output_filetype)
    logger.debug("validation_filetype: %s", args.validation_filetype)
    return args, logger, printer


def main(log_stream=sys.stderr, out_stream=sys.stdout, argv=None):
    """main(...)
       Daikon tool main program.
    """

    args, logger, printer = main_parse_args(
        log_stream=log_stream, out_stream=out_stream, argv=argv)

    if args.list:
        paths = []
        for config_dir in args.config_dirs:
            paths.append((config_dir, (Config,)))
        for schema_dir in args.schema_dirs:
            paths.append((schema_dir, (Schema,)))
        list_files(printer, *paths)
        return

    io_manager = _IoManager(printer=printer, logger=logger)

    defaults_factory = _DEFAULTS[args.defaults]

    try:
        if args.schema_filetype:
            schema = Schema()
            io_manager.read_obj(schema, args.schema_filetype)
        else:
            schema = None

        if args.input_filetype:
            config_class = args.input_filetype.config_class
            config_args = {}
            if issubclass(config_class, Config):
                config_args['defaults'] = defaults_factory()
            config = config_class(**config_args)
            io_manager.read_obj(config, args.input_filetype)
            if schema is not None:
                validation = schema.validate(config)
                if args.validation_filetype is not None:
                    io_manager.write_obj(validation, args.validation_filetype, overwrite=args.force)
                if validation and args.validation_filetype is None:
                    logger.warning("validation failed for config %s:", args.input_filetype.filepath)
                    io_manager.dump_obj(validation, print_function=logger.warning)
            if args.output_filetype is None:
                io_manager.dump_obj(config, protocol=args.input_filetype.protocol)
            else:
                io_manager.write_obj(config, args.output_filetype, overwrite=args.force)
    except Exception as err:  # pylint: disable=W0703
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.stderr.write("ERR: {}: {}\n".format(type(err).__name__, err))
        sys.exit(1)


