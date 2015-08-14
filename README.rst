Daikon
======
Python configuration library.


What is daikon
--------------

Daikon is a python library to handle configuration data. It behaves like a dictionary, and supports nested sections:

 >>> from daikon.config import Config
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

Daikon currently supports the following serialization protocols:

 +---------+--------+---------------------------------------------------------------+
 |Protocol |text/raw|description                                                    |
 +=========+========+===============================================================+
 |daikon   |text    |the native protocol; it implements a nested INI file           |
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
 * ``dump``: a shorthand for ``to_stream``, where by default *stream=sys.stdout* and *protocol="daikon"* 

Validation
----------

Daikon supports validation through a *Schema* object. A *Schema* is a *Config* with *Validator* values:

 >>> from daikon.schema import Schema
 >>> from daikon.validator import Int, Str, StrChoice, Float, Bool, FloatList
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
 >>> config.dump()
 num = 10
 mode = 'xy'
 [sub]
     enable = True
     x = 1.5
     y = -1.5
 name = 'alpha'
 w = 5
 min_value = 100
 coeffs = [1.0, 1.0, 1.0]

Notice that two values have been added to *config*, due to the defaults defined in the *schema*.

Interpolation
-------------

Daikon supports value interpolation: previously defined config values can inflence new values:

 >>> from daikon.config import ROOT
 >>> config = Config()
 >>> config['a'] = 10
 >>> config['b'] = ROOT['a'] * 2
 >>> config.dump()
 a = 10
 b = 20

 >>> config_s = """
 ... x = 1.0
 ... y = 2.0
 ... z = ROOT['x'] + ROOT['y']"""
 >>> config = Config.from_string(config_s, protocol="daikon")
 >>> config.dump()
 x = 1.0
 y = 2.0
 z = 3.0
 >>>

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