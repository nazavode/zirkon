.. _validation:

============
 Validation
============

The Schema class
================

The *Schema* class is a *Config* subclass containing the ``validate`` method to validate a config. It accepts only *Validator* instances as values; *Validators* are used to validate the value of an option.
In casse of errors, *Validators* raise a specific *OptionValidationError* exception. By default, the ``Schema.validate`` method collects all these xceptions and puts it in a *Validation* object (another *Config* subclass accepting *OptionValidationError* values).

Most of the validators check for a specific value type; if the type does not match, an *InvalidTypeError* exception is produced. They can additionally perform other checks.

A validator can

* add an option to the config;
* remove an option from the config;
* change an option value.


Standard validators
===================

There are many predefided validators; this is the list of integer validators:

 +------------+---------------------+------------------+
 |Validator   |Basic validation     |Accepted Arguments|
 |name        |                     |                  |
 +------------+---------------------+------------------+
 |Int         |An integer value     |* default         |
 |            |                     |* min             |
 |            |                     |* max             |
 +------------+---------------------+------------------+
 |IntList     |A list of integer    |* default         |
 |            |values               |* min_len         |
 |            |                     |* max_len         |
 |            |                     |* item_min        |
 |            |                     |* item_max        |
 +------------+---------------------+------------------+
 |IntTuple    |A tuple of integer   |* default         |
 |            |values               |* min_len         |
 |            |                     |* max_len         |
 |            |                     |* item_min        |
 |            |                     |* item_max        |
 +------------+---------------------+------------------+
 |IntChoice   |An integer value     |* **choices**     |
 |            |contained in a set   |* default         |
 |            |of prefedifed choices|                  |
 +------------+---------------------+------------------+

The list of floating point validators:

 +------------+---------------------+------------------+
 |Validator   |Basic validation     |Accepted Arguments|
 |name        |                     |                  |
 +------------+---------------------+------------------+
 |Float       |A floating point     |* default         |
 |            |value                |* min             |
 |            |                     |* max             |
 +------------+---------------------+------------------+
 |FloatList   |A list of floating   |* default         |
 |            |point values         |* min_len         |
 |            |                     |* max_len         |
 |            |                     |* item_min        |
 |            |                     |* item_max        |
 +------------+---------------------+------------------+
 |FloatTuple  |A tuple of floating  |* default         |
 |            |point values         |* min_len         |
 |            |                     |* max_len         |
 |            |                     |* item_min        |
 |            |                     |* item_max        |
 +------------+---------------------+------------------+
 |FloatChoice |A floating point     |* **choices**     |
 |            |value contained in   |* default         |
 |            |a set of             |                  |
 |            |prefedifed choices   |                  |
 +------------+---------------------+------------------+

The list of string validators:

 +------------+---------------------+------------------+
 |Validator   |Basic validation     |Accepted Arguments|
 |name        |                     |                  |
 +------------+---------------------+------------------+
 |Str         |A string             |* default         |
 |            |                     |* min_len         |
 |            |                     |* max_len         |
 +------------+---------------------+------------------+
 |StrList     |A list of strings    |* default         |
 |            |                     |* min_len         |
 |            |                     |* max_len         |
 |            |                     |* item_min_len    |
 |            |                     |* item_max_len    |
 +------------+---------------------+------------------+
 |StrTuple    |A tuple of strings   |* default         |
 |            |                     |* min_len         |
 |            |                     |* max_len         |
 |            |                     |* item_min_len    |
 |            |                     |* item_max_len    |
 +------------+---------------------+------------------+
 |StrChoice   |A string             |* **choices**     |
 |            |contained in a set   |* default         |
 |            |of prefedifed choices|                  |
 +------------+---------------------+------------------+

The list of boolean validators:

 +------------+---------------------+------------------+
 |Validator   |Basic validation     |Accepted Arguments|
 |name        |                     |                  |
 +------------+---------------------+------------------+
 |Bool        |A boolean value      |* default         |
 |            |                     |* min             |
 |            |                     |* max             |
 +------------+---------------------+------------------+
 |BoolList    |A list of boolean    |* default         |
 |            |values               |* min_len         |
 |            |                     |* max_len         |
 |            |                     |* item_min        |
 |            |                     |* item_max        |
 +------------+---------------------+------------------+
 |BoolTuple   |A tuple of boolean   |* default         |
 |            |values               |* min_len         |
 |            |                     |* max_len         |
 |            |                     |* item_min        |
 |            |                     |* item_max        |
 +------------+---------------------+------------------+
 |BoolChoice  |A boolean value      |* **choices**     |
 |            |contained in a set   |* default         |
 |            |of prefedifed choices|                  |
 +------------+---------------------+------------------+

The explanation of the accepted arguments is:

- *default*: if provided, it  sets a default value for the option; if the key is missing from the validated config, the option is added with *default* as value. If a key is missing from the validated config and the corresponding *Validator* does not define a default, a *MissingRequiredOptionError* exception is produced;
- *min*, *max*: if provided, it sets a minimum/maximum value for the value; if the option value does not match, a *MinValueError*/*MaxValueError* exception is produced;
- *min_len*, *max_len*: if provided, it sets a minimum/maximum length for the value (sequences or strings); if the corresponding option value does not match, a *MinLengthError*/*MaxLengthError* exception is produced;
- *item_min*, *item_max*, *item_min_len*, *item_max_len*: the same as *min*, *max*, *min_len* and *max_len*, but they are applied to all the sequence items (for List and Tuple validators only).
- *choices*: only for the Choice validators; it is mandatory and defines the set of accepted values. If the option value is not a valid choice, an InvalidChoiceError is produced.

All these validators can change the option value; for instance:

- each validator can set the default value;
- the floating point validators accept integer values, but they are converted to *float*;
- the boolean validators accept integer values, but they are converted to *bool*.

For instance:

 >>> from zirkon.schema import Schema
 >>> from zirkon.validator import StrList
 >>> schema = Schema()
 >>> schema['filenames'] = StrList(min_len=3, item_min_len=2)

This schema requires that the *filenames* value is a list of strings with at least 3 items; the minimum length of the items is 2.

 >>> from zirkon.config import Config
 >>> config = Config()
 >>> config['filenames'] = ['a.dat', 'b.dat', 'c', 'd.dat']
 >>> validation = schema.validate(config)
 >>> validation.dump()
 filenames = MinLengthError("filenames[2]='c': length 1 is lower than min_len 2")


Unexpected options
==================

The *Schema* class accepts an *unexpected_option_validator* argument to be used to validate all the options found in the *config* but not in the *schema*. Any validator is acceptable, anyway three validators are especially thought for this purpose:

 +-------------------+---------------------------------------+
 |Validator          |Performed action                       |
 +-------------------+---------------------------------------+
 |Complain           |**default**                            |
 |                   |An *UnexpectedOptionError*             |
 |                   |exception is produced;                 |
 +-------------------+---------------------------------------+
 |Ignore             |The unexpected option is ignored       |
 |                   |and left in the config;                |
 +-------------------+---------------------------------------+
 |Remove             |The unexpected option is removed       |
 |                   |from the config.                       |
 +-------------------+---------------------------------------+

For instance:


 >>> schema = Schema()
 >>> config = Config({'x': 1})
 >>> validation = schema.validate(config)
 >>> validation.dump()
 x = UnexpectedOptionError('x=1: unexpected option')


 >>> from zirkon.validator import Ignore
 >>> schema = Schema(unexpected_option_validator=Ignore())
 >>> config = Config({'x': 1})
 >>> validation = schema.validate(config)
 >>> validation.dump()  # no errors
 >>> config.dump()  # 'x' has been left in config
 x = 1
 >>>

 >>> from zirkon.validator import Remove
 >>> schema = Schema(unexpected_option_validator=Remove())
 >>> config = Config({'x': 1})
 >>> validation = schema.validate(config)
 >>> validation.dump()  # no errors
 >>> config.dump()  # 'x' has been removed
 >>>
