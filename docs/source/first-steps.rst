.. _first-steps:

.. include:: macros.txt

=============
 First steps
=============

.. contents::
    :local:
    :depth: 2

Creating a Config
=================

Creating a |Config| object is easy:

 >>> from zirkon import Config
 >>> config = Config()

An initializer mapping can be passed:

 >>> config = Config({'a': 10})
 >>> config.dump()
 a = 10

All the configuration data are kept in a newly created |OrderedDict|:

 >>> config.dictionary
 OrderedDict([('a', 10)])

This dictionary can be passed during construction; in this case, all the dictionary content is loaded:

 >>> import collections
 >>> from zirkon import Config
 >>> dictionary = collections.OrderedDict()
 >>> dictionary['x'] = 10
 >>> dictionary['y'] = 10
 >>> init = {'a': 20, 'y': 30}
 >>> config = Config(init, dictionary=dictionary)
 >>> print(config['x'])  # from dictionary
 10
 >>> print(config['y'])  # from init
 30
 >>> print(config['a'])  # from init
 20
 >>>

Accessing the Config content
============================

The |Config| is a dict-like object, with some restrictions:
* keys must be strings representing valid python identifiers (for instance, ``10``, ``c.x``, ``9c`` are all invalid keys)
* values can be

  - scalars of type ``int``, ``float``, ``str``, ``bool`` or ``NoneType``;
  - a ``list`` of scalars;
  - a ``tuple`` of scalars;

 >>> config = Config()
 >>> config['a'] = 10
 >>> config['l'] = [1, 2, 'x']

Setting a dict-like value is also possible, but in this case a subsection, and not an option, is added:

 >>> config['sub'] = {}  # empty subsection added

If the dict-like object is not empty, its content is added to the subsection:

 >>> config['sub']['subsub'] = {'a': 1}
 >>> print(config['sub']['subsub']['a'])
 1
 >>>

The actual type of the dictionary is not significant [#fn0]_: the subsection is always stored using the same *dict* class of the root *dictionary*.

 >>> type(config['sub'].dictionary)
 <class 'collections.OrderedDict'>

Storing/loading the Config
==========================

It is possible to store/load the |Config| object to/from strings, streams or files. All the store/load functions accept a :py:attr:`protocol` argument, which is the name of an available serialization protocol:

 >>> s_config = config.to_string(protocol="configobj")
 >>> print("{}".format(s_config), end='')
 a = 10
 l = [1, 2, 'x']
 [sub]
     [[subsub]]
         a = 1
 >>> config2 = config.from_string(s_config, protocol="configobj")
 >>> print(config2 == config)
 True
 >>>

The :py:meth:`zirkon.Config.to_stream`, :py:meth:`zirkon.Config.from_stream` methods allow serialization to/from a stream; the :py:meth:`zirkon.Config.to_file`, :py:meth:`zirkon.Config.from_file` methods allow serialization to/from a file. The :py:meth:`zirkon.Config.write` and :py:meth:`zirkon.Config.read` methods behaves like :py:meth:`zirkon.Config.to_file`, :py:meth:`zirkon.Config.from_file`.

 >>> import tempfile
 >>> with tempfile.NamedTemporaryFile() as fstream:
 ...     _ = config.to_file(fstream.name, "configobj")
 ...     config2 = Config.from_file(fstream.name, "configobj")
 ...     config3 = Config()
 ...     config3.read(fstream.name, protocol="configobj")
 >>> print(config2 == config)
 True
 >>> print(config3 == config)
 True

Finally, the :py:meth:`zirkon.Config.dump(stream=None, protocol="zirkon")` method is based on :py:meth:`zirkon.Config.to_stream` (if :py:attr:`stream` is *None*, it is set to *sys.stdout*).

 >>> config.dump()
 a = 10
 l = [1, 2, 'x']
 [sub]
     [subsub]
         a = 1
 >>>

The list of available serialization protocols is:

 >>> from zirkon.filetype import get_protocols
 >>> for protocol in get_protocols():
 ...     print(protocol)
 zirkon
 configobj
 json
 pickle
 >>>


Creating a Schema
=================

The |Schema| class is a special |Config| whose values can only be |Validator| objects. A Validator object is used to validate a key/value pair. There are many predefined Validator classes; each class can accept some attributes. For instance:

 >>> from zirkon import Schema
 >>> from zirkon.validator import Int
 >>> schema = Schema()
 >>> schema['a'] = Int(default=10, min=3, max=100)
 >>>
 
These :py:meth:`zirkon.Schema.validate(config, raise_on_error=False)` method can be used to validate a Config object. In this example, :py:attr:`schema` simply requires that ``config['a']`` is an integer in the range *[3...100]*. The result is a |Validation| object, i.e. a special Config accepting only |OptionValidationError| instances as values (these are exceptions representing a specific validation error for a key):

 >>> config = Config()
 >>> config['a'] = 23
 >>> validation = schema.validate(config)
 >>> validation.dump()  # Validation object is empty!
 >>> print(config['a'])
 23
 >>>

In this case all is fine, since, ``config`` has a valid integer value for *a*.

Since a *default* value has been provided to the |Int| validator*, it is acceptable that ``config`` do not have the *a* key: in this case, it is added with the default value *10*:

 >>> config = Config()
 >>> validation = schema.validate(config)
 >>> assert not validation  # no errors!
 >>> print(config['a'])
 10
 >>>

The :ref:`validation` guide lists all the svailable validators and their arguments.

Validation errors
-----------------

By default, validation errors are not raised: they are stored on the |Validation| object:

 >>> config = Config()
 >>> config['a'] = "abc"
 >>> validation = schema.validate(config)
 >>> validation.dump()
 a = InvalidTypeError("a='abc': invalid type str - expected type is int")
 >>> config.dump()
 a = 'abc'
 >>>

The :py:meth:`zirkon.Schema.validate` method accepts the :py:attr:`raise_on_error` boolean attribute, which is *False* by default; if *True*, the first validation error is raised.

 >>> from zirkon.validator.error import InvalidTypeError
 >>> try:
 ...     validation = schema.validate(config, raise_on_error=True)
 ... except InvalidTypeError:
 ...     print("type error!")
 type error!
 >>> validation.dump()
 a = InvalidTypeError("a='abc': invalid type str - expected type is int")
 >>> config.dump()
 a = 'abc'
 >>>

In this case, only the first error can be detected.

Dealing with unexpected options
-------------------------------

The *unexpected_option_validator* *Schema* attribute can be set to specify how to threat unexpected options, i.e. options found in the *config* and not defined in the *schema*. It is possible to change this validator; interesting alternatives are:

* |Complain|: this is the default: an |UnexpectedOptionError| validation error is produced:

     >>> config = Config()
     >>> config['u'] = 0.35
     >>> config.dump()
     u = 0.35
     >>> validation = schema.validate(config)
     >>> validation.dump()
     u = UnexpectedOptionError('u=0.35: unexpected option')
     >>>

  Notice that the option is not removed:

     >>> config['u']
     0.35
     >>>

* |Ignore|: the unexpected option is ignored and left in the config;

     >>> from zirkon.validator import Ignore
     >>> schema.unexpected_option_validator = Ignore()
     >>> validation = schema.validate(config)
     >>> validation.dump()  # no errors

  The unexpected option is still there:

     >>> config['u']
     0.35
     >>>

* |Remove|: the unexpected option is removed;

     >>> from zirkon.validator import Remove
     >>> schema.unexpected_option_validator = Remove()
     >>> validation = schema.validate(config)
     >>> validation.dump()  # no errors

  The unexpected option has been removed:

     >>> 'u' in config
     False
     >>>

Anyway, any othe validator can be used.

The Config schema attibute
==========================

A |Config| instance can be initialized with a schema attribute; the schema is then used for automatic validation during load/store, or when requested:

 >>> schema = Schema()
 >>> schema['x'] = Int(min=30)
 >>> schema['y'] = Int(max=2)
 >>> schema['z'] = Int(default=3)
 >>> config = Config(schema=schema, validate=False)
 >>> config['x'] = 10
 >>> config['y'] = 10
 >>> validation = config.self_validate(raise_on_error=False)
 >>> validation.dump()
 x = MinValueError('x=10: value is lower than min 30')
 y = MaxValueError('y=10: value is greater than max 2')

The :py:meth:`zirkon.Config.self_validate` method is automatically called by all the *store/load* methods, with ``raise_on_error=True``; in case of errors, a |ConfigValidationError| exception is raised. This exception has a :py:attr:`validation` attribute containing all the validation errors:
 
 >>> from zirkon import ConfigValidationError
 >>> try:
 ...     config.dump()
 ... except ConfigValidationError as err:
 ...     print("config validation error:")
 ...     err.validation.dump()
 config validation error:
 x = MinValueError('x=10: value is lower than min 30')
 y = MaxValueError('y=10: value is greater than max 2')
 >>>

The Config defaults
===================

The *defaults* is a separate, memory-only storage for default values. It's main purpose is to contain default values set by validation; normally it's preferrable to explicitly store in config files only required values, since defaults depend on the schema and are already stored in it.
Defaults can be used also for dependent values, i.e. options whose value depend on other options through some expression like ``ROOT["x"] * ROOT["y"]``; it's worthelss to store this values, since they must be computed at any access.

The :py:attr:`defaults` argument of the |Config| class can be used to pass a specific defaults object; it can be another config, or any mapping. It can also be shared between configs:

 >>> from zirkon import ROOT
 >>> defaults = Config()
 >>> defaults["y"] = ROOT["x"] * 10

 >>> config1 = Config(defaults=defaults)
 >>> config1["x"] = 3
 >>> config2 = Config(defaults=defaults)
 >>> config2["x"] = 7
 >>> config1["y"]
 30
 >>> config2["y"]
 70

The :py:meth:`zirkon.Config.set_defaults` method can be used to add default options or sections:

 >>> config = Config()
 >>> config['z'] = 100
 >>> config.set_defaults(a=10)
 >>> config.set_defaults(sub={'x': 1})

Only standard values are serialized:

 >>> config.dump()
 z = 100

Defaults can be retrieved:

 >>> config.defaults.dump()
 a = 10
 [sub]
     x = 1

The :py:meth:`zirkon.Config.set_defaults` method is a shorthand for explicitly adding options to the :py:attr:`defaults` attribute:

 >>> config.defaults["g"] = 9.8
 >>> config["g"]
 9.8

Anyway, if defaults are disabled, the :py:meth:`zirkon.Config.set_defaults` still works, and it behaves like normal key setting:

 >>> config = Config(defaults=None)
 >>> config.set_defaults(a=1)
 >>> config.dump()
 a = 1

Schema and defaults
-------------------

By default, during validation default values are added to the config's *defaults*. This can be disabled using the schema parameter ``use_defaults=False``:

 >>> schema = Schema(use_defaults=False)
 >>> schema["x"] = Int(default=10)
 >>> config = Config()
 >>> validation = schema.validate(config)
 >>> config.dump()
 x = 10

In this case, the ``x = 10`` option has been added as standard option, and is so serialized.

.. rubric:: Footnotes

.. [#fn0] Nevertheless, consider that the internal dictionary is by default an |OrderedDict|, so, if the subsection content is added using a standard unordered *dict*, its ordering is abritrary.
