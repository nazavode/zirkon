.. _intro-shelve:

================
 Using a shelve
================

This example shows how to add persistency to the configuration data; all the information is immediately registered on a persistent database. This is done by using a ``shelve.Shelf`` as internal dictionary.


 >>> from collections import OrderedDict
 >>> import os
 >>> import shelve
 >>> import tempfile
 >>> from zirkon.config import Config
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

In this example, the shelf is wrapped with a *FlatMap* object. The reason is that the *Shelf* object does not support subsection nesting as expected by *Config*. Indeed, `shelf[...]` is always a temporary object restored from db; if it's a mutable object, for instance a dict, it's worthless to change it, since the change will not be automatically registered on the db. For instance, suppose that `shelf["x"]` is a dictionary; executing `shelf["x"]["y"] = 10` will modify a temporary dictionary object, not the object stored on the db. If the config is directly based on the shelf object, subsections are stored as dict values, so changing subsection values as in `config["x"]["y"] = 10` has no effect on the config object itself:

 >>> with tempfile.TemporaryDirectory() as tdir:
 ...     tfile = os.path.join(tdir, 'y.shelf')
 ...     with shelve.open(tfile) as shelf:
 ...         config = Config(dictionary=shelf)
 ...         config['x'] = {}
 ...         config['x']['y'] = 10
 ...         config.dump()
 [x]
 >>>

The FlatMap utility class
-------------------------

The *FlatMap* class implements a nested dictionary interface over a flat dictionary:

 >>> container = OrderedDict()
 >>> flatdict = FlatMap(dictionary=container)
 >>> flatdict['x'] = 10
 >>> flatdict['sub'] = {'a': 1}
 >>> container
 OrderedDict([('x', 10), ('sub.', None), ('sub.a', 1)])

Using mutable values
--------------------
When a shelf is used as persistent storage, mutable values must be carefully handled. Indeed, when changing a mutable config item, the changed value cannot be automatically stored on the db:

.. code-block:: python

   config["x"] = []
   config["x"].append(10)

The latest statement changes a temporary object, not the object stored on the db.
