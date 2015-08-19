Zirkon
======
A python configuration library. Zirkon requires python >= 3.4.

.. image:: https://travis-ci.org/simone-campagna/zirkon.svg?branch=master
    :target: https://travis-ci.org/simone-campagna/zirkon

.. image:: https://coveralls.io/repos/simone-campagna/zirkon/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/simone-campagna/zirkon?branch=master

.. image:: https://codeclimate.com/github/simone-campagna/zirkon/badges/gpa.svg
   :target: https://codeclimate.com/github/simone-campagna/zirkon
   :alt: Code Climate

.. image:: https://badge.fury.io/py/zirkon.svg
    :target: http://badge.fury.io/py/zirkon

What is zirkon
--------------

Zirkon is a python library to handle configuration data. It behaves like a dictionary, and supports nested sections:

 >>> from zirkon.config import Config
 >>> config = Config()
 >>> config['num'] = 10
 >>> config['mode'] = 'xy'
 >>> config['sub'] = {'enable': True}
 >>> config['sub']['x'] = 1.5
 >>> config['sub']['y'] = -1.5
 >>> config['name'] = 'alpha'
 >>> config['w'] = 5
 >>> config.dump()
 num = 10
 mode = 'xy'
 [sub]
     enable = True
     x = 1.5
     y = -1.5
 name = 'alpha'
 w = 5



 >>> from zirkon.config import Config
 >>> config = Config()
 >>> config['num'] = 10
 >>> config['mode'] = 'xy'
 >>> config['sub'] = {'enable': True}
 >>> config['sub']['x'] = 1.5
 >>> config['sub']['y'] = -1.5
 >>> config['name'] = 'alpha'
 >>> config['w'] = 5
 >>> config.dump()
 num = 10
 mode = 'xy'
 [sub]
     enable = True
     x = 1.5
     y = -1.5
 name = 'alpha'
 w = 5



 >>> from zirkon.config import Config
 >>> config = Config()
 >>> config['num'] = 10
 >>> config['mode'] = 'xy'
 >>> config['sub'] = {'enable': True}
 >>> config['sub']['x'] = 1.5
 >>> config['sub']['y'] = -1.5
 >>> config['name'] = 'alpha'
 >>> config['w'] = 5
 >>> config.dump()
 num = 10
 mode = 'xy'
 [sub]
     enable = True
     x = 1.5
     y = -1.5
 name = 'alpha'
 w = 5

Multiple serialization protocols
--------------------------------

Zirkon currently supports the following serialization protocols:

 +---------+--------+---------------------------------------------------------------+
 |Protocol |text/raw|description                                                    |
 +=========+========+===============================================================+
 |zirkon   |text    |the native protocol; it implements a nested INI file           |
 +---------+--------+---------------------------------------------------------------+
 |configobj|raw     |partially compatible with ConfigObj using the ``unrepr`` option|
 |         |        |see http://www.voidspace.org.uk/python/configobj.html          |
 +---------+--------+---------------------------------------------------------------+
 |json     |text    |JSON serialization                                             |
 +---------+--------+---------------------------------------------------------------+
 |pickle   |text    |pickle serialization                                           |
 +---------+--------+---------------------------------------------------------------+

Other serialization protocols can be added.

The serialization methods are

 * ``to_string``, ``to_stream``, ``to_file``: write to string/stream/file
 * ``from_string``, ``from_stream``, ``from_file`` (classmethods): build a new *Config* reading content from sring/stream/file
 * ``write``: equivalent to ``to_file``
 * ``read``: replace an existing *Config* object with the content read from file
 * ``dump``: a shorthand for ``to_stream``, where by default *stream=sys.stdout* and *protocol="zirkon"* 

Validation
----------

Zirkon supports validation through a *Schema* object. A *Schema* is a *Config* with *Validator* values:

 >>> from zirkon.schema import Schema
 >>> from zirkon.validator import Int, Str, StrChoice, Float, Bool, FloatList
 >>> schema = Schema()
 >>> schema['num'] = Int(min=0)
 >>> schema['mode'] = StrChoice(choices=("xy", "yx", "xx"))
 >>> schema['sub'] = {}
 >>> schema['sub']['enable'] = Bool()
 >>> schema['sub']['x'] = Float(min=0.0)
 >>> schema['sub']['y'] = Float(min=0.0)
 >>> schema['name'] = Str()
 >>> schema['min_value'] = Int(default=100)
 >>> schema['coeffs'] = FloatList(min_len=1, default=[1.0, 1.0, 1.0])
 >>> validation = schema.validate(config)
 >>> validation.dump()
 w = UnexpectedOptionError('w=5: unexpected option')
 [sub]
     y = MinValueError('sub.y=-1.5: value is lower than min 0.0')
 >>> print(config['min_value'])
 100
 >>> print(config['coeffs'])
 [1.0, 1.0, 1.0]

Notice that two values have been added to

 >>> from zirkon.schema import Schema
 >>> from zirkon.validator import Int, Str, StrChoice, Float, Bool, FloatList
 >>> schema = Schema()
 >>> schema['num'] = Int(min=0)
 >>> schema['mode'] = StrChoice(choices=("xy", "yx", "xx"))
 >>> schema['sub'] = {}
 >>> schema['sub']['enable'] = Bool()
 >>> schema['sub']['x'] = Float(min=0.0)
 >>> schema['sub']['y'] = Float(min=0.0)
 >>> schema['name'] = Str()
 >>> schema['min_value'] = Int(default=100)
 >>> schema['coeffs'] = FloatList(min_len=1, default=[1.0, 1.0, 1.0])
 >>> validation = schema.validate(config)
 >>> validation.dump()
 w = UnexpectedOptionError('w=5: unexpected option')
 [sub]
     y = MinValueError('sub.y=-1.5: value is lower than min 0.0')
 >>> print(config['min_value'])
 100
 >>> print(config['coeffs'])
 [1.0, 1.0, 1.0]

Notice that two values have been added to

 >>> from zirkon.schema import Schema
 >>> from zirkon.validator import Int, Str, StrChoice, Float, Bool, FloatList
 >>> schema = Schema()
 >>> schema['num'] = Int(min=0)
 >>> schema['mode'] = StrChoice(choices=("xy", "yx", "xx"))
 >>> schema['sub'] = {}
 >>> schema['sub']['enable'] = Bool()
 >>> schema['sub']['x'] = Float(min=0.0)
 >>> schema['sub']['y'] = Float(min=0.0)
 >>> schema['name'] = Str()
 >>> schema['min_value'] = Int(default=100)
 >>> schema['coeffs'] = FloatList(min_len=1, default=[1.0, 1.0, 1.0])
 >>> validation = schema.validate(config)
 >>> validation.dump()
 w = UnexpectedOptionError('w=5: unexpected option')
 [sub]
     y = MinValueError('sub.y=-1.5: value is lower than min 0.0')
 >>> print(config['min_value'])
 100
 >>> print(config['coeffs'])
 [1.0, 1.0, 1.0]

Notice that two values have been added to

 >>> from zirkon.schema import Schema
 >>> from zirkon.validator import Int, Str, StrChoice, Float, Bool, FloatList
 >>> schema = Schema()
 >>> schema['num'] = Int(min=0)
 >>> schema['mode'] = StrChoice(choices=("xy", "yx", "xx"))
 >>> schema['sub'] = {}
 >>> schema['sub']['enable'] = Bool()
 >>> schema['sub']['x'] = Float(min=0.0)
 >>> schema['sub']['y'] = Float(min=0.0)
 >>> schema['name'] = Str()
 >>> schema['min_value'] = Int(default=100)
 >>> schema['coeffs'] = FloatList(min_len=1, default=[1.0, 1.0, 1.0])
 >>> validation = schema.validate(config)
 >>> validation.dump()
 w = UnexpectedOptionError('w=5: unexpected option')
 [sub]
     y = MinValueError('sub.y=-1.5: value is lower than min 0.0')
 >>> print(config['min_value'])
 100
 >>> print(config['coeffs'])
 [1.0, 1.0, 1.0]

Notice that two values have been added to

 >>> from zirkon.schema import Schema
 >>> from zirkon.validator import Int, Str, StrChoice, Float, Bool, FloatList
 >>> schema = Schema()
 >>> schema['num'] = Int(min=0)
 >>> schema['mode'] = StrChoice(choices=("xy", "yx", "xx"))
 >>> schema['sub'] = {}
 >>> schema['sub']['enable'] = Bool()
 >>> schema['sub']['x'] = Float(min=0.0)
 >>> schema['sub']['y'] = Float(min=0.0)
 >>> schema['name'] = Str()
 >>> schema['min_value'] = Int(default=100)
 >>> schema['coeffs'] = FloatList(min_len=1, default=[1.0, 1.0, 1.0])
 >>> validation = schema.validate(config)
 >>> validation.dump()
 w = UnexpectedOptionError('w=5: unexpected option')
 [sub]
     y = MinValueError('sub.y=-1.5: value is lower than min 0.0')
 >>> print(config['min_value'])
 100
 >>> print(config['coeffs'])
 [1.0, 1.0, 1.0]

Notice that two values have been added to *config*, due to the defaults defined in the *schema*.

Interpolation
-------------

Zirkon supports value interpolation: *config* values can be influenced by other values:

 >>> from zirkon.config import ROOT
 >>> config = Config()
 >>> config['x'] = 2
 >>> config['y'] = ROOT['x'] * 4
 >>> print(config['y'])
 8
 >>> config['x'] = 10
 >>> print(config['y'])
 40
 >>> config.dump()
 x = 10
 y = ROOT['x'] * 4
 >>>

The value of *y* is tied to *x* by means of the expression

 >>> from zirkon.config import ROOT
 >>> config = Config()
 >>> config['x'] = 2
 >>> config['y'] = ROOT['x'] * 4
 >>> print(config['y'])
 8
 >>> config['x'] = 10
 >>> print(config['y'])
 40
 >>> config.dump()
 x = 10
 y = ROOT['x'] * 4
 >>>

The value of *y* is tied to *x* by means of the expression

 >>> from zirkon.config import ROOT
 >>> config = Config()
 >>> config['x'] = 2
 >>> config['y'] = ROOT['x'] * 4
 >>> print(config['y'])
 8
 >>> config['x'] = 10
 >>> print(config['y'])
 40
 >>> config.dump()
 x = 10
 y = ROOT['x'] * 4
 >>>

The value of *y* is tied to *x* by means of the expression ``ROOT['x'] * 4``.

This can be used also in *Validators*:

 >>> schema = Schema()
 >>> schema['num'] = Int(min=1)
 >>> schema['coeffs'] = FloatList(min_len=ROOT['num'])

The 'coeffs' validator requires a float list whose length is at least 'num', where 'num' is the value found in the validated config:

 >>> config = Config()
 >>> config['num'] = 2
 >>> config['coeffs'] = []
 >>> schema.validate(config).dump()
 coeffs = MinLengthError('coeffs=[]: length 0 is lower than min_len 2')
 >>> config['num'] = 8
 >>> schema.validate(config).dump()
 coeffs = MinLengthError('coeffs=[]: length 0 is lower than min_len 8')
