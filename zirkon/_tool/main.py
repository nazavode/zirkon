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
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
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


def list_files(params, *, config_dirs, schema_dirs):
    """Lists files.

       Parameters
       ----------
       params: dict
           common params
       config_dirs: tuple
           list of config directories
       schema_dirs: tuple
           list of schema directories
    """
    printer = params["printer"]
    header = params.get("header", True)
    paths = []
    for config_dir in config_dirs:
        paths.append((config_dir, (Config,)))
    for schema_dir in schema_dirs:
        paths.append((schema_dir, (Schema,)))
    filetypes = discover(*paths, standard_paths=True)
    for line in tabulate_filetypes(filetypes, header=header):
        printer(line)


def read_config(params, *, defaults, input_filetype, schema_filetype,
                output_filetype, validation_filetype):
    """Reads a config file.

       Parameters
       ----------
       params: dict
           common parameters
       defaults: bool
           enable defaults
       input_filetype: FileType
           input filetype
       schema_filetype: FileType
           schema filetype
       output_filetype: FileType
           output filetype
       validation_filetype: FileType
           validation filetype
    """
    printer = params["printer"]
    logger = params["logger"]
    default_output_protocol = params["default_protocol"]
    io_manager = _IoManager(printer=printer, logger=logger)

    defaults_factory = _DEFAULTS[defaults]

    with trace_errors(params["debug"]):
        schema = None
        if schema_filetype:
            schema = Schema()
            io_manager.read_obj(schema, schema_filetype)

        default_output_protocol = input_filetype.protocol
        config_class = input_filetype.config_class
        config_args = {}
        if issubclass(config_class, Config):
            config_args['defaults'] = defaults_factory()
        config = config_class(**config_args)
        io_manager.read_obj(config, input_filetype)
        if schema is not None:
            validation = schema.validate(config)
            if validation_filetype is not None:
                io_manager.write_obj(validation, validation_filetype, overwrite=params["force"])
            if validation and validation_filetype is None:
                logger.warning("validation failed for config %s:", input_filetype.filepath)
                io_manager.dump_obj(validation, print_function=logger.warning)

        if output_filetype is None:
            io_manager.dump_obj(config, protocol=default_output_protocol)
        else:
            io_manager.write_obj(config, output_filetype, overwrite=params["force"])


def create_config(params, *, schema_filetype, output_filetype):
    """Creates a config file from a schema.

       Parameters
       ----------
       params: dict
           common parameters
       schema_filetype: FileType
           schema filetype
       output_filetype: FileType
           output filetype
    """
    printer = params["printer"]
    logger = params["logger"]
    default_output_protocol = params["default_protocol"]
    io_manager = _IoManager(printer=printer, logger=logger)
    schema = Schema()
    io_manager.read_obj(schema, schema_filetype)
    config = Config()
    create_template_from_schema(schema=schema, config=config)
    if output_filetype is None:
        io_manager.dump_obj(config, protocol=default_output_protocol)
    else:
        io_manager.write_obj(config, output_filetype, overwrite=params["force"])


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
    input_filetype = getattr(args, "input_filetype", None)
    schema_filetype = getattr(args, "schema_filetype", None)
    output_filetype = getattr(args, "output_filetype", None)
    validation_filetype = getattr(args, "validation_filetype", None)
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


def main_parse_args(log_stream=sys.stderr, out_stream=sys.stdout, argv=None):  # pylint: disable=too-many-locals
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

    default_verbose_level = 1

    config_class_names = [get_config_class_name(config_class) for config_class in get_config_classes()]

    parser_args = dict(
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    common_parser = argparse.ArgumentParser(
        add_help=False,
        **parser_args)

    common_parser.add_argument("--verbose", "-v",
                               dest="verbose_level",
                               action="count",
                               default=default_verbose_level,
                               help="increase verbosity")

    common_parser.add_argument("--quiet", "-q",
                               dest="verbose_level",
                               action="store_const",
                               const=0,
                               default=default_verbose_level,
                               help="quiet mode (only errors are shown)")

    common_parser.add_argument("--debug",
                               action="store_true",
                               default=False,
                               help="debug mode")

    common_parser.add_argument("--force", "-f",
                               action="store_true",
                               default=False,
                               help="force overwriting existing output files")

    common_parser.add_argument("--version",
                               action="version",
                               version="%(prog)s {}".format(VERSION),
                               help="show version")

    top_level_description = """\
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

    top_level_parser = argparse.ArgumentParser(
        "zirkon",
        parents=(common_parser,),
        description=top_level_description,
        **parser_args)

    subparsers = top_level_parser.add_subparsers()

    list_parser = subparsers.add_parser(
        "list",
        parents=(common_parser,),
        description="""Lists all the available config and schema files.""",
        **parser_args)

    list_parser.set_defaults(
        function=list_files,
        function_args=("config_dirs", "schema_dirs"))

    read_parser = subparsers.add_parser(
        "read",
        parents=(common_parser,),
        description="""Reads a config file.""",
        **parser_args)

    read_parser.set_defaults(
        function=read_config,
        function_args=("defaults", "input_filetype", "schema_filetype",
                       "output_filetype", "validation_filetype"))

    create_parser = subparsers.add_parser(
        "create",
        parents=(common_parser,),
        description="""Creates a config file from a schema.""",
        **parser_args)

    create_parser.set_defaults(
        function=create_config,
        function_args=("schema_filetype", "output_filetype"))

    for parser in (read_parser,):
        parser.add_argument("--input", "-i",
                            dest="input_filetype",
                            metavar="IC",
                            default=None,
                            required=True,
                            type=str,
                            help="input file")

    schema_required = {}
    schema_required[read_parser] = False
    schema_required[create_parser] = True

    for parser in read_parser, create_parser:
        parser.add_argument("--defaults", "-d",
                            metavar="D",
                            choices=tuple(_DEFAULTS.keys()),
                            default='False',
                            help="set defaults mode")

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
                            required=schema_required[parser],
                            type=str,
                            help="schema input file")

    for parser in (read_parser,):
        parser.add_argument("--validation", "-V",
                            dest="validation_filetype",
                            metavar="FILE",
                            default=None,
                            type=str,
                            help="validation output file")

    for parser in list_parser, read_parser, create_parser:
        parser.add_argument("--config-dir", "-cd",
                            dest="config_dirs",
                            metavar="CD",
                            action="append",
                            default=[],
                            type=str,
                            help="add config dir")

        parser.add_argument("--schema-dir", "-sd",
                            dest="schema_dirs",
                            metavar="SD",
                            action="append",
                            default=[],
                            type=str,
                            help="add config dir")

    args = top_level_parser.parse_args(argv)

    logger = _create_logger(log_stream, args.verbose_level)
    printer = lambda x: print(x, file=out_stream, flush=True)

    converter_d = {
        "input_filetype": _input_filetype,
        "schema_filetype": _input_schema_filetype,
        "output_filetype": _output_filetype,
        "validation_filetype": _validation_filetype,
    }

    for key, converter in converter_d.items():
        if hasattr(args, key):
            setattr(args, key, converter(logger=logger, filearg=getattr(args, key)))

    _validate_args(logger, args)

    for key, _ in converter_d.items():
        if hasattr(args, key):
            logger.debug("%(20)s: %s", key, getattr(args, key))
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

    function = args.function
    function_args = {}
    for function_arg in args.function_args:
        function_args[function_arg] = getattr(args, function_arg)

    params = {}
    params["printer"] = printer
    params["logger"] = logger
    params["default_protocol"] = "zirkon"
    for key in "force", "debug":
        params[key] = getattr(args, key)

    return function(params=params, **function_args)
