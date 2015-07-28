# -*- coding: utf-8 -*-
"""
config.serializer
=================
Serializer classes
"""

__all__ = ['Serializer']
from .serializer import Serializer

try:
    from .json_serializer import JSONSerializer
    __all__.append(JSONSerializer.__name__)
except ImportError:
    pass

try:
    from .configobj_serializer import ConfigObjSerializer
    __all__.append(ConfigObjSerializer.__name__)
except ImportError:
    pass

try:
    from .pickle_serializer import PickleSerializer
    __all__.append(PickleSerializer.__name__)
except ImportError:
    pass
