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
Implementation of the Macro abstract base class for evaluation of Macros. A Macro is
a python expression whose binding and evaluation can be deferred.
"""

__author__ = "Simone Campagna"
__copyright__ = 'Copyright (c) 2015 Simone Campagna'
__license__ = 'Apache License Version 2.0'
__all__ = [
    'Macro', 'MBinaryOperator', 'MUnaryOperator', 'MName', 'MConst', 'MAbs',
    'MPos', 'MNeg', 'MAdd', 'MSub', 'MMul', 'MTrueDiv', 'MFloorDiv', 'MMod',
    'MDivMod', 'MPow', 'MEq', 'MNe', 'MLt', 'MLe', 'MGt', 'MGe', 'MAnd', 'MOr',
    'MNot', 'MLen', 'MStr', 'MRepr', 'MContains', 'MGetattr', 'MGetitem', 'MCall',
]

import abc


class Macro(metaclass=abc.ABCMeta):
    """Abstract base class to compose generic expressions.
       Concrete classes must implement the evaluate(globals_d=None) method.
    """
    PRIORITY = {
        'MConst': 100000, 'MName': 100000, 'MOr': 1, 'MAnd': 2, 'MNot': 3, 'MContains': 4,
        # 'MIs': 5,
        'MLt': 6, 'MLe': 6, 'MGt': 6, 'MGe': 6, 'MEq': 6, 'MNe': 6,
        # 'MBitwiseOr': 7, 'MBitwiseXOr': 8, 'MBitwiseAnd': 9, 'MLeftShift': 10, 'MRightShift': 10,
        'MAdd': 11, 'MSub': 11, 'MMul': 12, 'MTrueDiv': 12, 'MFloorDiv': 12, 'MMod': 12,
        'MDivMod': 12, 'MPos': 13, 'MNeg': 13,
        # 'MBitwiseNot': 14,
        'MPow': 15, 'MCall': 16, 'MGetitem': 17, 'MGetattr': 18,
    }
    RIGHT_ASSOCIATIVITY = {
        'MPow': True
    }

    @abc.abstractmethod
    def evaluate(self, globals_d=None):
        """Evaluates the object using globals_d for name lookup.

        Parameters
        ----------
        globals_d: dict, optional
            the globals dictionary

        Raises
        -------
        NameError
            name not found

        Returns
        -------
        |any|
            the evaluated value
        """
        raise NotImplementedError

    @abc.abstractmethod
    def __reduce__(self):
        raise NotImplementedError

    def unparse(self):
        """Unparses the expression returning its python representation.
           It correctly handles operator priority and associativity.

           Returns
           -------
           str
               the unparsed expression
        """
        return self._impl_unparse_wrap(wrap=False)

    def _impl_unparse_wrap(self, wrap):
        """If 'wrap' puts output in parenthesis.

           Parameters
           ----------
           wrap: bool
               determines if enclosing braces are required

           Returns
           -------
           str
               the expression
        """
        expression = self._impl_unparse()
        if wrap:
            return '(' + expression + ')'
        else:
            return expression

    @abc.abstractmethod
    def _impl_unparse(self):
        """Implementation of the unparse method.

           Returns
           -------
           str
               the expression
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _impl_tree(self):
        """Implementation of the __str__ method. Returns an expression
           showing the tree structure of the object.

           Returns
           -------
           str
               the tree expression
        """
        raise NotImplementedError

    def __str__(self):
        return self._impl_tree()

    def __repr__(self):
        return self.unparse()

    # unary mathematical operators:
    def __abs__(self):
        return MAbs(self)

    def __pos__(self):
        return MPos(self)

    def __neg__(self):
        return MNeg(self)

    # binary mathematical operators:
    def __add__(self, other):
        return MAdd(self, other)

    def __radd__(self, other):
        return MAdd(other, self)

    def __sub__(self, other):
        return MSub(self, other)

    def __rsub__(self, other):
        return MSub(other, self)

    def __mul__(self, other):
        return MMul(self, other)

    def __rmul__(self, other):
        return MMul(other, self)

    def __truediv__(self, other):
        return MTrueDiv(self, other)

    def __rtruediv__(self, other):
        return MTrueDiv(other, self)

    def __floordiv__(self, other):
        return MFloorDiv(self, other)

    def __rfloordiv__(self, other):
        return MFloorDiv(other, self)

    def __mod__(self, other):
        return MMod(self, other)

    def __rmod__(self, other):
        return MMod(other, self)

    def __divmod__(self, other):
        return MDivMod(self, other)

    def __rdivmod__(self, other):
        return MDivMod(other, self)

    def __pow__(self, other):
        return MPow(self, other)

    def __rpow__(self, other):
        return MPow(other, self)

    # binary comparison operators:
    def __eq__(self, other):
        return MEq(self, other)

    def __ne__(self, other):
        return MNe(self, other)

    def __lt__(self, other):
        return MLt(self, other)

    def __le__(self, other):
        return MLe(self, other)

    def __gt__(self, other):
        return MGt(self, other)

    def __ge__(self, other):
        return MGe(self, other)

    # cannot work: immediately converted to bool
    # def __contains__(self, other):
    #     return MContains(self, other)

    def __call__(self, *p_args, **n_args):
        return MCall(functor=self, p_args=p_args, n_args=n_args)

    def __getattr__(self, attr_name):
        return MGetattr(self, attr_name)

    def __getitem__(self, item):
        return MGetitem(self, item)

    # utilities:
    @classmethod
    def _impl_evaluate_operand(cls, operand, globals_d):
        """Classmethod to evaluate an operand.

           Parameters
           ----------
           operand: |any|
               the operand to evaluate (a Macro object or other value)
           globals_d: dict
               the globals dictionary

           Returns
           -------
           |any|
               the evaluated operand
        """
        if isinstance(operand, Macro):
            return operand.evaluate(globals_d=globals_d)
        else:
            return operand

    @classmethod
    def _impl_unparse_lr_operand(cls, operand, wrap=None, right=None):
        """Classmethod to unparse an operand for a binary operator, handling associativity.

           Parameters
           ----------
           operand: |any|
               the operand to unparse (a Macro object or other value)
           wrap: bool
               if True the expression must be enclosed in braces
           right: bool
               if True right associativity is required

           Returns
           -------
           str
               the unparsed expression
        """
        if isinstance(operand, Macro):
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
            return operand._impl_unparse_wrap(wrap=wrap)  # pylint: disable=W0212
        else:
            return repr(operand)

    @classmethod
    def _impl_unparse_left_operand(cls, operand, wrap=None):
        """Classmethod to unparse the left operand, handling associativity.

           Parameters
           ----------
           operand: |any|
               the operand to unparse (a Macro object or other value)
           wrap: bool
               if True the expression must be enclosed in braces

           Returns
           -------
           str
               the unparsed expression
        """
        return cls._impl_unparse_lr_operand(operand, wrap=wrap, right=False)

    @classmethod
    def _impl_unparse_right_operand(cls, operand, wrap=None):
        """Classmethod to unparse the right operand, handling associativity.

           Parameters
           ----------
           operand: |any|
               the operand to unparse (a Macro object or other value)
           wrap: bool
               if True the expression must be enclosed in braces

           Returns
           -------
           str
               the unparsed expression
        """
        return cls._impl_unparse_lr_operand(operand, wrap=wrap, right=True)

    @classmethod
    def _impl_unparse_operand(cls, operand, wrap=None):
        """Classmethod to unparse an operand.

           Parameters
           ----------
           operand: |any|
               the operand to unparse (a Macro object or other value)
           wrap: bool
               if True the expression must be enclosed in braces

           Returns
           -------
           str
               the unparsed expression
        """
        return cls._impl_unparse_lr_operand(operand, wrap=wrap, right=None)

    @classmethod
    def _impl_tree_operand(cls, operand):
        """Returns the 'tree' representation for an operand.

           Parameters
           ----------
           operand: |any|
               the operand to unparse (a Macro object or other value)

           Returns
           -------
           str
               the tree expression
        """
        if isinstance(operand, Macro):
            return operand._impl_tree()  # pylint: disable=W0212
        else:
            return repr(operand)

    @classmethod
    def _priority(cls):
        """Returns the class priority

           Returns
           -------
           int
               the class priority
        """
        return cls.PRIORITY.get(cls.__name__, 1000)

    @classmethod
    def _right_associativity(cls):
        """Returns True if class is right associative

           Returns
           -------
           bool
               True if right associative
        """
        return cls.RIGHT_ASSOCIATIVITY.get(cls.__name__, False)


class MConst(Macro):
    """Macro const expression. Evaluates to a const value.

       Parameters
       ----------
       value: |any|
           the const value

       Attributes
       ----------
       value: |any|
           the const value
    """

    def __init__(self, value):
        self.value = value

    def __reduce__(self):
        return (self.__class__, (self.value,))

    def _impl_tree(self):
        return "{}({!r})".format(self.__class__.__name__, self.value)

    def evaluate(self, globals_d=None):
        return self._impl_evaluate_operand(operand=self.value, globals_d=globals_d)

    def _impl_unparse(self):
        return self._impl_unparse_operand(self.value)


class MName(Macro):
    """Macro name lookup. Evaluates to the value referred by 'name'

       Parameters
       ----------
       name: str
           the name
       globals_d: dict, optional
           the globals dictionary (defaults to None)

       Attributes
       ----------
       name: str
           the name
       globals_d: dict, optional
           the globals dictionary (defaults to None)
    """

    def __init__(self, name, globals_d=None):
        self.name = name
        self.globals_d = globals_d

    def __reduce__(self):
        return (self.__class__, (self.name, self.globals_d))

    def _impl_tree(self):
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

    def _impl_unparse(self):
        return self.name


class MCall(Macro):
    """Macro object call.

       Parameters
       ----------
       functor: callable
           the object to be called
       p_args: tuple
           functor's positional arguments
       n_args: dict
           functor's keyword arguments

       Attributes
       ----------
       functor: callable
           the object to be called
       p_args: tuple
           functor's positional arguments
       n_args: dict
           functor's keyword arguments
    """

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

    def _impl_tree(self):
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

    def _impl_unparse(self):
        l_args = []
        if self.p_args:
            l_args.extend(self._impl_unparse_operand(a) for a in self.p_args)
        if self.n_args:
            l_args.extend("{}={}".format(k, self._impl_unparse_operand(v)) for k, v in self.n_args.items())
        return "{}({})".format(self._impl_unparse_operand(self.functor), ', '.join(l_args))


class MUnaryOperator(Macro):
    """Abstract base class for macro unary operators.

       Parameters
       ----------
       operand: |any|
           the operand

       Attributes
       ----------
       operand: |any|
           the operand
    """

    def __init__(self, operand):
        self.operand = operand

    def __reduce__(self):
        return (self.__class__, (self.operand,))

    def _impl_tree(self):
        return "{}({})".format(self.__class__.__name__, self._impl_tree_operand(self.operand))

    def evaluate(self, globals_d=None):
        value = self._impl_evaluate_operand(operand=self.operand, globals_d=globals_d)
        return self._impl_unary_operation(value)

    @abc.abstractmethod
    def _impl_unary_operation(self, value):
        """Returns the unary operation

        Parameters
        ----------
        value: |any|
            the evaluated operand

        Returns
        -------
        |any|
            the operator's result
        """
        raise NotImplementedError


class MAbs(MUnaryOperator):
    """Macro 'abs()' function."""

    def _impl_unary_operation(self, value):
        return abs(value)

    def _impl_unparse(self):
        return "abs({})".format(self._impl_unparse_operand(self.operand, wrap=False))


class MPos(MUnaryOperator):
    """Macro '+' unary operator."""

    def _impl_unary_operation(self, value):
        return +value

    def _impl_unparse(self):
        return "+{}".format(self._impl_unparse_operand(self.operand))


class MNeg(MUnaryOperator):
    """Macro '-' unary operator."""

    def _impl_unary_operation(self, value):
        return -value

    def _impl_unparse(self):
        return "-{}".format(self._impl_unparse_operand(self.operand))


class MNot(MUnaryOperator):
    """Macro 'not' unary operator."""

    def _impl_unary_operation(self, value):
        return not value

    def _impl_unparse(self):
        return "not {}".format(self._impl_unparse_operand(self.operand))


class MLen(MUnaryOperator):
    """Macro 'len' function."""

    def _impl_unary_operation(self, value):
        return len(value)

    def _impl_unparse(self):
        return "len({})".format(self._impl_unparse_operand(self.operand, wrap=False))


class MStr(MUnaryOperator):
    """Macro 'str' function."""

    def _impl_unary_operation(self, value):
        return str(value)

    def _impl_unparse(self):
        return "str({})".format(self._impl_unparse_operand(self.operand, wrap=False))


class MRepr(MUnaryOperator):
    """Macro 'repr' function."""

    def _impl_unary_operation(self, value):
        return repr(value)

    def _impl_unparse(self):
        return "repr({})".format(self._impl_unparse_operand(self.operand, wrap=False))


class MBinaryOperator(Macro):
    """Abstract base class for macro binary operators.

       Parameters
       ----------
       left_operand: |any|
           the left operand
       right_operand: |any|
           the right operand

       Attributes
       ----------
       left_operand: |any|
           the left operand
       right_operand: |any|
           the right operand
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
        """Returns the binary operation result.

           Parameters
           ----------
           left_value: |any|
               the evaluated left operand
           right_value: |any|
               the evaluated right operand

           Returns
           -------
           |any|
               the result
        """
        raise NotImplementedError

    def __reduce__(self):
        return (self.__class__, (self.left_operand, self.right_operand))

    def _impl_tree(self):
        return "{}({}, {})".format(
            self.__class__.__name__,
            self._impl_tree_operand(self.left_operand),
            self._impl_tree_operand(self.right_operand))

    def _impl_unparse(self):
        return "{} {} {}".format(
            self._impl_unparse_left_operand(self.left_operand),
            self.BINOP_SYMBOL,
            self._impl_unparse_right_operand(self.right_operand))


class MAdd(MBinaryOperator):
    """Macro '+' binary operator."""
    BINOP_SYMBOL = '+'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value + right_value


class MMul(MBinaryOperator):
    """Macro '*' binary operator."""
    BINOP_SYMBOL = '*'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value * right_value


class MSub(MBinaryOperator):
    """Macro '-' binary operator."""
    BINOP_SYMBOL = '-'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value - right_value


class MTrueDiv(MBinaryOperator):
    """Macro '/' binary operator."""
    BINOP_SYMBOL = '/'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value / right_value


class MFloorDiv(MBinaryOperator):
    """Macro '//' binary operator."""
    BINOP_SYMBOL = '//'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value // right_value


class MMod(MBinaryOperator):
    """Macro '%' binary operator."""
    BINOP_SYMBOL = '%'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value % right_value


class MDivMod(MBinaryOperator):
    """Macro 'divmod' function."""

    def _impl_binary_operation(self, left_value, right_value):
        return divmod(left_value, right_value)

    def _impl_unparse(self):
        return "divmod({}, {})".format(
            self._impl_unparse_left_operand(self.left_operand, wrap=False),
            self._impl_unparse_right_operand(self.right_operand, wrap=False))


class MPow(MBinaryOperator):
    """Macro '**' binary operator."""
    BINOP_SYMBOL = '**'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value ** right_value


class MEq(MBinaryOperator):
    """Macro '==' binary operator."""
    BINOP_SYMBOL = '=='

    def _impl_binary_operation(self, left_value, right_value):
        return left_value == right_value


class MNe(MBinaryOperator):
    """Macro '!=' binary operator."""
    BINOP_SYMBOL = '!='

    def _impl_binary_operation(self, left_value, right_value):
        return left_value != right_value


class MLt(MBinaryOperator):
    """Macro '<' binary operator."""
    BINOP_SYMBOL = '<'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value < right_value


class MLe(MBinaryOperator):
    """Macro '<=' binary operator."""
    BINOP_SYMBOL = '<='

    def _impl_binary_operation(self, left_value, right_value):
        return left_value <= right_value


class MGt(MBinaryOperator):
    """Macro '>' binary operator."""
    BINOP_SYMBOL = '>'

    def _impl_binary_operation(self, left_value, right_value):
        return left_value > right_value


class MGe(MBinaryOperator):
    """Macro '>=' binary operator."""
    BINOP_SYMBOL = '>='

    def _impl_binary_operation(self, left_value, right_value):
        return left_value >= right_value


class MAnd(MBinaryOperator):
    """Macro 'and' binary operator."""

    def _impl_binary_operation(self, left_value, right_value):
        return left_value and right_value

    def unparse(self):
        return "{} and {}".format(
            self._impl_unparse_left_operand(self.left_operand),
            self._impl_unparse_right_operand(self.right_operand))


class MOr(MBinaryOperator):
    """Macro 'or' binary operator."""

    def _impl_binary_operation(self, left_value, right_value):
        return left_value or right_value


class MGetattr(MUnaryOperator):
    """Macro 'getattr' function."""
    def __init__(self, operand, attr_name):
        super().__init__(operand)
        self.attr_name = attr_name

    def _impl_unary_operation(self, operand):
        return getattr(operand, self.attr_name)

    def _impl_unparse(self):
        operand = self._impl_unparse_operand(self.operand)
        fmt = "{}.{}"
        return fmt.format(operand, self.attr_name)


class MGetitem(MBinaryOperator):
    """Macro 'getitem' function."""

    def _impl_binary_operation(self, left, right):
        return left[right]

    def _impl_unparse(self):
        left = self._impl_unparse_left_operand(self.left_operand)
        right = self._impl_unparse_right_operand(self.right_operand, wrap=False)
        fmt = "{}[{}]"
        return fmt.format(left, right)


class MContains(MBinaryOperator):
    """Macro 'in' binary operator."""

    def _impl_binary_operation(self, left_value, right_value):
        return left_value in right_value

    def _impl_unparse(self):
        return "{} in {}".format(
            self._impl_unparse_left_operand(self.left_operand),
            self._impl_unparse_right_operand(self.right_operand))
