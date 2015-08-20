.. _intro:

================
 Using a shelve
================

This example shows how to add dynamic persistency to the configuration data; all the information is immediately registered on a persistent database. This is done by using a ``shelve.Shelf`` as internal dictionary.


 >>> import os
 >>> import shelve
 >>> import tempfile
 >>> with tempfile.TemporaryDirectory() as tdir:
 ...     tfile = os.path.join(tdir, 'x.shelf')
 ...     shelf = shelve.open(tfile)
 ...     from zirkon.toolbox.flatmap import FlatMap
 ...     flatshelf = FlatMap(dictionary=shelf)
 ...     config = Config(dictionary=flatshelf)
 ...     config['sub'] = {}
 ...     config['sub']['filename'] = "x.dat"
 ...     config['sub']['data'] = {'max': 100}
 ...     config['sub']['alpha'] = 1.05
 ...     print(config['sub']['data']['max'])
 100
 >>>

The *Shelf* object does not support subsection nesting as expected by *Config*; it's preferrable to use the *Shelf* as a flat dictionary, without nesting; this is why it's wrapped in a *FlatMap* object.

The FlatMap utility class
-------------------------

The *FlatMap* class implements a nested dictionary interface over a flat dictionary:

 >>> container = OrderedDict()
 >>> flatdict = FlatMap(dictionary=container)
 >>> flatdict['x'] = 10
 >>> flatdict['sub'] = {'a': 1}
 >>> container
 OrderedDict([('x', 10), ('sub.', None), ('sub.a', 1)])

