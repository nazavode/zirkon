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
config.toolbox.unrepr
=====================
Implementation of the 'unrepr' function, which does unrepr of
python builtin types (int, str, float, bool, list, tuple).
"""

__author__ = "Simone Campagna"
__all__ = [
    'unrepr',
]

import ast


def unrepr(string, globals_d=None):
    """unrepr(string, globals_d=None) -> object
       Returns the object whose representation is 'string'.
       >>> for string in "1.05", "[2, 'a']", "3", "()":
       ...     obj = unrepr(string)
       ...     print(obj, type(obj).__name__)
       1.05 float
       [2, 'a'] list
       3 int
       () tuple
       >>>
    """

    if globals_d is None:
        globals_d = {
            'list': list,
            'tuple': tuple,
        }

    unary_op_d = {
        ast.UAdd: lambda x: +x,
        ast.USub: lambda x: -x,
    }
    binary_op_d = {
        ast.Add: lambda x, y: x + y,
        ast.Sub: lambda x, y: x - y,
        ast.Mult: lambda x, y: x * y,
        ast.Div: lambda x, y: x / y,
        ast.FloorDiv: lambda x, y: x // y,
        ast.Mod: lambda x, y: x // y,
        ast.Pow: lambda x, y: x ** y,
    }

    def py_ast_unrepr(ast_body):  # pylint: disable=R0911,R0912
        """py_ast_unrepr(ast_body) -> value"""
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
        elif isinstance(ast_body, ast.Dict):
            dct = {}
            for ast_key, ast_value in zip(ast_body.keys, ast_body.values):
                key = py_ast_unrepr(ast_key)
                value = py_ast_unrepr(ast_value)
                dct[key] = value
            return dct
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
        elif isinstance(ast_body, ast.Name):
            if ast_body.id in globals_d:
                return globals_d[ast_body.id]
            else:
                raise SyntaxError("cannot unrepr string {!r}: col {}: undefined symbol {}".format(
                    string,
                    ast_body.col_offset,
                    ast_body.id))
        elif isinstance(ast_body, ast.Index):
            return py_ast_unrepr(ast_body.value)
        elif isinstance(ast_body, ast.Slice):
            slist = []
            for k in 'lower', 'upper', 'step':
                v = getattr(ast.body, k)
                if v is not None:
                    v = py_ast_body(v)
            slist.append(v)
            return slice(*slist)
        elif isinstance(ast_body, ast.Subscript):
            v_element = py_ast_unrepr(ast_body.value)
            v_slice = py_ast_unrepr(ast_body.slice)
            return v_element[v_slice]
        elif isinstance(ast_body, ast.UnaryOp):
            op = ast_body.op
            for op_class, op_function in unary_op_d.items():
                if isinstance(op, op_class):
                    return op_function(py_ast_unrepr(ast_body.operand))
            else:
                raise SyntaxError("cannot unrepr string {!r}: col {}: unsupported unary operator {}".format(
                    string,
                    ast_body.col_offset,
                    type(ast_body).__name__,
                    op.__class__.__name__))
        elif isinstance(ast_body, ast.BinOp):
            op = ast_body.op
            for op_class, op_function in binary_op_d.items():
                if isinstance(op, op_class):
                    return op_function(py_ast_unrepr(ast_body.left), py_ast_unrepr(ast_body.right))
            else:
                raise SyntaxError("cannot unrepr string {!r}: col {}: unsupported binary operator {}".format(
                    string,
                    ast_body.col_offset,
                    type(ast_body).__name__,
                    op.__class__.__name__))
        elif isinstance(ast_body, ast.Call):
            ast_func = ast_body.func
            if ast_func.id in globals_d:
                p_args = [py_ast_unrepr(arg) for arg in ast_body.args]
                n_args = {keyword.arg: py_ast_unrepr(keyword.value) for keyword in ast_body.keywords}
                if ast_body.starargs is not None:
                    starargs = py_ast_unrepr(ast_body.starargs)
                    p_args.extend(starargs)
                if ast_body.kwargs is not None:
                    kwargs = py_ast_unrepr(ast_body.kwargs)
                    n_args.update(kwargs)
                func = globals_d[ast_func.id]
                try:
                    return func(*p_args, **n_args)
                except Exception as err:
                    raise SyntaxError("cannot unrepr string {!r}: col {}: invalid call to function {}: {}: {}".format(
                        string,
                        ast_body.col_offset,
                        ast_func.id,
                        type(err).__name__,
                        err))
            else:
                raise SyntaxError("cannot unrepr string {!r}: col {}: invalid call to undefined function {}".format(
                    string,
                    ast_body.col_offset,
                    ast_func.id))
        raise SyntaxError("cannot unrepr string {!r}: col {}: invalid ast {}".format(
            string,
            ast_body.col_offset,
            type(ast_body).__name__))

    expr = compile(string, "<string>", "eval", ast.PyCF_ONLY_AST)
    return py_ast_unrepr(expr.body)
