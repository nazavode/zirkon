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
zirkon.toolbox.unrepr
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

    def py_ast_str(ast_body):
        """py_ast_str"""
        return ast_body.s

    def py_ast_num(ast_body):
        """py_ast_num"""
        return ast_body.n

    def py_ast_name_constant(ast_body):
        """py_ast_name_constant"""
        return ast_body.value

    def py_ast_list(ast_body):
        """py_ast_list"""
        elements = []
        for element in ast_body.elts:
            elements.append(py_ast_unrepr(element))
        if isinstance(ast_body, ast.Tuple):
            elements = tuple(elements)
        return elements

    def py_ast_tuple(ast_body):
        """py_ast_tuple"""
        return tuple(py_ast_list(ast_body))

    def py_ast_dict(ast_body):
        """py_ast_dict"""
        dct = {}
        for ast_key, ast_value in zip(ast_body.keys, ast_body.values):
            key = py_ast_unrepr(ast_key)
            value = py_ast_unrepr(ast_value)
            dct[key] = value
        return dct

    def py_ast_name(ast_body):
        """py_ast_name"""
        if ast_body.id in globals_d:
            return globals_d[ast_body.id]
        else:
            raise SyntaxError("cannot unrepr string {!r}: col {}: undefined symbol {}".format(
                string,
                ast_body.col_offset,
                ast_body.id))

    def py_ast_index(ast_body):
        """py_ast_index"""
        return py_ast_unrepr(ast_body.value)

    def py_ast_slice(ast_body):
        """py_ast_slice"""
        slist = []
        for key in 'lower', 'upper', 'step':
            value = getattr(ast_body, key)
            if value is not None:
                value = py_ast_unrepr(value)
            slist.append(value)
        return slice(*slist)

    def py_ast_subscript(ast_body):
        """py_ast_subscript"""
        v_element = py_ast_unrepr(ast_body.value)
        v_slice = py_ast_unrepr(ast_body.slice)
        return v_element[v_slice]

    def py_ast_unary_op(ast_body):
        """py_ast_unary_op"""
        unary_op_d = {
            ast.UAdd: lambda x: +x,
            ast.USub: lambda x: -x,
        }
        ast_op = ast_body.op
        for op_class, op_function in unary_op_d.items():
            if isinstance(ast_op, op_class):
                return op_function(py_ast_unrepr(ast_body.operand))
        raise SyntaxError("cannot unrepr string {!r}: col {}: unsupported unary operator {}".format(
            string,
            ast_body.col_offset,
            ast_op.__class__.__name__))

    def py_ast_bin_op(ast_body):
        """py_ast_bin_op"""
        binary_op_d = {
            ast.Add: lambda x, y: x + y,
            ast.Sub: lambda x, y: x - y,
            ast.Mult: lambda x, y: x * y,
            ast.Div: lambda x, y: x / y,
            ast.FloorDiv: lambda x, y: x // y,
            ast.Mod: lambda x, y: x // y,
            ast.Pow: lambda x, y: x ** y,
        }
        ast_op = ast_body.op
        for op_class, op_function in binary_op_d.items():
            if isinstance(ast_op, op_class):
                return op_function(py_ast_unrepr(ast_body.left), py_ast_unrepr(ast_body.right))
        raise SyntaxError("cannot unrepr string {!r}: col {}: unsupported binary operator {}".format(
            string,
            ast_body.col_offset,
            ast_op.__class__.__name__))

    def py_ast_call(ast_body):
        """py_ast_call"""
        ast_func = ast_body.func
        if not hasattr(ast_func, 'id'):
            raise SyntaxError("cannot unrepr string {!r}: col {}: invalid call: not a function".format(
                string,
                ast_body.col_offset))
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

    py_ast_function_d = {
        ast.Str: py_ast_str,
        ast.Num: py_ast_num,
        ast.NameConstant: py_ast_name_constant,
        ast.List: py_ast_list,
        ast.Tuple: py_ast_tuple,
        ast.Dict: py_ast_dict,
        ast.Name: py_ast_name,
        ast.Index: py_ast_index,
        ast.Slice: py_ast_slice,
        ast.Subscript: py_ast_subscript,
        ast.UnaryOp: py_ast_unary_op,
        ast.BinOp: py_ast_bin_op,
        ast.Call: py_ast_call,
    }

    if globals_d is None:
        globals_d = {
            'list': list,
            'tuple': tuple,
            'dict': dict,
        }

    def py_ast_unrepr(ast_body):
        """py_ast_unrepr(ast_body) -> value"""
        for ast_class, function in py_ast_function_d.items():
            if isinstance(ast_body, ast_class):
                return function(ast_body)
        raise SyntaxError("cannot unrepr string {!r}: col {}: invalid ast {}".format(
            string,
            ast_body.col_offset,
            type(ast_body).__name__))

    expr = compile(string, "<string>", "eval", ast.PyCF_ONLY_AST)
    return py_ast_unrepr(expr.body)
