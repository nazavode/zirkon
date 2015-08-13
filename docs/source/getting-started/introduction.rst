.. _intro:

========================
 Introduction to Daikon
========================

.. contents::
    :local:
    :depth: 1

What is Daikon
==============

.. sidebar:: Requirements
    :subtitle: Daikon requires only

    - Python 3.4

Daikon is a python library to manage configuration information. It implements multiple serialization protocols, generic validation and advanced value interpolation.
Moreover, it has been designed to fully delegate the management of the configuration data to an external dictionary-like object, so that it is possible, for instance, to use a persistent dictionary like a ``shelve.Shelf``.


Daikon features
===============

Simplicity
----------

Daikon Config objects behaves like traditional mappings:

 >>> from daikon.config import Config
 >>> config = Config()
 >>> config['x'] = 10
 >>> config['subsection'] = {}
 >>> config['subsection']['y'] = "alpha"
 >>> config.dump()
 x = 10
 [subsection]
     y = 'alpha'
 >>>

Flexibility
-----------

Daikon Config objects internally store information in a dict-like
object, by default ad OrderedDict. It is possible to change this
internal dictionary and to use, for instance, a ``shelve`` in order
to add persistency.

Multiple file serializations
----------------------------

Daikon supports multiple serialization methods; currently four are
available:

 +---------+--------+-----------------------------------------------------+
 |Protocol |text/raw|description                                          |
 +=========+========+=====================================================+
 |daikon   |text    |the native protocol; it implements a nested INI file |
 +---------+--------+-----------------------------------------------------+
 |configobj|raw     |compatible with ConfigObj using the ``unrepr`` option|
 |         |        |see http://www.voidspace.org.uk/python/configobj.html|
 +---------+--------+-----------------------------------------------------+
 |json     |text    |JSON serialization                                   |
 +---------+--------+-----------------------------------------------------+
 |pickle   |text    |pickle serialization                                 |
 +---------+--------+-----------------------------------------------------+

Validation
----------
    
Daikon supports validation of Config objects to a Schema. A Schema
is simply a special Config having Validators as values:

 >>> from daikon.schema import Schema
 >>> from daikon.validator import Int, Str, Float
 >>> schema = Schema()
 >>> schema['x'] = Int(min=1)
 >>> schema['subsection'] = {}
 >>> schema['subsection']['y'] = Str(min_len=6)
 >>> schema['subsection']['w'] = Float()
 >>> schema.dump()
 x = Int(min=1)
 [subsection]
     y = Str(min_len=6)
     w = Float()
 >>>

The validation result itself is a Config object having KeyValidationErrors
as values.

 >>> validation = schema.validate(config)
 >>> validation.dump()
 [subsection]
     y = MinLengthError(KeyValue('subsection.y', 'alpha'), 'value has length 5 than is lower than min_len 6')
     w = MissingRequiredParameterError(KeyValue('subsection.w', None, defined=False), 'required value is missing')
 >>>

There list of available Validators can be easily extended.

Advanced value interpolation
----------------------------

Daikon supports advanced value interpolation: key/values precedently stored in 
the Config object can be accessed and used in complex expressions to set new values.
For instance:

 >>> config_s = """\
 ... x = 10
 ... y = ROOT['x'] * 4
 ... """
 >>> config = Config.from_string(config_s, protocol="daikon")
 >>> config.dump()
 x = 10
 y = 40
 >>>

Moreover, this can be used in validators:

 >>> schema_s = """\
 ... x = Int()
 ... y = Int(min=ROOT['x'] // 2)
 ... z = Int(default=ROOT['x'] * ROOT['y'])
 ... """
 >>> schema = Schema.from_string(schema_s, protocol="daikon")
 >>> validation = schema.validate(config)
 >>> validation.dump()
 >>> config.dump()
 x = 10
 y = 40
 z = 400
 >>>
