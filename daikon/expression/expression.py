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
config.expression.expression
============================
Implementation of the Expression class
"""

__author__ = "Simone Campagna"

import abc


class Expression(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def evaluate(self):
        pass

    # unary mathematical operators:
    def __abs__(self):
        return Abs(self)

    def __pos__(self):
        return Pos(self)

    def __neg__(self):
        return Neg(self)

    # other unary operators:
#    def __len__(self):
#        return Len(self)
#
#    def __str__(self):
#        return Str(self)
#
#    def __repr__(self):
#        return Repr(self)

    # binary mathematical operators:
    def __add__(self, other):
        return Add(self, other)
    __radd__ = __add__

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
        return TrueDiv(Value(other), self)

    def __floordiv__(self, other):
        return FloorDiv(self, other)

    def __rfloordiv__(self, other):
        return FloorDiv(Value(other), self)

    def __mod__(self, other):
        return Mod(self, other)

    def __rmod__(self, other):
        return Mod(Value(other), self)

    def __divmod__(self, other):
        return DivMod(self, other)

    def __rdivmod__(self, other):
        return DivMod(Value(other), self)

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(Value(other), self)

    # binary comparison operators:
    def __eq__(self, other):
        return Eq(self, other)

    def __ne__(self, other):
        return Ne(self, other)

    def __lt__(self, other):
        return Lt(self, other)

    def __le__(self, other):
        return Le(self, other)

    def __gt__(self, other):
        return Gt(self, other)

    def __ge__(self, other):
        return Ge(self, other)

    # utilities:
    def evaluate_operand(self, operand):
        if isinstance(operand, Expression):
            return operand.evaluate()
        else:
            return operand

class Value(Expression):
    def __init__(self, value):
        self.value = value

    def evaluate(self):
        return self.evaluate_operand(self.value)

class UnaryOperator(Expression):
    def __init__(self, operand):
        self.operand = operand

    def evaluate(self):
        value = self.evaluate_operand(self.operand)
        return self.unary_operation(value)

    @abc.abstractmethod
    def unary_operation(self, value):
        pass

class Abs(UnaryOperator):
    def unary_operation(self, value):
        return abs(value)

class Pos(UnaryOperator):
    def unary_operation(self, value):
        return +value

class Neg(UnaryOperator):
    def unary_operation(self, value):
        return -value

class Len(UnaryOperator):
    def unary_operation(self, value):
        return len(value)

class Str(UnaryOperator):
    def unary_operation(self, value):
        return Str(value)

class Repr(UnaryOperator):
    def unary_operation(self, value):
        return Repr(value)

class BinaryOperator(Expression):
    def __init__(self, left_operand, right_operand):
        self.left_operand = left_operand
        self.right_operand = right_operand

    def evaluate(self):
        left_value = self.evaluate_operand(self.left_operand)
        right_value = self.evaluate_operand(self.right_operand)
        return self.binary_operation(left_value, right_value)

    @abc.abstractmethod
    def binary_operation(self, left_value, right_value):
        pass

class Add(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value + right_value

class Mul(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value * right_value

class Sub(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value - right_value

class TrueDiv(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value / right_value

class FloorDiv(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value // right_value

class Mod(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value % right_value

class DivMod(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return divmod(left_value, right_value)

class Pow(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value ** right_value

class Eq(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value == right_value

class Ne(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value != right_value

class Lt(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value <  right_value

class Le(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value <= right_value

class Gt(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value >  right_value

class Ge(BinaryOperator):
    def binary_operation(self, left_value, right_value):
        return left_value >= right_value


