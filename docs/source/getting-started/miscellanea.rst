.. _intro:

=============
 Miscellanea
=============

.. contents::

How configuration data are stored
=================================

Daikon Config has a dictionary interface:
 >>> from daikon.config import Config
 >>> config = Config()
 >>> config['x'] = 10
 >>> config['y'] = (2, 3, 4)
 >>> config.dump()
 x = 10
 y = (2, 3, 4)
 >>>

Daikon configuration is structured in sections; a Section is a mapping, with the following constraints:
* keys must be string representing valid python identifiers
* value type can be any of int, float, str, bool, list, tuple or dictionaries

If a key is a dictionary, a subsection is created; so, sections can be nested:

 >>> config['sub'] = {}
 >>> config['sub']['filename'] = "x.dat"
 >>> config['sub']['data'] = {'max': 100}
 >>> config['sub']['alpha'] = 1.05
 >>> config.dump()
 x = 10
 y = (2, 3, 4)
 [sub]
    filename = 'x.dat'
    [data]
        max = 100
    alpha = 1.05
 >>>
 

Daikon configuration data are internally stored on a dict-like object, by default an OrderedDict. Anyway, this dictionary can be changed. For instance, you can use a persistent dictionary (automatically saved onto a database) to store internal data. If the internal dictionary dos not support nesting, the FlatMap class can be used. A FlatMap mapping wraps a flatten dictionary and implements a nested dictionary interface on it.

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
 

Reading/writing configuration files
===================================

Daikon config files can be read/written from/to strings, streams or files. There are four available protocols:
Four serialization methods (protocols) are currently implemented:
* daikon: the native serialization
* configobj: the ConfigObj serialization, see http://www.voidspace.org.uk/python/configobj.html
* json: JSON serialization
* pickle: pickle-based serialization (not human-readable!)

 >>> with tempfile.TemporaryDirectory() as tdir:
 ...     tfile = os.path.join(tdir, 'x.json')
 ...     config = Config()
 ...     config['sub'] = {'a': 1}
 ...     config['w'] = 10
 ...     config.write(tfile, protocol="json")
 ...     config2 = Config()
 ...     config2.read(tfile, protocol="json")
 ...     assert config == config2
 >>>

How validation works
====================

Daikon supports validation. A Schema object defines a validation schema for any Config (or Section). A Schema is a Config accepting Validator objects as values; standard valid validators are:

- ``Int([default=...], [min=...], [max=...])``
  an integer value; 
- ``IntList([default=...], [min_len=...], [max_len=...], [item_min=...], [item_max=...])``
  an integer list; 
- ``IntTuple([default=...], [min_len=...], [max_len=...], [item_min=...], [item_max=...])``
  an integer tuple; 
- ``IntOption(values=(...), [default=...])``
  an integer option; 
- ``Float([default=...], [min=...], [max=...])``
  an float value; 
- ``FloatList([default=...], [min_len=...], [max_len=...], [item_min=...], [item_max=...])``
  an float list; 
- ``FloatTuple([default=...], [min_len=...], [max_len=...], [item_min=...], [item_max=...])``
  an float tuple; 
- ``FloatOption(values=(...), [default=...])``
  an float option; 
- ``Str([default=...], [min_len=...], [max_len=...])``
  a string; 
- ``StrList([default=...], [min_len=...], [max_len=...], [item_min_len=...], [item_max_len=...])``
  a string list; 
- ``StrTuple([default=...], [min_len=...], [max_len=...], [item_min_len=...], [item_max_len=...])``
  a string tuple; 
- ``StrOption(values=(...), [default=...])``
  a string option; 
- ``Bool([default=...])``
  a boolean value;
- ``BoolList([default=...], [min_len=...], [max_len=...])``
  a boolean list;
- ``BoolTuple([default=...], [min_len=...], [max_len=...])``
  a boolean tuple;
- ``BoolOption(values=(...), [default=...])``
  a boolean option.

Additional validators can be used to manage keys unexpected keys found in validated section:
- ``Complain()``
  unexpected keys raise an UnexpectedOptionError (the default behaviour);
- ``Remove()``
  unexpected keys are removed;
- ``Ignore()``
  unexpected keys are silently ignored.

Validation is performed by the Schema ``validate`` method; unless ``rase_on_error`` argument is set to True, it does not raise errors, that are instead stored on a Validation object and then returned to the caller. 

Validation changes the validated config; it can:
- add keys (for missing keys with a default in the Schema)
- change values
- remove keys

By default the 

>>> from daikon.schema import Schema
>>> from daikon.validator import Int, Float, Str
>>> schema = Schema()
>>> schema['a'] = Int(default=10)
>>> schema['b'] = Float(default=1.02)
>>> schema['sub'] = {}
>>> schema['sub']['c'] = Str(min_len=2)
>>> schema['d'] = Float()
>>> 
>>> config = Config()
>>> config['a'] = 9
>>> config['w'] = 1.1
>>> config['sub'] = {'c': 'x'}
>>> validation = schema.validate(config)
>>> validation.dump()
d = MissingRequiredOptionError(KeyValue('d', None, defined=False), 'required value is missing')
w = UnexpectedOptionError(KeyValue('w', 1.1), "unexpected option 'w'")
[sub]
    c = MinLengthError(KeyValue('sub.c', 'x'), 'value has length 1 than is lower than min_len 2')

>>> print(config['b'])
1.02
>>> config['sub']['c'] = 'xxx'
>>> config['d'] = 1.18
>>> del config['w']
>>> validation = schema.validate(config)
>>> validation.dump()
>>>

A schema can be added to the Config object; in this case it is automatically called on load/write, and it can be done by calling the ``Config.self_validate`` method:

>>> config2 = Config(schema=schema, init=config) # automatic validation
>>> validation = config2.self_validate(raise_on_error=True)
>>> assert not validation
