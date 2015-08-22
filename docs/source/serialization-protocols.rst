.. _serialization formats:

=======================
 Serialization formats
=======================

.. contents::
    :local:
    :depth: 2

The *zirkon* protocol
=====================

The *zirkon* protocol is very simple:

* options are serialized as ``key = value``, where value is the representation of the pyton object

  .. code-block:: python

     x = 10
     name = "alpha"

* section begins with ``[section_name]``, and their content is indented:

  .. code-block:: python

     x = 10
     name = "alpha"
     [params]
         a = 1.02
         b = 3.3
         coeffs = [-0.5, 0.5]

* sections can be nested using indentation:

  .. code-block:: python

     x = 10
     [params]
         a = 1.02
         [sub]
             y = 4
         b = 3.3
         coeffs = [-0.5, 0.5]
     name = "alpha"

In the last example:

* option ``y`` belongs to subsection *sub* (``config["params"]["sub"]["y"]``)
* options ``a``, ``b`` and ``coeffs`` belong to subsection *params* (``config["params"]["a"]``, ...)
* options ``x``, ``name`` belong to the root section (``config["x"]``, ...)

The *configobj* protocol
========================

The configobj protocol is compatible with the *ConfigObj* format using the ``unrepr`` option, see http://www.voidspace.org.uk/python/configobj.html.

* options are serialized as ``key = value``, where value is the representation of the pyton object

  .. code-block:: python

     x = 10
     name = "alpha"

* section begins with the ``section_name`` enclosed in a number of square brackets equal to the nesting level; the indentation **is not** significant:

  .. code-block:: python

     [params]
         a = 1.02
         [[sub]]
             y = 4
         b = 3.3
         coeffs = [-0.5, 0.5]

In the last example:

* option ``a`` belongs to subsection *params* (``config["params"]["a"]``, ...)
* options ``y``, ``b`` and ``coeffs`` belong to subsection *sub* (``config["params"]["sub"]["y"]``, ...), in spite of indentation.


The *json* protocol
===================

For a full explanation, see http://json.org/. For instance, the following *zirkon* serialization:

  .. code-block:: python

     x = 10
     [params]
         a = 1.02
         [sub]
             y = 4
         b = 3.3
         coeffs = [-0.5, 0.5]
     name = "alpha"

is serialized to *json* as:

  .. code-block:: python

     {
         "x": 10,
         "params": {
             "a": 1.02,
             "sub": {
                 "y": 4
             },
             "b": 3.3,
             "coeffs": [
                 -0.5,
                 0.5
             ]
         },
         "name": "alpha"
     }

The *pickle* protocol
=====================

The pickle serialization is a simple *pickle* dump of the internal dictionary. It's a raw format.

