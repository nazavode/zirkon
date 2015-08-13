.. _intro:

=====================
 Value interpolation
=====================

.. contents::

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

The definition of ``ROOT`` is equivalent to

 >>> from daikon.toolbox.deferred import DName
 >>> ROOT = DName('ROOT')
 >>> expr = ROOT['a']
 >>> type(expr)
 <class 'daikon.toolbox.deferred.DGetitem'>
 >>> print(expr.unparse())
 ROOT['a']

In order to evaluate this object it is necessary to provide a dictionary for the name lookup:

 >>> from daikon.config import Config
 >>> config1 = Config({'a': 10})
 >>> config2 = Config({'a': 20})
 >>> expr.evaluate({'ROOT': config1})
 10
 >>> expr.evaluate({'ROOT': config2})
 20

The Daikon ``ROOT`` object is always mapped to the current *config* (i.e., the *root section*).

 >>> config = Config({'a': 5})
 >>> config['b'] = ROOT['a'] * 10  # ROOT -> config
 >>> config.dump()
 a = 5
 b = 50

The SECTION object
------------------

The ``SECTION`` object is very similar to ``ROOT``, but it refers to the current *section* and not to the *config*:

 >>> from daikon.config import SECTION
 >>> config['sub'] = {'x': 2}
 >>> config['sub']['y'] = ROOT['a'] - SECTION['x']

Here, *ROOT* is *config*, while *SECTION* is *config['sub']*:

 >>> config.dump()
 a = 5
 b = 50
 [sub]
    x = 2
    y = 3

    .. note::

        Notice that deferred expressions are **never** stored on the *config*: they are evaluated at the moment they are inserted into the *config*.
        The *config* contains always the evaluated values, not the deferred expressions.

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
 y = 20
 z = 30

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
 y = 20
 z = 30

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
 coeffs = MaxLengthError(KeyValue('coeffs', [0.1, 0.2, 0.3, 0.4]), 'value has length 4 that is greater than max_len 3')

