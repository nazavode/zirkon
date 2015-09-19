.. _intro-introduction:

.. py:currentmodule:: zirkon.config

.. |Config| replace:: :py:class:`Config`

.. py:currentmodule:: zirkon.schema

.. |Schema| replace:: :py:class:`Schema`

.. py:currentmodule:: zirkon.validator.validator

.. |Validator| replace:: :py:class:`Validator`

.. py:currentmodule:: zirkon.validator.error

.. |OptionValidationError| replace:: :py:class:`OptionValidationError`

.. _ConfigObj: http://www.voidspace.org.uk/python/configobj.html

.. |ConfigObj| replace:: ConfigObj_

.. |OrderedDict| replace:: :py:class:`OrderedDict`

========================
 Introduction to Zirkon
========================

.. contents::
    :local:
    :depth: 1

What is Zirkon
==============

.. sidebar:: Requirements
    :subtitle: Zirkon requires only

    - Python >= 3.4

Zirkon is a python library to manage configuration information. It implements `multiple serialization protocols`_, `option validation`_, `default values`_ and `macros`_.
Moreover, it has been designed to fully delegate the management of the configuration data to an external dictionary-like object, so that it is possible, for instance, to use a persistent dictionary like a :py:mod:`shelve`.

Zirkon features
===============

Simplicity
----------

Zirkon |Config| objects behaves like traditional mappings:

 >>> from zirkon.config import Config
 >>> config = Config()
 >>> config['x'] = 10
 >>> config['y'] = 20

When a dictionary is added, it becomes a subsection:

 >>> config['subsection'] = {}
 >>> config['subsection']['y'] = "alpha"
 >>> print(config['subsection']['y'])
 alpha

Subsections can be nested at any level:

 >>> config['subsection'] = {'sub2': {'sub3': {'a' : 3}}}
 >>> print(config['subsection']['sub2']['sub3']['a'])
 3

Flexibility
-----------

Zirkon |Config| objects internally store information in a dict-like
object, by default an |OrderedDict|:

 >>> config = Config({'x': 1})
 >>> config['y'] = 2
 >>> config.dictionary
 OrderedDict([('x', 1), ('y', 2)])

It is possible to explicitly set this internal dictionary:

 >>> dct = {}
 >>> config = Config(dictionary=dct)
 >>> config['x'] = 1
 >>> dct
 {'x': 1}

.. _serialization protocols:

Multiple serialization protocols
--------------------------------

Zirkon supports multiple serialization protocols; currently four are
available:

 +---------+--------+-----------------------------------------------------------------+
 |Protocol |text/raw|description                                                      |
 +=========+========+=================================================================+
 |zirkon   |text    |the native protocol; it implements a nested INI file             |
 +---------+--------+-----------------------------------------------------------------+
 |configobj|raw     |partially compatible with |ConfigObj| format using the           |
 |         |        |``unrepr`` option                                                |
 +---------+--------+-----------------------------------------------------------------+
 |json     |text    |JSON serialization                                               |
 +---------+--------+-----------------------------------------------------------------+
 |pickle   |text    |pickle serialization                                             |
 +---------+--------+-----------------------------------------------------------------+

For a description of the serialization format, see :ref:`serialization formats`.

Some examples:

 >>> config = Config()
 >>> config["x"] = 10
 >>> config["subsection"] = {"y": "alpha"}
 >>> print(config.to_string(protocol="zirkon"), end='')
 x = 10
 [subsection]
     y = 'alpha'
 >>> print(config.to_string(protocol="json"), end='')
 {
     "x": 10,
     "subsection": {
         "y": "alpha"
     }
 }

The :py:meth:`Config.dump()` method is a shorthand for :py:meth:`Config.to_stream(sys.stdout, protocol="zirkon")`:

 >>> config.dump()
 x = 10
 [subsection]
     y = 'alpha'

.. _option validation:

Validation
----------
    
Zirkon allows to define a |Schema| for the validation of |Config| objects. A Schema
is simply a special Config having |Validator| objects as values:

 >>> from zirkon.schema import Schema
 >>> from zirkon.validator import Int, Str, Float
 >>> schema = Schema()
 >>> schema['x'] = Int(min=1)
 >>> schema['y'] = Int(default=2)
 >>> schema['subsection'] = {}
 >>> schema['subsection']['y'] = Str(min_len=6)
 >>> schema['subsection']['w'] = Float()

The validation result itself is a Config object having |OptionValidationError| objects
as values:

 >>> validation = schema.validate(config)
 >>> validation.dump()
 [subsection]
     y = MinLengthError("subsection.y='alpha': length 5 is lower than min_len 6")
     w = MissingRequiredOptionError('subsection.w: required value is missing')

Since the validator for *y* sets a default value and the key is missing from config, it is added:

 >>> print(config['y'])
 2

There list of available validators can be easily extended.

.. _default values:

Default values
--------------

Zirkon supports default values. Defaults are stored in a separated space, not in the dictionary, and they are not serialized; nevertheless they can be accessed as normal values:

 >>> defaults = {'x': 1.0, 'y': 2.0}
 >>> config = Config(defaults=defaults)
 >>> print(config['x'], config['y'])
 1.0 2.0

Default values can be added:

 >>> config.set_defaults(z=3.0)
 >>> print(config['z'])
 3.0

They can be overwritten by standard values:

 >>> config['x'] = 100
 >>> print(config['x'])
 100
 >>> del config['x']
 >>> print(config['x'])
 1.0

The main purpose for defaults is to store the default values set during validation:

 >>> config = Config(defaults={})
 >>> schema = Schema()
 >>> schema['t'] = Int(default=789)
 >>> validation = schema.validate(config)
 >>> config.dump()
 >>> print(config['t'])
 789

Defaults can directly be accessed:

 >>> config.defaults.dump()
 t = 789
 
It is possible to disable defaults by simply setting defaults to *None*:

 >>> config = Config(defaults=None)
 >>> validation = schema.validate(config)
 >>> config.dump()
 t = 789

In this case the default value set during the validation is stored in the dictionary as a standard value.

.. _macros:

Macros
------

Zirkon supports an advanced version of value interpolation: it is possible to set new options by means of macro expressions involving other option values. For instance:

 >>> from zirkon.config import ROOT
 >>> config = Config()
 >>> config['x'] = 2
 >>> config['y'] = ROOT['x'] * 4

Here ``ROOT`` is a reference to the *config* itself. Notice that the macro expression ``ROOT['x'] * 4`` is not immediately evaluated: it will be evaluated each time *y* is accessed:

 >>> print(config['y'])
 8
 >>> config['x'] = 10
 >>> print(config['y'])
 40
 >>> config.dump()
 x = 10
 y = ROOT['x'] * 4

Using this feature, values can be set as functions of other values.

Moreover, this can be used in validators:

 >>> schema_s = """\
 ... x = Int()
 ... y = Int(min=ROOT['x'] * 5)
 ... z = Int(default=ROOT['x'] * ROOT['y'])
 ... """
 >>> schema = Schema.from_string(schema_s, protocol="zirkon")
 >>> validation = schema.validate(config)
 >>> validation.dump()
 y = MinValueError('y=40: value is lower than min 50')
 >>> config.dump()
 x = 10
 y = ROOT['x'] * 4
 >>> print(config['x'], config['y'], config['z'])
 10 40 400

So validation parameters can be tied to particular values found in the validated config.

    .. tip::
       Suppose you want a config with two values: the dimension *N*, which can be 1, 2 or 3, and the *coefficients*, a tuple of *N* floating point values. The schema can be defined as follows:

        >>> from zirkon.validator import FloatTuple
        >>> schema = Schema()
        >>> schema['N'] = Int(min=1, max=3)
        >>> schema['coefficients'] = FloatTuple(min_len=ROOT['N'], max_len=ROOT['N'])
        
Macros can be disabled by setting ``macros=False``:

 >>> config = Config(macros=False)
