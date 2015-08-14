.. _intro:

==================
 The Config class
==================

The *Config* class behaves like a dict: it has ``__getitem__``, ``__setitem__`` and ``__delitem__`` methods:

 >>> from daikon.config import Config
 >>> config = Config()
 >>> config['x'] = 10
 >>> print(config['x'])
 10
 >>> len(config)
 1
 >>> del config['x']
 >>> len(config)
 0
 >>> config['a'] = 1
 >>> config['b'] = 2
 >>> for key in config.keys():
 ...     print(key)
 a
 b
 >>> for value in config.values():
 ...     print(value)
 1
 2
 >>> for key, value in config.items():
 ...     print(key, value)
 a 1
 b 2

It can be initialized from a dict-like object:

 >>> config = Config({'x': 10})
 >>> print(config['x'])
 10

It accepts only values of the following types:
* scalars *(int, float, bool, str)*
* list of scalars
* tuple of scalars
* the object None

It accepts also dict-like objects as values: in this case, a subsection is created:

 >>> config['sub'] = {'w': 100}
 >>> type(config['sub'])
 <class 'daikon.section.Section'>

Serialization/deserialization methods
-------------------------------------

The config class provides serialization/deserialization methods. Config object can be serialized to/deserialized from a string, a stream or a file, with changeable serialization protocols:

 >>> config = Config({'x': 10})
 >>> config['sub'] = {'a': 20}
 >>> config_s = config.to_string(protocol="daikon")
 >>> print(config_s)
 x = 10
 [sub]
     a = 20
 >>> config2 = Config.from_string(config_s, protocol="daikon")
 >>> print(config == config2)
 True

 >>> config_json = config.to_string(protocol="json")
 >>> print(config_json)
 {
     "x": 10,
     "sub": {
         "a": 20
     }
 }
 >>> config2 = Config.from_string(config_json, protocol="json")
 >>> print(config == config2)
 True

Similarly:
* ``to_stream`` and ``from_stream`` can be used to write to/read from a stream;
* ``to_file`` and ``from_file`` can be used to write to/read from a file.

The ``dump(stream=None, protocol="daikon")`` method is based on ``to_stream``; by default, *stream* is *sys.stdout*.

The schema and validate attributes
----------------------------------

It is possible to attach a *schema* to a newly created *config*:

 >>> from daikon.schema import Schema
 >>> from daikon.validator import Int
 >>> schema = Schema({'x': Int()})
 >>> config = Config({'x': 10}, schema=schema)

Since the *schema* has been provided, the *config* object is immediately validated. In case of errors, a ``ConfigValidationError`` exception is raised; this exception contains a *validation* attribute referring to the validation result:

 >>> from daikon.config import ConfigValidationError
 >>> try:
 ...     config = Config({'x': 6.5}, schema=schema)
 ... except ConfigValidationError as err:
 ...     err.validation.dump()
 x = InvalidTypeError('x=6.5: invalid type float - expected type is int')
 >>>

When a *Config* object has a *schema*, it is automatically validated when serialized/deserialized:

 >>> config = Config({'x': 10}, schema=schema)
 >>> config['x'] = 'abc'  # no validation
 >>> try:
 ...     config.dump()  # validation
 ... except ConfigValidationError as err:
 ...     err.validation.dump()
 x = InvalidTypeError("x='abc': invalid type str - expected type is int")

Validation can be manually invoked by means of the ``self_validate`` method:

 >>> config = Config({'x': 10}, schema=schema)
 >>> config['x'] = 'abc'  # no validation
 >>> validation = config.self_validate(raise_on_error=False)
 >>> validation.dump()
 x = InvalidTypeError("x='abc': invalid type str - expected type is int")

It is possible to avoid validation during ``__init__``:

 >>> config = Config(schema=schema, validate=False)

Even if *config* does not conform to the *schema*, validation is not performed during initialization, since *validate=False* has been provided. Nevertheless, the *schema* is attached to the *config* and will be used for future self-validations.

It is also possible to attach or detach a *schema* at any moment:

 >>> config.set_schema(None)  # detach schema from config
 >>> schema2 = Schema({'x': Int(min=10)})
 >>> config.set_schema(schema2, validate=False)

The latter statement attaches *schema2* to *config*, but validation is not immediately performed.

The dictionary attribute
------------------------

The *Config* class is designed to delegate the storage of the information to an underlayinig dictionary object. By default, this underlaying dictionary is an ``OrderedDict``.

 >>> from collections import OrderedDict
 >>> container = OrderedDict()
 >>> container['x'] = 10
 >>> container['y'] = 20

 >>> config = Config(dictionary=container)
 >>> config.dump()
 x = 10
 y = 20
 >>> config['sub'] = {'a': 3}
 >>> container
 OrderedDict([('x', 10), ('y', 20), ('sub', OrderedDict([('a', 3)]))])

Notice that the added subsection is an *OrderedDict* too, not a *dict*: when a subsection is added, *Config* uses the same class of its dictionary.

The main reason for that is to allow to change the information container; for instance, it is possible to use a ``shelve.Shelf`` or some other persistent dictionary:

 >>> import os
 >>> import shelve
 >>> import tempfile
 >>> with tempfile.TemporaryDirectory() as tdir:
 ...     tfile = os.path.join(tdir, 'x.shelf')
 ...     shelf = shelve.open(tfile)
 ...     from daikon.toolbox.flatmap import FlatMap
 ...     flatshelf = FlatMap(dictionary=shelf)
 ...     config = Config(dictionary=flatshelf)
 ...     config['sub'] = {}
 ...     config['sub']['filename'] = "x.dat"
 ...     config['sub']['data'] = {'max': 100}
 ...     config['sub']['alpha'] = 1.05
 ...     print(config['sub']['data']['max'])
 100
 >>>

In this example, the ``shelve.Shelf`` object is wrapped by a ``FlatMap`` object, that implements a nested dictionary over a flat dictionary; indeed, the ``shelve.Shelf`` object does not support nesting.

The FlatMap utility class
-------------------------

The following example shows as ``FlatMap`` implements a nested dictionary interface over a flat dictionary:

 >>> container = OrderedDict()
 >>> flatdict = FlatMap(dictionary=container)
 >>> flatdict['x'] = 10
 >>> flatdict['sub'] = {'a': 1}
 >>> container
 OrderedDict([('x', 10), ('sub.', None), ('sub.a', 1)])

