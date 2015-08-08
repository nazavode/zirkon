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
config.deferred
===============
Implementation of the Deferred class for deferred evaluation of expressions.
"""

__author__ = "Simone Campagna"

import abc


class Deferred(metaclass=abc.ABCMeta):
    """Deferred()
       Abstract base class to compose generic expressions.
       Concrete classes must implement the evaluate() method.
    """

    @abc.abstractmethod
    def evaluate(self):
        """evaluate() -> expression value"""
        pass

    # unary mathematical operators:
    def __abs__(self):
        return Abs(self)

    def __pos__(self):
        return Pos(self)

    def __neg__(self):
        return Neg(self)

    # binary mathematical operators:
    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return TrueDiv(self, other)

    def __rtruediv__(self, other):
        return TrueDiv(other, self)

    def __floordiv__(self, other):
        return FloorDiv(self, other)

    def __rfloordiv__(self, other):
        return FloorDiv(other, self)

    def __mod__(self, other):
        return Mod(self, other)

    def __rmod__(self, other):
        return Mod(other, self)

    def __divmod__(self, other):
        return DivMod(self, other)

    def __rdivmod__(self, other):
        return DivMod(other, self)

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)

    # binary comparison operators:
    def __eq__(self, other):
        return Eq(self, other)

    def __req__(self, other):
        return Eq(other, self)

    def __ne__(self, other):
        return Ne(self, other)

    def __rne__(self, other):
        return Ne(other, self)

    def __lt__(self, other):
        return Lt(self, other)

    def __rlt__(self, other):
        return Ge(other, self)

    def __le__(self, other):
        return Le(self, other)

    def __rle__(self, other):
        return Gt(self, other)

    def __gt__(self, other):
        return Gt(self, other)

    def __rgt__(self, other):
        return Le(self, other)

    def __ge__(self, other):
        return Ge(self, other)

    def __rge__(self, other):
        return Lt(self, other)

    # Call:
    def __call__(self, *p_args, **n_args):
        return Call(self, p_args, n_args)

    # Get attribute:
    def __getattr__(self, attr_name):
        return Getattr(self, attr_name)

    # utilities:
    @classmethod
    def evaluate_operand(cls, operand):
        """evaluate_operand() -> operand value"""
        if isinstance(operand, Deferred):
            return operand.evaluate()
        else:
            return operand


class Const(Deferred):
    """Const(value)
       Const value expression.
    """

    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.evaluate_operand(self.value)


class UnaryOperator(Deferred):
    """UnaryOperator(operand)
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


class Abs(UnaryOperator):
    """'abs' unary operator."""

    def unary_operation(self, value):
        return abs(value)


class Pos(UnaryOperator):
    """'pos' unary operator."""

    def unary_operation(self, value):
        return +value


class Neg(UnaryOperator):
    """'neg' unary operator."""

    def unary_operation(self, value):
        return -value


class Len(UnaryOperator):
    """'len' unary operator."""

    def unary_operation(self, value):
        return len(value)


class Str(UnaryOperator):
    """'str' unary operator."""

    def unary_operation(self, value):
        return str(value)


class Repr(UnaryOperator):
    """'repr' unary operator."""

    def unary_operation(self, value):
        return repr(value)


class Not(UnaryOperator):
    """'not' unary operator."""
    def unary_operation(self, value):
        return Not(value)


class Getattr(UnaryOperator):
    """'getattr' unary operator."""

    def __init__(self, operand, attr_name):
        super().__init__(operand=operand)
        self.attr_name = attr_name

    def unary_operation(self, value):
        return getattr(value, self.attr_name)


class Call(UnaryOperator):
    """'call' unary operator."""

    def __init__(self, operand, p_args, n_args):
        super().__init__(operand=operand)
        self.p_args = p_args
        self.n_args = n_args

    def unary_operation(self, value):
        return value(*self.p_args, **self.n_args)


class BinaryOperator(Deferred):
    """BinaryOperator(operand)
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


class Add(BinaryOperator):
    """'add' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value + right_value


class Mul(BinaryOperator):
    """'mul' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value * right_value


class Sub(BinaryOperator):
    """'sub' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value - right_value


class TrueDiv(BinaryOperator):
    """'truediv' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value / right_value


class FloorDiv(BinaryOperator):
    """'floordiv' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value // right_value


class Mod(BinaryOperator):
    """'mod' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value % right_value


class DivMod(BinaryOperator):
    """'divmod' binary operator."""

    def binary_operation(self, left_value, right_value):
        return divmod(left_value, right_value)


class Pow(BinaryOperator):
    """'pow' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value ** right_value


class Eq(BinaryOperator):
    """'eq' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value == right_value


class Ne(BinaryOperator):
    """'ne' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value != right_value


class Lt(BinaryOperator):
    """'lt' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value < right_value


class Le(BinaryOperator):
    """'le' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value <= right_value


class Gt(BinaryOperator):
    """'gt' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value > right_value


class Ge(BinaryOperator):
    """'ge' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value >= right_value


class And(BinaryOperator):
    """'and' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value and right_value


class Or(BinaryOperator):
    """'or' binary operator."""

    def binary_operation(self, left_value, right_value):
        return left_value or right_value


