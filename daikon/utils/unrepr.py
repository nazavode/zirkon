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
config.utils.unrepr
===================
Implementation of the 'py_unrepr' function, which does unrepr of
python builtin types (int, str, float, bool, list, tuple).
"""

__author__ = "Simone Campagna"
__all__ = [
    'unrepr',
]

import ast

def unrepr(string):
    def py_ast_unrepr(ast_body):
        if isinstance(ast_body, ast.Str):
            return ast_body.s
        elif isinstance(ast_body, ast.Num):
            return ast_body.n
        elif isinstance(ast_body, ast.NameConstant):
            return ast_body.value
        elif isinstance(ast_body, (ast.List, ast.Tuple)):
            elements = []
            for element in ast_body.elts:
                elements.append(py_ast_unrepr(element))
            if isinstance(ast_body, ast.Tuple):
                elements = tuple(elements)
            return elements
        elif isinstance(ast_body, ast.UnaryOp):
            try:
                operand = py_ast_unrepr(ast_body.operand)
                if isinstance(ast_body.op, ast.UAdd):
                    return +operand
                elif isinstance(ast_body.op, ast.USub):
                    return -operand
            except TypeError as err:
                raise SyntaxError("cannot unrepr string {!r}: col {}: invalid operator {} followed by {!r}".format(
                    string,
                    ast_body.col_offset,
                    type(ast_body).__name__,
                    operand))
        raise SyntaxError("cannot unrepr string {!r}: col {}: invalid ast {}".format(
            string,
            ast_body.col_offset,
            type(ast_body).__name__))
    

    expr = compile(string, "<string>", "eval", ast.PyCF_ONLY_AST)
    return py_ast_unrepr(expr.body)
