.. zirkon documentation master file, created by
   sphinx-quickstart on Thu Aug 20 13:21:39 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Zirkon documentation
====================

Zirkon is a python configuration library. It allows to read/write configuration files using multiple serializatio protocols, and to define a schema to validate configuration data. Moreover, it supports by design to delegate the storage of internal data to an external dict-like object, for instance a ``shelve``, in order to provide persistence.

Zirkon requires python version 3.4.


.. toctree::
    :maxdepth: 2

    introduction
    first-steps
    validation
    examples/index
    tool

The zirkon package
------------------

.. toctree::
    :maxdepth: 1

    modules

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

