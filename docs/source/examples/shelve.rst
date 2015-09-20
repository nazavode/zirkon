.. _intro-shelve:

.. py:currentmodule:: zirkon.config

.. |Config| replace:: :py:class:`Config`

.. py:currentmodule:: zirkon.flatmap

.. |FlatMap| replace:: :py:class:`FlatMap`


================
 Using a shelve
================

This example shows how to add persistency to the configuration data; all the information is immediately registered on a persistent database. This is done by using a :py:class:`shelve.Shelf` as internal dictionary.

.. warning::

    The python :py:class:`shelve.Shelf` mapping needs particular attention when using mutable values. Indeed, when a key value is retrieved, the shelf always
    returns a temporary object; if this object is changed, the change does not automatically apply to the database data.

     >>> import os
     >>> import shelve
     >>> import tempfile
     >>> with tempfile.TemporaryDirectory() as tdir:
     ...     tfile = os.path.join(tdir, 'tmp.shelf')
     ...     with shelve.open(tfile) as shelf:
     ...         shelf['x'] = {}
     ...         shelf['x']['y'] = 10
     ...         print(shelf['x'])
     {}

    The statement ``shelf['x']['y'] = 10`` has no effect, since ``shelf['x']`` is a temporary object.

The following example shows how to use a shelf as container for the config's data:

 >>> from collections import OrderedDict
 >>> from zirkon import Config
 >>> from zirkon.flatmap import FlatMap

 >>> with tempfile.TemporaryDirectory() as tdir:
 ...     tfile = os.path.join(tdir, 'x.shelf')
 ...     with shelve.open(tfile) as shelf:
 ...         config = Config(dictionary=FlatMap(shelf))
 ...         config['sub'] = {}
 ...         config['sub']['filename'] = "x.dat"
 ...         config['sub']['data'] = {'max': 100}
 ...         config['sub']['alpha'] = 1.05
 ...     # the shelf has been closed
 ...     # reopen the shelf:
 ...     with shelve.open(tfile) as shelf:
 ...         config = Config(dictionary=FlatMap(shelf))
 ...         print(config['sub']['data']['max'])
 100
 >>>

In this example, the shelf is wrapped with a |FlatMap| object. The reason is that |Config| implements subsections as dictionary values; since dictionaries are mutable objects, due to the shelf's limitation with mutable values an expression like ``config["x"]["y"] = 10`` does not really change the config object:

 >>> with tempfile.TemporaryDirectory() as tdir:
 ...     tfile = os.path.join(tdir, 'y.shelf')
 ...     with shelve.open(tfile) as shelf:
 ...         config = Config(dictionary=shelf)
 ...         config['x'] = {}
 ...         config['x']['y'] = 10
 ...         config.dump()
 [x]
 >>>

The |FlatMap| class implements a nested dictionary interface over a flat dictionary:

 >>> container = OrderedDict()
 >>> flatdict = FlatMap(dictionary=container)
 >>> flatdict['x'] = 10
 >>> flatdict['sub'] = {'a': 1}
 >>> container
 OrderedDict([('x', 10), ('sub.', None), ('sub.a', 1)])

This solves the problem with subsections, since subsections will not be implemented as dictionary values of the shelf object.

.. caution::
    When a shelf is used as persistent storage, mutable values must be carefully handled. Indeed, when changing a mutable config item, the changed value cannot be automatically stored on the db:

    .. code-block:: python

       config["x"] = []
       config["x"].append(10)

    The latest statement changes a temporary object, not the object stored on the db.
