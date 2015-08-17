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
daikon._tool.trace_errors
===========================
Context manager for exception handling
"""

__author__ = "Simone Campagna"

__all__ = [
    'trace_errors',
]

import sys


class TraceErrors(object):  # pylint: disable=R0903
    """Context manager to trace errors"""

    def __init__(self, debug_mode=False, exceptions=None, stream=sys.stderr):
        self._debug_mode = debug_mode
        if exceptions is None:
            exceptions = (Exception, )
        self._exceptions = exceptions
        self._stream = stream

    def __enter__(self):
        pass

    def exception_handler(self, exc_instance):
        """exception_handler(exc_instance)"""
        if self._debug_mode:
            import traceback
            traceback.print_exc()
        self._stream.write("ERR: {}: {}\n".format(type(exc_instance).__name__, exc_instance))
        sys.exit(1)

    def __exit__(self, exc_type, exc_instance, exc_traceback):
        if exc_type is not None:
            if issubclass(exc_type, self._exceptions):
                self.exception_handler(exc_instance)


def trace_errors(debug_mode=False, exceptions=None, stream=sys.stderr):
    """trace_errors(debug_mode=False, exceptions=None, stream=sys.stderr)
       Context manager to enable/disable errors traceback.
    """
    return TraceErrors(debug_mode=debug_mode, exceptions=exceptions, stream=stream)
