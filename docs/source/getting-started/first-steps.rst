.. _intro:

=============
 First steps
=============

.. contents::
    :local:
    :depth: 2

Creating a Config
=================

The *Config* class has the following signature:

 .. code-block:: python
    
    Config(init=None, *, dictionary=None, schema=None)

where *init* is an optional initialization dict-like object. The *dictionary* attribute, if present, is a dict-like object that can be used to load/store all the configuration data; it does not need to be empty, anyway, if it is not empty, the content is loaded as initial configuration (and then updated with *init*). The *schema* attribute, if present, is a *Schema* object used for validation, as explained below.

 >>> import collections
 >>> from daikon.config import Config
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

The *Config* is a dict-like object, with some restrictions:
* keys must be strings representing valid python identifiers
* values can be
  - scalars of type ``int``, ``float``, ``str``, ``bool`` or ``NoneType``;
  - a ``list`` of scalars;
  - a ``tuple`` of scalars;

 >>> config = Config()
 >>> config['a'] = 10
 >>> config['l'] = [1, 2, 'x']

The *Config* object can contain subsections; in order to have a subsection, you can simply add any dict-like object (the actual dict type is not significant):

 >>> config['sub'] = {}  # empty subsection added

If the dict-like object is not empty, its content is added to the subsection

 >>> config['sub']['subsub'] = {'a': 1}
 >>> print(config['sub']['subsub']['a'])
 1
 >>>

Storing/loading the Config
==========================

It is possible to store/load the *Config* object to/from strings, streams or files. All the store/load functions accept a ``protocol`` argument, which is the name of an available serialization protocol:

 >>> s_config = config.to_string(protocol="configobj")
 >>> print(s_config)
 a = 10
 l = [1, 2, 'x']
 [sub]
    [[subsub]]
        a = 1
 >>> config2 = config.from_string(s_config, protocol="configobj")
 >>> print(config2 == config)
 True
 >>>

The ``to_stream``, ``from_stream`` methods allow serialization to/from a stream; the ``to_file``, ``from_file`` methods allow serialization to/from a file. The ``write`` and ``read`` methods behaves like ``to_file``, ``from_file``.
Finally, the ``dump(stream=None, protocol="daikon")`` method is based on ``to_stream`` (if ``stream`` is ``None``, it is set to ``sys.stdout``).

 >>> config.dump()
 a = 10
 l = [1, 2, 'x']
 [sub]
    [subsub]
        a = 1
 >>>

The list of available serialization protocols is:

 >>> from daikon.toolbox.serializer import Serializer
 >>> for protocol in Serializer.class_dict():
 ...     print(protocol)
 daikon
 configobj
 json
 pickle
 >>>

Creating a Schema
=================

The *Schema* class is a special *Config* whose values can only be *KeyValidator* objects. A *KeyValidator* object is used to validate a key/value pair. There are many predefined *KeyValidator* classes; each class can accept some attributes. For instance:

 >>> from daikon.schema import Schema
 >>> from daikon.validator import Int
 >>> schema = Schema()
 >>> schema['a'] = Int(default=10, min=3, max=100)
 >>>
 
These *Schema.validate(config, raise_on_error=False)* method can be used to validate a *Config* object. In this example, ``schema`` simply requires that ``config['a']`` is an integer in the range *[3...100]*. The result is a ``Validation`` object, i.e. a special *Config* accepting only *KeyValidationError* instances as values (these are exceptions representing a validation error for a key):

 >>> config = Config()
 >>> config['a'] = 23
 >>> validation = schema.validate(config)
 >>> validation.dump()  # Validation object is empty!
 >>> print(config['a'])
 23
 >>>

In this case all is fine, since, *config* has a valid integer value for *a*.

Since a *default* value has been provided to the ``Int`` *KeyValidator*, it is acceptable that ``config`` do not have the *a* key: in this case, it is added with the default value *10*:

 >>> config = Config()
 >>> config.dump()
 >>> validation = schema.validate(config)
 >>> assert not validation
 >>> config.dump()
 a = 10
 >>>

Validation errors
-----------------

By default, validation errors are not raised: they are stored on the ``Validation`` object:

 >>> config = Config()
 >>> config['a'] = "abc"
 >>> validation = schema.validate(config)
 >>> validation.dump()
 a = InvalidTypeError(KeyValue('a', 'abc'), 'invalid type str - expected type is int')
 >>> config.dump()
 a = 'abc'
 >>>

The ``Schema.validate`` method accepts the *raise_on_error* boolean attribute, which is *False* by default; if *True*, the first validation error is raised.

 >>> from daikon.validator.error import InvalidTypeError
 >>> try:
 ...     validation = schema.validate(config, raise_on_error=True)
 ... except InvalidTypeError:
 ...     print("type error!")
 type error!
 >>> validation.dump()
 a = InvalidTypeError(KeyValue('a', 'abc'), 'invalid type str - expected type is int')
 >>> config.dump()
 a = 'abc'
 >>>

In this case, only the first error can be detected.

Dealing with unexpected parameters
----------------------------------

The *unexpected_parameter_validator* *Schema* attribute can be set to specify how to threat unexpected parameters, i.e. keys found in the *config* and not defined in the *schema*. It is possible to change this validator; interesting alternatives are:

* ``daikon.validator.UnexpectedParameter``: this is the default: an ``UnexpectedParameterError`` validation error is produced:

     >>> config = Config()
     >>> config['u'] = 0.35
     >>> config.dump()
     u = 0.35
     >>> validation = schema.validate(config)
     >>> validation.dump()
     u = UnexpectedParameterError(KeyValue('u', 0.35), "unexpected parameter 'u'")
     >>> config.dump()
     u = 0.35
     a = 10
     >>>

* ``daikon.validator.Ignore``: the unexpected parameter is ignored and left in the config;

     >>> from daikon.validator import Ignore
     >>> schema.unexpected_parameter_validator = Ignore()
     >>> config.dump()
     u = 0.35
     a = 10
     >>> validation = schema.validate(config)
     >>> validation.dump()
     >>> config.dump()
     u = 0.35
     a = 10
     >>>

* ``daikon.validator.Remove``: the unexpected parameter is removed;

     >>> from daikon.validator import Remove
     >>> schema.unexpected_parameter_validator = Remove()
     >>> config.dump()
     u = 0.35
     a = 10
     >>> validation = schema.validate(config)
     >>> validation.dump()
     >>> config.dump()
     a = 10
     >>>

Anyway, any othe validator can be used.

The Config schema attibute
==========================

A *Config* instance can be initialized with a schema attribute; the schema is then used for automatic validation during load/store, or when requested:

 >>> schema = Schema()
 >>> schema['x'] = Int(min=30)
 >>> schema['y'] = Int(max=2)
 >>> schema['z'] = Int(default=3)
 >>> config = Config(schema=schema, validate=False)
 >>> config['x'] = 10
 >>> config['y'] = 10
 >>> validation = config.self_validate(raise_on_error=False)
 >>> validation.dump()
 x = MinValueError(KeyValue('x', 10), 'value is lower than min 30')
 y = MaxValueError(KeyValue('y', 10), 'value is greater than max 2')

The ``self_validate`` method is automatically called by all the *store/load* methods, with ``raise_on_error=True``; in case of errors, a *ConfigValidationError* exception is raised. This exception has a ``validation`` attribute containing all the validation errors:
 
 >>> from daikon.config import ConfigValidationError
 >>> try:
 ...     config.dump()
 ... except ConfigValidationError as err:
 ...     print("config validation error:")
 ...     err.validation.dump()
 config validation error:
 x = MinValueError(KeyValue('x', 10), 'value is lower than min 30')
 y = MaxValueError(KeyValue('y', 10), 'value is greater than max 2')
 >>>

