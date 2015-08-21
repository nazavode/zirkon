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
Main 'zirkon' tool program.
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

from ..filetype import FileType, guess, discover, search_filetype, \
    get_protocols, get_config_classes, get_config_class, get_config_class_name
from ..config import Config
from ..schema import Schema
from ..utils import create_template_from_schema
from ..validation import Validation
from ..version import VERSION

from .trace_errors import trace_errors

_DEFAULTS = collections.OrderedDict()
_DEFAULTS['True'] = lambda: True
_DEFAULTS['False'] = lambda: False


class _IoManager(object):
    """_IoManager: read/write zirkon config objects

       Parameters
       ----------
       printer: function
           the printer function
       logger: logging.Logger
           the logger

       Attributes
       ----------
       printer: function
           the printer function
       logger: logging.Logger
           the logger
    """

    def __init__(self, printer, logger):
        self.printer = printer
        self.logger = logger

    def read_obj(self, obj, filetype):
        """Reads an object from file.

           Parameters
           ----------
           obj: ConfigBase
               the object to be read
           filetype: FileType
               the input file
        """
        if filetype:
            config_class_name = get_config_class_name(filetype.config_class)
            filepath = filetype.filepath
            protocol = filetype.protocol
            filepath.format(config_class=config_class_name, protocol=protocol)
            self.logger.info("reading {} from file {} using protocol {}...".format(
                config_class_name, filepath, protocol))
            if not os.path.exists(filepath):  # pragma: no cover
                self.logger.error("{} file {!r} does not exist".format(config_class_name, filepath))
                sys.exit(1)
            obj.read(filepath, protocol=protocol)

    def dump_obj(self, obj, *, protocol="zirkon", print_function=None):
        """Dumps an object.

           Parameters
           ----------
           obj: ConfigBase
               the object to be dumped
           protocol: str
               the serialization protocol
           print_function: function, optional
               the print function
        """

        if print_function is None:  # pragma: no cover
            print_function = self.printer
        for line in obj.to_string(protocol=protocol).split('\n'):
            print_function(line)

    def write_obj(self, obj, filetype, overwrite=False):
        """Writes an object to file.

           Parameters
           ----------
           obj: ConfigBase
               the object to be written
           filetype: FileType
               the input file
           overwrite: bool, optional
               enables overwriting output file (defaults to False)
        """
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
    """tabulate_filetypes(filetypes, header=True)

       Parameters
       ----------
       filetypes: list
           a list of FileType objects
       header: bool, optional
           include an header (defaults to True)

       Yields
       ------
       str
           all the output lines
    """
    files = []
    for filetype in filetypes:
        files.append((filetype.filepath, filetype.config_class.__name__, filetype.protocol))
    files.sort(key=lambda x: x[0])
    files.sort(key=lambda x: x[1])
    files.sort(key=lambda x: x[2])
    rows = []
    if header:
        rows.append(("filename", "type", "protocol"))
    rows.extend(files)
    col_indices = tuple(range(len(rows[0])))
    lengths = tuple(max(len(row[col_index]) for row in rows) for col_index in col_indices)
    if header:
        hdr = tuple(('-' * length) for length in lengths)
        rows.insert(1, hdr)
    fmt = ' '.join("{{{i}:{{lengths[{i}]}}}}".format(i=col_index) for col_index in col_indices)
    for row in rows:
        yield fmt.format(*row, lengths=lengths)


def list_files(printer, header=True, *, config_dirs, schema_dirs):
    """Lists files.

       Parameters
       ----------
       printer: function
           the printer function
       header: bool, optional
           adds an header line (defaults to True)
       config_dirs: tuple
           list of config directories
       schema_dirs: tuple
           list of schema directories
    """
    paths = []
    for config_dir in config_dirs:
        paths.append((config_dir, (Config,)))
    for schema_dir in schema_dirs:
        paths.append((schema_dir, (Schema,)))
    filetypes = discover(*paths, standard_paths=True)
    for line in tabulate_filetypes(filetypes, header=header):
        printer(line)


def _create_logger(stream, verbose_level):
    """Creates a logger.

       Parameters
       ----------
       stream: file
           the logger's stream
       verbose_level: int
           the initial verbose level

       Returns
       -------
       Logger
           the logger
    """
    logger = logging.getLogger("ZIRKON-LOG")
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
    """Logs an error message and terminates the program.

       Parameters
       ----------
       logger: Logger
           the logger
       message: str
           the error message
       exit_code: int, optional
           the exit code (defaults to 1)
    """
    logger.error(message)
    sys.exit(exit_code)


def _filetype(logger, filearg, config_class=None, protocol=None):
    """Converts a string from command line to filetype.

       Parameters
       ----------
       logger: Logger
           the logger
       filearg: str
           the command line string
       config_class: ConfigBase, optional
           the expected config class (defaults to None)
       protocol: str, optional
           the expected protocol (defaults to None)

       Returns
       -------
       FileType
           the FileType object
    """
    if filearg is None:
        return None
    tokens = filearg.rsplit(':', 2)
    tokens += tuple(None for _ in range(3 - len(tokens)))
    filepath, protocol, config_class_name = tokens
    if config_class_name is not None:
        config_class = get_config_class(config_class_name)
    if protocol is not None and protocol not in get_protocols():
        _die(logger, "invalid protocol {}".format(protocol))
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
            if protocol is None:
                protocol = guessed_filetype.protocol
            if config_class is None:
                config_class = guessed_filetype.config_class
    filetype = FileType(filepath=filepath, protocol=protocol, config_class=config_class)
    return filetype


def _input_filetype(logger, filearg, config_class=None):
    """Converts a string from command line to an input filetype.

       Parameters
       ----------
       logger: Logger
           the logger
       filearg: str
           the command line string
       config_class: ConfigBase, optional
           the expected config class (defaults to None)

       Returns
       -------
       FileType
           the FileType object
    """
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
            filearg))
    undetected_attributes = []
    for attribute in 'config_class', 'protocol':
        if getattr(filetype, attribute) is None:
            undetected_attributes.append(attribute)
    if undetected_attributes:
        _die(logger, "invalid value {}: cannot detect {}".format(
            filearg, ', '.join(undetected_attributes)))
    return filetype


def _input_schema_filetype(logger, filearg):
    """Converts a string from command line to an input schema filetype.

       Parameters
       ----------
       logger: Logger
           the logger
       filearg: str
           the command line string

       Returns
       -------
       FileType
           the FileType object
    """
    return _input_filetype(logger, filearg, config_class=Schema)


def _output_filetype(logger, filearg):
    """Converts a string from command line to an output filetype.

       Parameters
       ----------
       logger: Logger
           the logger
       filearg: str
           the command line string

       Returns
       -------
       FileType
           the FileType object
    """
    return _filetype(logger, filearg)


def _validation_filetype(logger, filearg):
    """Converts a string from command line to an output validation filetype.

       Parameters
       ----------
       logger: Logger
           the logger
       filearg: str
           the command line string

       Returns
       -------
       FileType
           the FileType object
    """
    return _filetype(logger, filearg, config_class=Validation)


def _validate_args(logger, args):
    """Validates args.

       Parameters
       ----------
       logger: Logger
           the logger
       filearg: str
           the command line string
    """
    input_filetype = args.input_filetype
    schema_filetype = args.schema_filetype
    output_filetype = args.output_filetype
    validation_filetype = args.validation_filetype
    ref_protocol = None
    ref_config_class = None
    if input_filetype is not None:
        ref_protocol = input_filetype.protocol
        ref_config_class = input_filetype.config_class
    elif schema_filetype is not None:
        ref_protocol = schema_filetype.protocol

    if output_filetype is not None:
        replace_d = {}
        if output_filetype.protocol is None and ref_protocol is not None:
            replace_d['protocol'] = ref_protocol
        if ref_config_class is not None:
            if output_filetype.config_class is None:
                replace_d['config_class'] = ref_config_class
            elif output_filetype.config_class != ref_config_class:
                logger.warning("output filename {}: config_class mismatch: {} or {}?".format(
                    output_filetype.filepath,
                    ref_config_class.__name__,
                    output_filetype.config_class.__name__))
                replace_d['config_class'] = ref_config_class
        if replace_d:
            args.output_filetype = output_filetype._replace(**replace_d)

    if validation_filetype is not None:
        if validation_filetype.protocol is None and ref_protocol is not None:
            args.validation_filetype = validation_filetype._replace(protocol=ref_protocol)
    if args.create_template:
        if schema_filetype is None:
            _die(logger, "missing required argument --schema/-s")


def main_parse_args(log_stream=sys.stderr, out_stream=sys.stdout, argv=None):
    """Parses command line arguments.

       Parameters
       ----------
       log_stream: file, optional
           the log file (defaults to sys.stderr)
       out_stream: file, optional
           the output file (defaults to sys.stdout)
       argv: list, optional
           the command line arguments (defaults to None, meaning sys.args[1:])
    """
    if argv is None:  # pragma: no cover
        argv = sys.argv[1:]

    default_config_dirs = []
    default_schema_dirs = []
    default_verbose_level = 1
    default_defaults = 'False'

    config_class_names = [get_config_class_name(config_class) for config_class in get_config_classes()]
    description = """\
Zirkon tool - read/write/validate config files.

The FILE values can be specified with the following syntax:

    filepath[:protocol[:config_class]]

where protocol can be any of the available protocols:

    {protocols}

and config_class any of the available classes:

    {config_classes}

Environment variables
---------------------
* ZIRKON_CONFIG_PATH colon-separated list of directories for config files search
* ZIRKON_SCHEMA_PATH colon-separated list of directories for schema files search
""".format(protocols=', '.join(get_protocols()),
           config_classes=', '.join(config_class_names))

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    input_group = parser.add_mutually_exclusive_group()

    input_group.add_argument("--list", "-l",
                             action="store_true",
                             default=False,
                             help="list available files")

    input_group.add_argument("--input", "-i",
                             dest="input_filetype",
                             metavar="FILE",
                             default=None,
                             type=str,
                             help="input file")

    input_group.add_argument("--create-template", "-t",
                             action="store_true",
                             default=False,
                             help="create a template from schema")

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

    parser.add_argument("--version",
                        action="version",
                        version="%(prog)s {}".format(VERSION),
                        help="show version")

    args = parser.parse_args(argv)

    logger = _create_logger(log_stream, args.verbose_level)
    printer = lambda x: print(x, file=out_stream, flush=True)

    input_filetype = _input_filetype(logger, args.input_filetype)
    args.input_filetype = input_filetype

    schema_filetype = _input_schema_filetype(logger, args.schema_filetype)
    args.schema_filetype = schema_filetype

    output_filetype = _output_filetype(logger, args.output_filetype)
    args.output_filetype = output_filetype

    validation_filetype = _validation_filetype(logger, args.validation_filetype)
    args.validation_filetype = validation_filetype

    _validate_args(logger, args)
    logger.debug("input_filetype:      %s", args.input_filetype)
    logger.debug("schema_filetype:     %s", args.schema_filetype)
    logger.debug("output_filetype:     %s", args.output_filetype)
    logger.debug("validation_filetype: %s", args.validation_filetype)
    return args, logger, printer


def main(log_stream=sys.stderr, out_stream=sys.stdout, argv=None):
    """Runs the main program.

       Parameters
       ----------
       log_stream: file, optional
           the log file (defaults to sys.stderr)
       out_stream: file, optional
           the output file (defaults to sys.stdout)
       argv: list, optional
           the command line arguments (defaults to None, meaning sys.args[1:])
    """

    args, logger, printer = main_parse_args(
        log_stream=log_stream, out_stream=out_stream, argv=argv)

    if args.list:
        list_files(printer, config_dirs=args.config_dirs, schema_dirs=args.schema_dirs)
        return

    io_manager = _IoManager(printer=printer, logger=logger)

    defaults_factory = _DEFAULTS[args.defaults]

    with trace_errors(args.debug):
        schema = None
        default_output_protocol = "zirkon"
        if args.schema_filetype:
            schema = Schema()
            io_manager.read_obj(schema, args.schema_filetype)

        config = None
        if args.input_filetype:
            default_output_protocol = args.input_filetype.protocol
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
        elif args.create_template:
            config = Config()
            create_template_from_schema(schema=schema, config=config)

        if config is not None:
            if args.output_filetype is None:
                io_manager.dump_obj(config, protocol=default_output_protocol)
            else:
                io_manager.write_obj(config, args.output_filetype, overwrite=args.force)
