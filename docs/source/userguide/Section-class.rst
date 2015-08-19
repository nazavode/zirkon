.. _intro:

==================
 The Section class
==================

.. contents::


The ``Section`` class is the base class for ``Config``, ``Schema`` and ``Validation``; it implements a dictionary-like object.

The Section class
=================













How value interpolation works
=============================

Value interpolation is based on the ``daikon.toolbox.deferred`` module. This module provides support for deferred evaluation of expressions. For instance:

The deferred module
-------------------

 >>> from daikon.toolbox.deferred import DConst
 >>> x = DConst(10)
 >>> expr = 3 * (x - 5)
 >>> type(expr)
 <class 'daikon.toolbox.deferred.DMul'>
 >>> print(expr)
 DMul(3, DSub(DConst(10), 5))

The expression has not been evaluated; the evaluation can be deferred at any time:

 >>> print(expr.evaluate())
 15

The expression can be unparsed to the original python expression:

 >>> print(expr.unparse())
 3 * (10 - 5)

The ROOT object
---------------

The Daikon ``ROOT`` object is always mapped to the current *config* (i.e., the *root section*). It can be used to compose expressions:

 >>> from daikon.config import Config, ROOT
 >>> config = Config({'a': 5})
 >>> config['b'] = ROOT['a'] * 10  # ROOT -> config
 >>> print(config['b'])
 50

The SECTION object
------------------

The ``SECTION`` object is very similar to ``ROOT``, but it refers to the current *section* and not to the *config*:

 >>> from daikon.config import SECTION
 >>> config['sub'] = {'x': 2}
 >>> config['sub']['y'] = ROOT['a'] - SECTION['x']

Here, *ROOT* is *config*, while *SECTION* is *config['sub']*:

 >>> print(config['a'], config['sub']['x'], config['sub']['y'])
 5 2 3

    .. note::

        Values referring to ``ROOT`` and ``SECTION`` (deferred expressions) are always evaluated using getter methods: ``__getitem__``,
        ``get``, ``get_option``.
        During iteration, deferred expressions are not evaluated. The ``daikon.utils.replace_deferred`` function can be used to replace
        all deferred values with their current value.

Interpolation in config files
=============================

Interpolation can be used in config files or strings; in the following example, the config object is loaded from a string serialization:

 >>> config_s = """\
 ... x = 10
 ... y = ROOT['x'] * 2
 ... z = ROOT['x'] * 3
 ... """
 >>> config = Config.from_string(config_s, protocol="daikon")
 >>> config.dump()
 x = 10
 y = ROOT['x'] * 2
 z = ROOT['x'] * 3
 >>> print(config['x'], config['y'], config['z'])
 10 20 30

This allows to define values depending on previously defined values. 

Interpolation in validators
===========================

Interpolation can be used to set validators' arguments; for instance:

 >>> from daikon.schema import Schema
 >>> from daikon.validator import Int
 >>> schema = Schema()
 >>> schema['x'] = Int()
 >>> schema['y'] = Int(default=ROOT['x'] * 2)
 >>> schema['z'] = Int(default=ROOT['x'] * 3)
 >>> config = Config({'x': 10}, schema=schema)
 >>> config.dump()
 x = 10

The default values *y* and *z* are not shown, but they are available:

 >>> print(config['y'], config['z'])
 20 30

Interpolation can be applied to any validator argument. In the following example, interpolation is used to force a list *coeffs* to have the length specified by a config parametes *num*:

 >>> from daikon.validator import FloatList
 >>> schema = Schema()
 >>> schema['num'] = Int()
 >>> schema['coeffs'] = FloatList(min_len=ROOT['num'], max_len=ROOT['num'])
 >>> config = Config()
 >>> config['num'] = 3
 >>> config['coeffs'] = [0.1, 0.2, 0.3, 0.4]
 >>> validation = schema.validate(config)
 >>> validation.dump()
 coeffs = MaxLengthError('coeffs=[0.1, 0.2, 0.3, 0.4]: length 4 is greater than max_len 3')

