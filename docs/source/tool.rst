.. _intro-tool:

=================
 The zirkon tool
=================

.. contents::
    :local:
    :depth: 1

The *zirkon* tool is a simple command line interface allowing to search, read, validate and write config files.

Config/schema relative paths are searched:

* in the current directory;
* in the directories listed in ``os.environ["ZIRKON_CONFIG_DIRS"]``/``os.environ["ZIRKON_SCHEMA_DIRS"]``;
* in the directories specified at command line, option ``--config-dir``/``--schema-dir``.

The list command
================

The *list* subcommand shows all the available files; for each file the command shows:

* the absolute path
* the guessed config class
* the guessed protocol

For instance:

    .. code-block:: bash

       $ zirkon list
       filename                  type   protocol
       ------------------------- ------ --------
       /home/.../x.json          Config json    
       /home/.../x.zirkon        Config zirkon  
       /home/.../x.zirkon-schema Schema zirkon  
       $

The read command
================

The *read* command reads a config file. It can optionally

* validate the read config, if a schema is provided
* write the config file, possibly changing the protocol

The following command reads the *x.zirkon* config file, validates it using the schema read from *x.zirkon-schema*, and
writes the validated config to *x.json*, using the *json* protocol:

    .. code-block:: bash

       $ zirkon read -i x.zirkon -s x.zirkon-schema -o x.zirkon.json
       $
       
Normally the protocol and the config class are deduced from the file name, but they can be provided explicitly:

    .. code-block:: bash

       $ zirkon read -i x.zirkon:zirkon:config
       x = 10
       [sub]
           a = [1, 2, 3]
           s = 'x.dat'
       $

The create command
==================

The *create* command reads a schema and creates a template config file from it. This config file can be written to file:

    .. code-block:: bash

       $ zirkon create -s x.zirkon-schema
       x = '# Float()'
       [sub]
           a = '# FloatList(min_len=3)'
           s = ''
       $
       
