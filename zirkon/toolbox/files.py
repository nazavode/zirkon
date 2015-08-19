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

"""\
zirkon.toolbox.files
====================
File-related utility functions
"""

__author__ = "Simone Campagna"

import os


def createdir(filename):
    """create_dir(filename)
       Create the filename directory if it does not exist
    """
    dirname, filename = os.path.split(filename)
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
