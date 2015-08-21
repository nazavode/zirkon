# -*- coding: utf-8 -*-
#
# Copyright 2013 Simone Campagna
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Serializer classes.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = ['Serializer']

from .serializer import Serializer

try:
    from .zirkon_serializer import ZirkonSerializer
    __all__.append(ZirkonSerializer.__name__)
except ImportError:  # pragma: no cover
    pass

try:
    from .json_serializer import JSONSerializer
    __all__.append(JSONSerializer.__name__)
except ImportError:  # pragma: no cover
    pass

try:
    from .configobj_serializer import ConfigObjSerializer
    __all__.append(ConfigObjSerializer.__name__)
except ImportError:  # pragma: no cover
    pass

try:
    from .pickle_serializer import PickleSerializer
    __all__.append(PickleSerializer.__name__)
except ImportError:  # pragma: no cover
    pass
