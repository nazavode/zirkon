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
Implementation of the DE_Base class for deferred evaluation of expressions.
"""

__author__ = "Simone Campagna"
__all__ = [
    'DE_Base',
    'DE_BinaryOperator',
    'DE_UnaryOperator',
    'DE_Const',
    'DE_Abs',
    'DE_Pos',
    'DE_Neg',
    'DE_Add',
    'DE_Sub',
    'DE_Mul',
    'DE_TrueDiv',
    'DE_FloorDiv',
    'DE_Mod',
    'DE_DivMod',
    'DE_Pow',
    'DE_Eq',
    'DE_Ne',
    'DE_Lt',
    'DE_Le',
    'DE_Gt',
    'DE_Ge',
    'DE_And',
    'DE_Or',
    'DE_Not',
    'DE_Len',
    'DE_Str',
    'DE_Repr',
    'DE_Getattr',
    'DE_Getitem',
    'DE_Call',
]

import abc


class DE_Base(metaclass=abc.ABCMeta):
    """DE_Base()
       Abstract base class to compose generic expressions.
       Concrete classes must implement the evaluate() method.
    """

    @abc.abstractmethod
    def evaluate(self):
        """evaluate() -> expression value"""
        pass

    # unary mathematical operators:
    def __abs__(self):
        return DE_Abs(self)

    def __pos__(self):
        return DE_Pos(self)

    def __neg__(self):
        return DE_Neg(self)

    # binary mathematical operators:
    def __add__(self, other):
        return DE_Add(self, other)

    def __radd__(self, other):
        return DE_Add(other, self)

    def __sub__(self, other):
        return DE_Sub(self, other)

    def __rsub__(self, other):
        return DE_Sub(other, self)

    def __mul__(self, other):
        return DE_Mul(self, other)

    def __rmul__(self, other):
        return DE_Mul(other, self)

    def __truediv__(self, other):
        return DE_TrueDiv(self, other)

    def __rtruediv__(self, other):
        return DE_TrueDiv(other, self)

    def __floordiv__(self, other):
        return DE_FloorDiv(self, other)

    def __rfloordiv__(self, other):
        return DE_FloorDiv(other, self)

    def __mod__(self, other):
        return DE_Mod(self, other)

    def __rmod__(self, other):
        return DE_Mod(other, self)

    def __divmod__(self, other):
        return DE_DivMod(self, other)

    def __rdivmod__(self, other):
        return DE_DivMod(other, self)

    def __pow__(self, other):
        return DE_Pow(self, other)

    def __rpow__(self, other):
        return DE_Pow(other, self)

    # binary comparison operators:
    def __eq__(self, other):
        return DE_Eq(self, other)

    def __req__(self, other):
        return DE_Eq(other, self)

    def __ne__(self, other):
        return DE_Ne(self, other)

    def __rne__(self, other):
        return DE_Ne(other, self)

    def __lt__(self, other):
        return DE_Lt(self, other)

    def __rlt__(self, other):
        return DE_Ge(other, self)

    def __le__(self, other):
        return DE_Le(self, other)

    def __rle__(self, other):
        return DE_Gt(self, other)

    def __gt__(self, other):
        return DE_Gt(self, other)

    def __rgt__(self, other):
        return DE_Le(self, other)

    def __ge__(self, other):
        return DE_Ge(self, other)

    def __rge__(self, other):
        return DE_Lt(self, other)

    # Call:
    def __call__(self, *p_args, **n_args):
        return DE_Call(self, p_args, n_args)

    # Get attribute:
    def __getattr__(self, attr_name):
        return DE_Getattr(self, attr_name)

    # Get item:
    def __getitem__(self, item):
        return DE_Getitem(self, item)

    # utilities:
    @classmethod
    def evaluate_operand(cls, operand):
        """evaluate_operand() -> operand value"""
        if isinstance(operand, DE_Base):
            return operand.evaluate()
        else:
            return operand


class DE_Const(DE_Base):
    """DE_Const(value)
       DE_Const value expression.
    """

    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.evaluate_operand(self.value)


class DE_UnaryOperator(DE_Base):
    """DE_UnaryOperator(operand)
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


class DE_Abs(DE_UnaryOperator):
    """'abs' unary operator."""

    def unary_operation(self, value):
        return abs(value)


class DE_Pos(DE_UnaryOperator):
    """'pos' unary operator."""

    def unary_operation(self, value):
        return +value


class DE_Neg(DE_UnaryOperator):
    """'neg' unary operator."""

    def unary_operation(self, value):
        return -value


class DE_Len(DE_UnaryOperator):
    """'len' unary operator."""

    def unary_operation(self, value):
        return len(value)


class DE_Str(DE_UnaryOperator):
    """'str' unary operator."""

    def unary_operation(self, value):
        return str(value)


class DE_Repr(DE_UnaryOperator):
    """'repr' unary operator."""

    def unary_operation(self, value):
        return repr(value)


class DE_Not(DE_UnaryOperator):
    """'not' unary operator."""
    def unary_operation(self, value):
        return not value


class DE_Call(DE_UnaryOperator):
    """'call' unary operator."""

    def __init__(self, operand, p_args, n_args):
        super().__init__(operand=operand)
        self.p_args = p_args
        self.n_args = n_args

    def unary_operation(self, value):
        return value(*self.p_args, **self.n_args)


class DE_BinaryOperator(DE_Base):
    """DE_BinaryOperator(operand)
       Abstract base class for binary operators.
    """

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


class DE_Add(DE_BinaryOperator):
    """'add' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value + right_value


class DE_Mul(DE_BinaryOperator):
    """'mul' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value * right_value


class DE_Sub(DE_BinaryOperator):
    """'sub' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value - right_value


class DE_TrueDiv(DE_BinaryOperator):
    """'truediv' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value / right_value


class DE_FloorDiv(DE_BinaryOperator):
    """'floordiv' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value // right_value


class DE_Mod(DE_BinaryOperator):
    """'mod' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value % right_value


class DE_DivMod(DE_BinaryOperator):
    """'divmod' binary operator."""

    def binary_operation(self, left_value, right_value):
        return divmod(left_value, right_value)


class DE_Pow(DE_BinaryOperator):
    """'pow' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value ** right_value


class DE_Eq(DE_BinaryOperator):
    """'eq' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value == right_value


class DE_Ne(DE_BinaryOperator):
    """'ne' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value != right_value


class DE_Lt(DE_BinaryOperator):
    """'lt' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value < right_value


class DE_Le(DE_BinaryOperator):
    """'le' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value <= right_value


class DE_Gt(DE_BinaryOperator):
    """'gt' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value > right_value


class DE_Ge(DE_BinaryOperator):
    """'ge' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value >= right_value


class DE_And(DE_BinaryOperator):
    """'and' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value and right_value


class DE_Or(DE_BinaryOperator):
    """'or' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value or right_value


class DE_Getattr(DE_BinaryOperator):
    """'getattr' binary operator."""

    def binary_operation(self, left, right):
        return getattr(left, right)


class DE_Getitem(DE_BinaryOperator):
    """'getitem' binary operator."""

    def binary_operation(self, left, right):
        return left[right]

