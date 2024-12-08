"""A mini Mathematica."""
from functools import singledispatch
import numbers


class Expression:
    """Class for expression."""

    def __init__(self, *operands):
        """Initialise."""
        self.operands = operands

    def __add__(self, other):
        """Add."""
        if not isinstance(other, Expression):
            other = Number(other)
        return Add(self, other)

    def __sub__(self, other):
        """Subtract."""
        if not isinstance(other, Expression):
            other = Number(other)
        return Sub(self, other)

    def __mul__(self, other):
        """Multiply."""
        if not isinstance(other, Expression):
            other = Number(other)
        return Mul(self, other)

    def __truediv__(self, other):
        """Divide."""
        if not isinstance(other, Expression):
            other = Number(other)
        return Div(self, other)

    def __pow__(self, other):
        """Raise to the power."""
        if not isinstance(other, Expression):
            other = Number(other)
        return Pow(self, other)

    def __radd__(self, other):
        """Reverse add."""
        return Add(Number(other), self)

    def __rsub__(self, other):
        """Reverse subtract."""
        return Sub(Number(other), self)

    def __rmul__(self, other):
        """Reverse multiply."""
        return Mul(Number(other), self)

    def __rtruediv__(self, other):
        """Reverse divide."""
        return Div(Number(other), self)

    def __rpow__(self, other):
        """Reverse raise to the power."""
        return Pow(Number(other), self)

    def __repr__(self):
        """Represent."""
        return type(self).__name__ + repr(self.operands)

    def __str__(self):
        """Represent using strings."""
        return self.operands


class Terminal(Expression):
    """Terminal class."""

    def __init__(self, value):
        """Initialise."""
        super().__init__()
        self.value = value

    def __repr__(self):
        """Represent."""
        return repr(self.value)

    def __str__(self):
        """Represent using strings."""
        return str(self.value)


class Number(Terminal):
    """Number class."""

    def __init__(self, value):
        """Initialise."""
        if not isinstance(value, numbers.Number):
            raise TypeError(f"Expected a number, got a {type(value)}.")
        super().__init__(value)


class Symbol(Terminal):
    """Symbol class."""

    def __init__(self, value):
        """Initialise."""
        if not isinstance(value, str):
            raise TypeError(f"Expected a string, got {type(value)}.")
        super().__init__(value)


class Operator(Expression):
    """Operator class."""

    precedence = 0
    symbol = ""

    def __str__(self):
        """Represent using strings."""
        left, right = self.operands
        left_str = str(left)
        right_str = str(right)

        if isinstance(left, Operator) and left.precedence < self.precedence:
            left_str = f"({left_str})"
        if isinstance(right, Operator) and right.precedence < self.precedence:
            right_str = f"({right_str})"

        return f"{left_str} {self.symbol} {right_str}"


class Add(Operator):
    """Add class."""

    precedence = 1
    symbol = "+"


class Sub(Operator):
    """Subtract class."""

    precedence = 1
    symbol = "-"


class Mul(Operator):
    """Multiply class."""

    precedence = 2
    symbol = "*"


class Div(Operator):
    """Divide class."""

    precedence = 2
    symbol = "/"


class Pow(Operator):
    """Power class."""

    precedence = 3
    symbol = "^"


def postvisitor(expr, fn, **kwargs):
    """Postvisitor function."""
    stack = [expr]
    visited = {}
    while stack:
        e = stack.pop()
        unvisited_children = []
        for o in e.operands:
            if o not in visited:
                unvisited_children.append(o)
        if unvisited_children:
            stack.append(e)
            for child in unvisited_children:
                stack.append(child)
        else:
            visited[e] = fn(e, *(visited[o] for o in e.operands), **kwargs)
    return visited[expr]


@singledispatch
def differentiate(expr, *o, **kwargs):
    """Differentiate."""
    raise NotImplementedError(
        f"Cannot differentiate a {type(expr).__name__}"
    )


@differentiate.register(Number)
def _(expr, *o, **kwargs):
    return Number(0)


@differentiate.register(Symbol)
def _(expr, *o, **kwargs):
    if expr.value in kwargs.values():
        return Number(1)
    else:
        return Number(0)


@differentiate.register(Add)
def _(expr, *o, **kwargs):
    return o[0] + o[1]


@differentiate.register(Sub)
def _(expr, *o, **kwargs):
    return o[0] - o[1]


@differentiate.register(Mul)
def _(expr, *o, **kwargs):
    return o[0] * expr.operands[1] + o[1] * expr.operands[0]


@differentiate.register(Div)
def _(expr, *o, **kwargs):
    return (o[0] * expr.operands[1] - o[1]
            * expr.operands[0]) / (expr.operands[1] ** 2)


@differentiate.register(Pow)
def _(expr, *o, **kwargs):
    return (o[0] * expr.operands[1]
            * expr.operands[0] ** (expr.operands[1] - 1))
