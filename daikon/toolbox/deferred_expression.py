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
config.deferred_expression
==========================
Implementation of the DEBase class for deferred evaluation of expressions.
"""

__author__ = "Simone Campagna"
__all__ = [
    'DEBase',
    'DEBinaryOperator',
    'DEUnaryOperator',
    'DEName',
    'DEConst',
    'DEAbs',
    'DEPos',
    'DENeg',
    'DEAdd',
    'DESub',
    'DEMul',
    'DETrueDiv',
    'DEFloorDiv',
    'DEMod',
    'DEDivMod',
    'DEPow',
    'DEEq',
    'DENe',
    'DELt',
    'DELe',
    'DEGt',
    'DEGe',
    'DEAnd',
    'DEOr',
    'DENot',
    'DELen',
    'DEStr',
    'DERepr',
    'DEContains',
    'DEGetattr',
    'DEGetitem',
    'DECall',
]

import abc

# lambda	Lambda Expression
# or	Boolean OR
# and	Boolean AND
# not x	Boolean NOT
# in, not in	Membership tests
# is, is not	Identity tests
# <, <=, >, >=, !=, ==	Comparisons
# |	Bitwise OR
# ^	Bitwise XOR
# &	Bitwise AND
# <<, >>	Shifts
# +, -	Addition and subtraction
# *, /, %	Multiplication, Division and Remainder
# +x, -x	Positive, Negative
# ~x	Bitwise NOT
# **	Exponentiation
# x.attribute	Attribute reference
# x[index]	Subscription
# x[index:index]	Slicing
# f(arguments ...)	Function call
# (expressions, ...)	Binding or tuple display
# [expressions, ...]	List display
# {key:datum, ...}	Dictionary display
# `expressions, ...`	String conversion


class DEBase(metaclass=abc.ABCMeta):
    """DEBase()
       Abstract base class to compose generic expressions.
       Concrete classes must implement the evaluate() method.
    """
    PRIORITY = {
        'DEConst': 100000,
        'DEName': 100000,
        'DEOr': 1,
        'DEAnd': 2,
        'DENot': 3,
        'DEContains': 4,
        # 'DEIs': 5,
        'DELt': 6,
        'DELe': 6,
        'DEGt': 6,
        'DEGe': 6,
        'DEEq': 6,
        'DENe': 6,
        # 'DEBitwiseOr': 7,
        # 'DEBitwiseXOr': 8,
        # 'DEBitwiseAnd': 9,
        # 'DELeftShift': 10,
        # 'DERightShift': 10,
        'DEAdd': 11,
        'DESub': 11,
        'DEMul': 12,
        'DETrueDiv': 12,
        'DEFloorDiv': 12,
        'DEMod': 12,
        'DEDivMod': 12,
        'DEPos': 13,
        'DENeg': 13,
        # 'DEBitwiseNot': 14,
        'DEPow': 15,
        'DECall': 16,
        'DEGetitem': 17,
        'DEGetattr': 18,
    }

    @abc.abstractmethod
    def evaluate(self):
        """evaluate() -> expression value"""
        pass

    def expression(self):
        """expression() -> python expression representation"""
        return self.impl_expression_wrap(wrap=False)

    def impl_expression_wrap(self, wrap):
        """impl_expression_wrap(wrap) -> expression representation
           If 'wrap' puts output in parenthesis.
        """
        return self.wrap(expression=self.impl_expression(), wrap=wrap)

    @abc.abstractmethod
    def impl_expression(self):
        """impl_expression() -> expression representation."""
        pass

    def wrap(self, expression, wrap):  # pylint: disable=R0201
        """wrap(expression, wrap) -> [wrapped] expression"""
        if wrap:
            return '(' + expression + ')'
        else:
            return expression

    # unary mathematical operators:
    def __abs__(self):
        return DEAbs(self)

    def __pos__(self):
        return DEPos(self)

    def __neg__(self):
        return DENeg(self)

    # binary mathematical operators:
    def __add__(self, other):
        return DEAdd(self, other)

    def __radd__(self, other):
        return DEAdd(other, self)

    def __sub__(self, other):
        return DESub(self, other)

    def __rsub__(self, other):
        return DESub(other, self)

    def __mul__(self, other):
        return DEMul(self, other)

    def __rmul__(self, other):
        return DEMul(other, self)

    def __truediv__(self, other):
        return DETrueDiv(self, other)

    def __rtruediv__(self, other):
        return DETrueDiv(other, self)

    def __floordiv__(self, other):
        return DEFloorDiv(self, other)

    def __rfloordiv__(self, other):
        return DEFloorDiv(other, self)

    def __mod__(self, other):
        return DEMod(self, other)

    def __rmod__(self, other):
        return DEMod(other, self)

    def __divmod__(self, other):
        return DEDivMod(self, other)

    def __rdivmod__(self, other):
        return DEDivMod(other, self)

    def __pow__(self, other):
        return DEPow(self, other)

    def __rpow__(self, other):
        return DEPow(other, self)

    # binary comparison operators:
    def __eq__(self, other):
        return DEEq(self, other)

    def __req__(self, other):
        return DEEq(other, self)

    def __ne__(self, other):
        return DENe(self, other)

    def __rne__(self, other):
        return DENe(other, self)

    def __lt__(self, other):
        return DELt(self, other)

    def __rlt__(self, other):
        return DEGe(other, self)

    def __le__(self, other):
        return DELe(self, other)

    def __rle__(self, other):
        return DEGt(self, other)

    def __gt__(self, other):
        return DEGt(self, other)

    def __rgt__(self, other):
        return DELe(self, other)

    def __ge__(self, other):
        return DEGe(self, other)

    def __rge__(self, other):
        return DELt(self, other)

    def __contains__(self, other):
        return DEContains(self, other)

    # Call:
    def __call__(self, *p_args, **n_args):
        return DECall(self, p_args, n_args)

    # Get attribute:
    def __getattr__(self, attr_name):
        return DEGetattr(self, attr_name)

    # Get item:
    def __getitem__(self, item):
        return DEGetitem(self, item)

    # utilities:
    @classmethod
    def evaluate_operand(cls, operand):
        """evaluate_operand() -> operand value"""
        if isinstance(operand, DEBase):
            return operand.evaluate()
        else:
            return operand

    @classmethod
    def impl_expression_operand(cls, operand, wrap=None):
        """impl_expression_operand(operand, wrap=None) -> operand value"""
        if isinstance(operand, DEBase):
            if wrap is None:
                wrap = operand.priority() < cls.priority()
            return operand.impl_expression_wrap(wrap=wrap)
        else:
            return repr(operand)

    @classmethod
    def priority(cls):
        """priority() -> priority"""
        return cls.PRIORITY.get(cls.__name__, 1000)


class DEConst(DEBase):
    """DEConst(value)
       DEConst value expression.
    """

    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.evaluate_operand(self.value)

    def impl_expression(self):
        return self.impl_expression_operand(self.value)


class DEName(DEBase):
    """DEName(name)
       DEName name expression.
    """

    def __init__(self, name, globals_d=None):
        self.name = name
        self.globals_d = globals_d

    def evaluate(self):
        globals_d = self.globals_d
        if globals_d is None:
            globals_d = globals()
        return globals_d[self.name]

    def impl_expression(self):
        return self.name


class DEUnaryOperator(DEBase):
    """DEUnaryOperator(operand)
       Abstract base class for unary operators.
    """

    def __init__(self, operand):
        self.operand = operand

    def evaluate(self):
        value = self.evaluate_operand(self.operand)
        return self.unary_operation(value)

    @abc.abstractmethod
    def unary_operation(self, value):
        """unary_operation(value) -> result"""

        pass


class DEAbs(DEUnaryOperator):
    """'abs' unary operator."""

    def unary_operation(self, value):
        return abs(value)

    def impl_expression(self):
        return "abs({})".format(self.impl_expression_operand(self.operand, wrap=False))


class DEPos(DEUnaryOperator):
    """'pos' unary operator."""

    def unary_operation(self, value):
        return +value

    def impl_expression(self):
        return "+{}".format(self.impl_expression_operand(self.operand))


class DENeg(DEUnaryOperator):
    """'neg' unary operator."""

    def unary_operation(self, value):
        return -value

    def impl_expression(self):
        return "-{}".format(self.impl_expression_operand(self.operand))


class DELen(DEUnaryOperator):
    """'len' unary operator."""

    def unary_operation(self, value):
        return len(value)

    def impl_expression(self):
        return "len({})".format(self.impl_expression_operand(self.operand, wrap=False))


class DEStr(DEUnaryOperator):
    """'str' unary operator."""

    def unary_operation(self, value):
        return str(value)

    def impl_expression(self):
        return "str({})".format(self.impl_expression_operand(self.operand, wrap=False))


class DERepr(DEUnaryOperator):
    """'repr' unary operator."""

    def unary_operation(self, value):
        return repr(value)

    def impl_expression(self):
        return "repr({})".format(self.impl_expression_operand(self.operand, wrap=False))


class DENot(DEUnaryOperator):
    """'not' unary operator."""

    def unary_operation(self, value):
        return not value

    def impl_expression(self):
        return "not {}".format(self.impl_expression_operand(self.operand))


class DECall(DEUnaryOperator):
    """'call' unary operator."""

    def __init__(self, operand, p_args, n_args):
        super().__init__(operand=operand)
        self.p_args = p_args
        self.n_args = n_args

    def unary_operation(self, value):
        return value(*self.p_args, **self.n_args)

    def impl_expression(self):
        l_args = []
        if self.p_args:
            l_args.extend(repr(a) for a in self.p_args)
        if self.n_args:
            l_args.extend("{}={!r}".format(k, v) for k, v in self.n_args)
        return "{}({})".format(self.impl_expression_operand(self.operand), ', '.join(l_args))


class DEBinaryOperator(DEBase):
    """DEBinaryOperator(operand)
       Abstract base class for binary operators.
    """
    BINOP_SYMBOL = None

    def __init__(self, left_operand, right_operand):
        self.left_operand = left_operand
        self.right_operand = right_operand

    def evaluate(self):
        left_value = self.evaluate_operand(self.left_operand)
        right_value = self.evaluate_operand(self.right_operand)
        return self.binary_operation(left_value, right_value)

    @abc.abstractmethod
    def binary_operation(self, left_value, right_value):
        """binary_operation(left_value, right_value) -> result"""

        pass

    def __repr__(self):
        return "{}(left_operand={!r}, right_operand={!r})".format(
            self.__class__.__name__, self.left_operand, self.right_operand)

    def impl_expression(self):
        return "{} {} {}".format(
            self.impl_expression_operand(self.left_operand),
            self.BINOP_SYMBOL,
            self.impl_expression_operand(self.right_operand))


class DEAdd(DEBinaryOperator):
    """'add' binary operator."""
    BINOP_SYMBOL = '+'

    def binary_operation(self, left_value, right_value):
        return left_value + right_value


class DEMul(DEBinaryOperator):
    """'mul' binary operator."""
    BINOP_SYMBOL = '*'

    def binary_operation(self, left_value, right_value):
        return left_value * right_value


class DESub(DEBinaryOperator):
    """'sub' binary operator."""
    BINOP_SYMBOL = '-'

    def binary_operation(self, left_value, right_value):
        return left_value - right_value


class DETrueDiv(DEBinaryOperator):
    """'truediv' binary operator."""
    BINOP_SYMBOL = '/'

    def binary_operation(self, left_value, right_value):
        return left_value / right_value


class DEFloorDiv(DEBinaryOperator):
    """'floordiv' binary operator."""
    BINOP_SYMBOL = '//'

    def binary_operation(self, left_value, right_value):
        return left_value // right_value


class DEMod(DEBinaryOperator):
    """'mod' binary operator."""
    BINOP_SYMBOL = '%'

    def binary_operation(self, left_value, right_value):
        return left_value % right_value


class DEDivMod(DEBinaryOperator):
    """'divmod' binary operator."""

    def binary_operation(self, left_value, right_value):
        return divmod(left_value, right_value)

    def impl_expression(self):
        return "divmod({}, {})".format(
            self.impl_expression_operand(self.left_operand, wrap=False),
            self.impl_expression_operand(self.right_operand, wrap=False))


class DEPow(DEBinaryOperator):
    """'pow' binary operator."""
    BINOP_SYMBOL = '**'

    def binary_operation(self, left_value, right_value):
        return left_value ** right_value


class DEEq(DEBinaryOperator):
    """'eq' binary operator."""
    BINOP_SYMBOL = '=='

    def binary_operation(self, left_value, right_value):
        return left_value == right_value


class DENe(DEBinaryOperator):
    """'ne' binary operator."""
    BINOP_SYMBOL = '!='

    def binary_operation(self, left_value, right_value):
        return left_value != right_value


class DELt(DEBinaryOperator):
    """'lt' binary operator."""
    BINOP_SYMBOL = '<'

    def binary_operation(self, left_value, right_value):
        return left_value < right_value


class DELe(DEBinaryOperator):
    """'le' binary operator."""
    BINOP_SYMBOL = '<='

    def binary_operation(self, left_value, right_value):
        return left_value <= right_value


class DEGt(DEBinaryOperator):
    """'gt' binary operator."""
    BINOP_SYMBOL = '>'

    def binary_operation(self, left_value, right_value):
        return left_value > right_value


class DEGe(DEBinaryOperator):
    """'ge' binary operator."""
    BINOP_SYMBOL = '>='

    def binary_operation(self, left_value, right_value):
        return left_value >= right_value


class DEAnd(DEBinaryOperator):
    """'and' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value and right_value

    def expression(self):
        return "{} and {}".format(
            self.impl_expression_operand(self.left_operand),
            self.impl_expression_operand(self.right_operand))


class DEGetattr(DEUnaryOperator):
    """'getattr' binary operator."""
    def __init__(self, operand, attr_name):
        super().__init__(operand)
        self.attr_name = attr_name

    def unary_operation(self, operand):
        return getattr(operand, self.attr_name)

    def impl_expression(self):
        operand = self.impl_expression_operand(self.operand)
        fmt = "{}.{}"
        return fmt.format(operand, self.attr_name)


class DEGetitem(DEBinaryOperator):
    """'getitem' binary operator."""

    def binary_operation(self, left, right):
        return left[right]

    def impl_expression(self):
        left = self.impl_expression_operand(self.left_operand)
        right = self.impl_expression_operand(self.right_operand, wrap=False)
        fmt = "{}[{}]"
        return fmt.format(left, right)


class DEContains(DEBinaryOperator):
    """'in' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value in right_value

    def impl_expression(self):
        return "{} in {}".format(
            self.impl_expression_operand(self.left_operand),
            self.impl_expression_operand(self.right_operand))


class DEOr(DEBinaryOperator):
    """'or' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value or right_value

# from . import serializer
# from .subclasses import subclasses
# text_serializer_module = getattr(serializer, 'text_serializer', None)
# if text_serializer_module is not None:
#     def _deferred_expression_text_encode(deferred_expression):
#         """_deferred_expression_text_encode(deferred_expression)
#            ConfigObj/Daikon encoder for Validator instances
#         """
#         return repr(deferred_expression)
#
#
#     def _deferred_expression_text_decode(type_name, repr_data):  # pylint: disable=W0613
#         """_deferred_expression_text_decode(deferred_expression_name, arguments)
#            ConfigObj/Daikon decoder for Validator instances
#         """
#         globals_d = {}
#         for subclass in subclasses(DEBase, include_self=False):
#             globals_d[subclass.__name__] = subclass
#         globals_d['len'] = len
#         globals_d['str'] = str
#         globals_d['repr'] = repr
#         return unrepr(repr_data, globals_d)
#
#
#     text_serializer_module.TextSerializer.codec_catalog().add_codec(
#         class_=DEBase,
#         encode=_deferred_expression_text_encode,
#         decode=_deferred_expression_text_decode,
#     )

