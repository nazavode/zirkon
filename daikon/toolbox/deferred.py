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
Implementation of the Deferred abstract base class for deferred evaluation of python expressions.
"""

__author__ = "Simone Campagna"
__all__ = [
    'Deferred',
    'DBinaryOperator',
    'DUnaryOperator',
    'DName',
    'DConst',
    'DAbs',
    'DPos',
    'DNeg',
    'DAdd',
    'DSub',
    'DMul',
    'DTrueDiv',
    'DFloorDiv',
    'DMod',
    'DDivMod',
    'DPow',
    'DEq',
    'DNe',
    'DLt',
    'DLe',
    'DGt',
    'DGe',
    'DAnd',
    'DOr',
    'DNot',
    'DLen',
    'DStr',
    'DRepr',
    'DContains',
    'DGetattr',
    'DGetitem',
    'DCall',
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


class Deferred(metaclass=abc.ABCMeta):
    """Deferred()
       Abstract base class to compose generic expressions.
       Concrete classes must implement the evaluate(globals_d=None) method.
    """
    PRIORITY = {
        'DConst': 100000,
        'DName': 100000,
        'DOr': 1,
        'DAnd': 2,
        'DNot': 3,
        'DContains': 4,
        # 'DIs': 5,
        'DLt': 6,
        'DLe': 6,
        'DGt': 6,
        'DGe': 6,
        'DEq': 6,
        'DNe': 6,
        # 'DBitwiseOr': 7,
        # 'DBitwiseXOr': 8,
        # 'DBitwiseAnd': 9,
        # 'DLeftShift': 10,
        # 'DRightShift': 10,
        'DAdd': 11,
        'DSub': 11,
        'DMul': 12,
        'DTrueDiv': 12,
        'DFloorDiv': 12,
        'DMod': 12,
        'DDivMod': 12,
        'DPos': 13,
        'DNeg': 13,
        # 'DBitwiseNot': 14,
        'DPow': 15,
        'DCall': 16,
        'DGetitem': 17,
        'DGetattr': 18,
    }
    RIGHT_ASSOCIATIVITY = {
        'DPow': True
    }

    @abc.abstractmethod
    def evaluate(self, globals_d=None):
        """evaluate(globals_d=None) -> expression value"""
        pass

    @abc.abstractmethod
    def __reduce__(self):
        pass

    def expression(self):
        """expression() -> python expression representation"""
        return self._impl_expression_wrap(wrap=False)

    def _impl_expression_wrap(self, wrap):
        """_impl_expression_wrap(wrap) -> expression representation
           If 'wrap' puts output in parenthesis.
        """
        expression = self._impl_expression()
        if wrap:
            return '(' + expression + ')'
        else:
            return expression

    @abc.abstractmethod
    def _impl_expression(self):
        """_impl_expression() -> expression representation."""
        pass

    def _wrap(self, expression, wrap):  # pylint: disable=R0201
        """wrap(expression, wrap) -> [wrapped] expression"""

    # __str__:
    @abc.abstractmethod
    def __str__(self):
        pass

    # __repr__:
    def __repr__(self):
        return self.expression()

    # unary mathematical operators:
    def __abs__(self):
        return DAbs(self)

    def __pos__(self):
        return DPos(self)

    def __neg__(self):
        return DNeg(self)

    # binary mathematical operators:
    def __add__(self, other):
        return DAdd(self, other)

    def __radd__(self, other):
        return DAdd(other, self)

    def __sub__(self, other):
        return DSub(self, other)

    def __rsub__(self, other):
        return DSub(other, self)

    def __mul__(self, other):
        return DMul(self, other)

    def __rmul__(self, other):
        return DMul(other, self)

    def __truediv__(self, other):
        return DTrueDiv(self, other)

    def __rtruediv__(self, other):
        return DTrueDiv(other, self)

    def __floordiv__(self, other):
        return DFloorDiv(self, other)

    def __rfloordiv__(self, other):
        return DFloorDiv(other, self)

    def __mod__(self, other):
        return DMod(self, other)

    def __rmod__(self, other):
        return DMod(other, self)

    def __divmod__(self, other):
        return DDivMod(self, other)

    def __rdivmod__(self, other):
        return DDivMod(other, self)

    def __pow__(self, other):
        return DPow(self, other)

    def __rpow__(self, other):
        return DPow(other, self)

    # binary comparison operators:
    def __eq__(self, other):
        return DEq(self, other)

    def __req__(self, other):
        return DEq(other, self)

    def __ne__(self, other):
        return DNe(self, other)

    def __rne__(self, other):
        return DNe(other, self)

    def __lt__(self, other):
        return DLt(self, other)

    def __rlt__(self, other):
        return DGe(other, self)

    def __le__(self, other):
        return DLe(self, other)

    def __rle__(self, other):
        return DGt(self, other)

    def __gt__(self, other):
        return DGt(self, other)

    def __rgt__(self, other):
        return DLe(self, other)

    def __ge__(self, other):
        return DGe(self, other)

    def __rge__(self, other):
        return DLt(self, other)

    def __contains__(self, other):
        return DContains(self, other)

    # Call:
    def __call__(self, *p_args, **n_args):
        return DCall(functor=self, p_args=p_args, n_args=n_args)

    # Get attribute:
    def __getattr__(self, attr_name):
        return DGetattr(self, attr_name)

    # Get item:
    def __getitem__(self, item):
        return DGetitem(self, item)

    # utilities:
    @classmethod
    def _impl_evaluate_operand(cls, operand, globals_d):
        """_impl_evaluate_operand(operand, globals_d) -> operand value"""
        if isinstance(operand, Deferred):
            return operand.evaluate(globals_d=globals_d)
        else:
            return operand

    @classmethod
    def _impl_expression_lr_operand(cls, operand, wrap=None, right=None):
        """_impl_expression_operand(operand, wrap=None, right=None) -> operand value"""
        if isinstance(operand, Deferred):
            if wrap is None:
                p_operand = operand._priority()  # pylint: disable=W0212
                p_cls = cls._priority()
                if p_operand == p_cls:
                    right_associativity = cls._right_associativity()
                    if right_associativity:
                        wrap = not right
                    else:
                        wrap = right
                else:
                    wrap = (p_operand < p_cls)
            return operand._impl_expression_wrap(wrap=wrap)  # pylint: disable=W0212
        else:
            return repr(operand)

    @classmethod
    def _impl_expression_left_operand(cls, operand, wrap=None):
        """_impl_expression_left_operand(operand, wrap=None) -> operand value"""
        return cls._impl_expression_lr_operand(operand, wrap=wrap, right=False)

    @classmethod
    def _impl_expression_right_operand(cls, operand, wrap=None):
        """_impl_expression_left_operand(operand, wrap=None) -> operand value"""
        return cls._impl_expression_lr_operand(operand, wrap=wrap, right=True)

    @classmethod
    def _impl_expression_operand(cls, operand, wrap=None):
        """_impl_expression_left_operand(operand, wrap=None) -> operand value"""
        return cls._impl_expression_lr_operand(operand, wrap=wrap, right=None)

    @classmethod
    def _priority(cls):
        """_priority() -> priority"""
        return cls.PRIORITY.get(cls.__name__, 1000)

    @classmethod
    def _right_associativity(cls):
        """_right_associativity() -> right_associativity"""
        return cls.RIGHT_ASSOCIATIVITY.get(cls.__name__, False)


class DConst(Deferred):
    """DConst(value)
       DConst value expression.
    """

    def __init__(self, value):
        self.value = value

    def __reduce__(self):
        return (self.__class__, (self.value,))

    def __str__(self):
        return "{}({!r})".format(self.__class__.__name__, self.value)

    def evaluate(self, globals_d=None):
        return self._impl_evaluate_operand(operand=self.value, globals_d=globals_d)

    def _impl_expression(self):
        return self._impl_expression_operand(self.value)


class DName(Deferred):
    """DName(name)
       DName name expression.
    """

    def __init__(self, name, globals_d=None):
        self.name = name
        self.globals_d = globals_d

    def __reduce__(self):
        return (self.__class__, (self.name, self.globals_d))

    def __str__(self):
        if self.globals_d is None:
            gstring = ""
        else:
            gstring = ", {!r}".format(self.globals_d)
        return "{}({!r}{})".format(self.__class__.__name__, self.name, gstring)

    def evaluate(self, globals_d=None):
        if globals_d is None:
            globals_d = {}
        else:
            globals_d = globals_d.copy()
        if self.globals_d is not None:
            globals_d.update(self.globals_d)
        if self.name not in globals_d:
            raise NameError("name {!r} is not defined".format(self.name))
        return globals_d[self.name]

    def _impl_expression(self):
        return self.name


class DCall(Deferred):
    """'call' operator."""

    def __init__(self, functor, p_args=None, n_args=None):
        super().__init__()
        self.functor = functor
        if p_args is None:
            p_args = ()
        self.p_args = p_args
        if n_args is None:
            n_args = {}
        self.n_args = n_args

    def __reduce__(self):
        return (self.__class__, (self.functor, self.p_args, self.n_args))

    def __str__(self):
        return "{}({!r}, {!r}, {!r})".format(
            self.__class__.__name__,
            self.functor,
            self.p_args,
            self.n_args
        )

    def evaluate(self, globals_d=None):
        value = self._impl_evaluate_operand(operand=self.functor, globals_d=globals_d)
        p_args = [self._impl_evaluate_operand(operand, globals_d) for operand in self.p_args]
        n_args = {key: self._impl_evaluate_operand(operand, globals_d) for key, operand in self.n_args.items()}
        return value(*p_args, **n_args)

    def _impl_expression(self):
        l_args = []
        if self.p_args:
            l_args.extend(self._impl_expression_operand(a) for a in self.p_args)
        if self.n_args:
            l_args.extend("{}={}".format(k, self._impl_expression_operand(v)) for k, v in self.n_args.items())
        return "{}({})".format(self._impl_expression_operand(self.functor), ', '.join(l_args))


class DUnaryOperator(Deferred):
    """DUnaryOperator(operand)
       Abstract base class for unary operators.
    """

    def __init__(self, operand):
        self.operand = operand

    def __reduce__(self):
        return (self.__class__, (self.operand,))

    def __str__(self):
        return "{}({!r})".format(self.__class__.__name__, self.operand)

    def evaluate(self, globals_d=None):
        value = self._impl_evaluate_operand(operand=self.operand, globals_d=globals_d)
        return self._impl_unary_operation(value)

    @abc.abstractmethod
    def _impl_unary_operation(self, value):
        """_impl_unary_operation(value) -> result"""

        pass


class DAbs(DUnaryOperator):
    """'abs' unary operator."""

    def _impl_unary_operation(self, value):
        return abs(value)

    def _impl_expression(self):
        return "abs({})".format(self._impl_expression_operand(self.operand, wrap=False))


class DPos(DUnaryOperator):
    """'pos' unary operator."""

    def _impl_unary_operation(self, value):
        return +value

    def _impl_expression(self):
        return "+{}".format(self._impl_expression_operand(self.operand))


class DNeg(DUnaryOperator):
    """'neg' unary operator."""

    def _impl_unary_operation(self, value):
        return -value

    def _impl_expression(self):
        return "-{}".format(self._impl_expression_operand(self.operand))


class DLen(DUnaryOperator):
    """'len' unary operator."""

    def _impl_unary_operation(self, value):
        return len(value)

    def _impl_expression(self):
        return "len({})".format(self._impl_expression_operand(self.operand, wrap=False))


class DStr(DUnaryOperator):
    """'str' unary operator."""

    def _impl_unary_operation(self, value):
        return str(value)

    def _impl_expression(self):
        return "str({})".format(self._impl_expression_operand(self.operand, wrap=False))


class DRepr(DUnaryOperator):
    """'repr' unary operator."""

    def _impl_unary_operation(self, value):
        return repr(value)

    def _impl_expression(self):
        return "repr({})".format(self._impl_expression_operand(self.operand, wrap=False))


class DNot(DUnaryOperator):
    """'not' unary operator."""

    def _impl_unary_operation(self, value):
        return not value

    def _impl_expression(self):
        return "not {}".format(self._impl_expression_operand(self.operand))


class DBinaryOperator(Deferred):
    """DBinaryOperator(operand)
       Abstract base class for binary operators.
    """
    BINOP_SYMBOL = None

    def __init__(self, left_operand, right_operand):
        self.left_operand = left_operand
        self.right_operand = right_operand

    def evaluate(self, globals_d=None):
        left_value = self._impl_evaluate_operand(operand=self.left_operand, globals_d=globals_d)
        right_value = self._impl_evaluate_operand(operand=self.right_operand, globals_d=globals_d)
        return self._impl_binary_operation(left_value, right_value)

    @abc.abstractmethod
    def _impl_binary_operation(self, left_value, right_value):
        """_impl_binary_operation(left_value, right_value) -> result"""

        pass

    def __reduce__(self):
        return (self.__class__, (self.left_operand, self.right_operand))

    def __str__(self):
        return "{}({!r}, {!r})".format(
            self.__class__.__name__, self.left_operand, self.right_operand)

    def _impl_expression(self):
        return "{} {} {}".format(
            self._impl_expression_left_operand(self.left_operand),
            self.BINOP_SYMBOL,
            self._impl_expression_right_operand(self.right_operand))


class DAdd(DBinaryOperator):
    """'add' binary operator."""
    BINOP_SYMBOL = '+'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value + right_value


class DMul(DBinaryOperator):
    """'mul' binary operator."""
    BINOP_SYMBOL = '*'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value * right_value


class DSub(DBinaryOperator):
    """'sub' binary operator."""
    BINOP_SYMBOL = '-'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value - right_value


class DTrueDiv(DBinaryOperator):
    """'truediv' binary operator."""
    BINOP_SYMBOL = '/'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value / right_value


class DFloorDiv(DBinaryOperator):
    """'floordiv' binary operator."""
    BINOP_SYMBOL = '//'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value // right_value


class DMod(DBinaryOperator):
    """'mod' binary operator."""
    BINOP_SYMBOL = '%'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value % right_value


class DDivMod(DBinaryOperator):
    """'divmod' binary operator."""

    def _impl_binary_operation(self, left_value, right_value):
        return divmod(left_value, right_value)

    def _impl_expression(self):
        return "divmod({}, {})".format(
            self._impl_expression_left_operand(self.left_operand, wrap=False),
            self._impl_expression_right_operand(self.right_operand, wrap=False))


class DPow(DBinaryOperator):
    """'pow' binary operator."""
    BINOP_SYMBOL = '**'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value ** right_value


class DEq(DBinaryOperator):
    """'eq' binary operator."""
    BINOP_SYMBOL = '=='

    def _impl_binary_operation(self, left_value, right_value):
        return left_value == right_value


class DNe(DBinaryOperator):
    """'ne' binary operator."""
    BINOP_SYMBOL = '!='

    def _impl_binary_operation(self, left_value, right_value):
        return left_value != right_value


class DLt(DBinaryOperator):
    """'lt' binary operator."""
    BINOP_SYMBOL = '<'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value < right_value


class DLe(DBinaryOperator):
    """'le' binary operator."""
    BINOP_SYMBOL = '<='

    def _impl_binary_operation(self, left_value, right_value):
        return left_value <= right_value


class DGt(DBinaryOperator):
    """'gt' binary operator."""
    BINOP_SYMBOL = '>'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value > right_value


class DGe(DBinaryOperator):
    """'ge' binary operator."""
    BINOP_SYMBOL = '>='

    def _impl_binary_operation(self, left_value, right_value):
        return left_value >= right_value


class DAnd(DBinaryOperator):
    """'and' binary operator."""

    def _impl_binary_operation(self, left_value, right_value):
        return left_value and right_value

    def expression(self):
        return "{} and {}".format(
            self._impl_expression_left_operand(self.left_operand),
            self._impl_expression_right_operand(self.right_operand))


class DGetattr(DUnaryOperator):
    """'getattr' binary operator."""
    def __init__(self, operand, attr_name):
        super().__init__(operand)
        self.attr_name = attr_name

    def _impl_unary_operation(self, operand):
        return getattr(operand, self.attr_name)

    def _impl_expression(self):
        operand = self._impl_expression_operand(self.operand)
        fmt = "{}.{}"
        return fmt.format(operand, self.attr_name)


class DGetitem(DBinaryOperator):
    """'getitem' binary operator."""

    def _impl_binary_operation(self, left, right):
        return left[right]

    def _impl_expression(self):
        left = self._impl_expression_left_operand(self.left_operand)
        right = self._impl_expression_right_operand(self.right_operand, wrap=False)
        fmt = "{}[{}]"
        return fmt.format(left, right)


class DContains(DBinaryOperator):
    """'in' binary operator."""

    def _impl_binary_operation(self, left_value, right_value):
        return left_value in right_value

    def _impl_expression(self):
        return "{} in {}".format(
            self._impl_expression_left_operand(self.left_operand),
            self._impl_expression_right_operand(self.right_operand))


class DOr(DBinaryOperator):
    """'or' binary operator."""

    def _impl_binary_operation(self, left_value, right_value):
        return left_value or right_value