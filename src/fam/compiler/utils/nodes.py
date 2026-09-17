# Fam - query and storage language specialised in modelling family trees
# repo at: https://github.com/not-louis-239/fam
# Copyright (C) 2026  Louis Masarei-Boulton <243234869+not-louis-239@users.noreply.github.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from collections.abc import Sequence as Sequence_t
from dataclasses import dataclass

# Base AST node definition

@dataclass
class ASTNode:
    # start and end position in the original source code
    # this is for error reporting
    start_pos: int
    end_pos: int


type AST = Sequence_t[ASTNode]

# Module imports

@dataclass
class Import(ASTNode):
    fp: str

# Expressions

@dataclass
class Expr(ASTNode):
    pass

@dataclass
class Name(Expr):
    string: str

# Literals

@dataclass
class Literal(Expr):
    pass

@dataclass
class Date(Literal):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    frac_seconds: float

@dataclass
class Duration(Literal):
    day: int
    hour: int
    minute: int
    second: int
    frac_seconds: float

@dataclass
class Integer(Literal):
    value: int

@dataclass
class Real(Literal):
    value: float

@dataclass
class String(Literal):
    value: str

@dataclass
class Boolean(Literal):
    value: bool

@dataclass
class NoneItem(Literal): pass

# Sequences

@dataclass
class Sequence(Expr):
    elems: list[Expr]

# Indexing

@dataclass
class IndexOp(Expr):
    container: Expr
    index: Expr

# Unary operators

@dataclass
class UnaryOp(Expr):
    operand: Expr

@dataclass
class PosOp(UnaryOp): pass
@dataclass
class NegOp(UnaryOp): pass

# Arithmetic, comparative, logical bitwise operators

@dataclass
class BinOp(Expr):
    lhs: Expr
    rhs: Expr

# Arithmetic binary operators
@dataclass
class AddOp(BinOp): pass
@dataclass
class SubOp(BinOp): pass
@dataclass
class MultOp(BinOp): pass
@dataclass
class DivOp(BinOp): pass
@dataclass
class FloorDivOp(BinOp): pass
@dataclass
class ModuloOp(BinOp): pass
@dataclass
class PowOp(BinOp): pass

# Comparative binary operators
@dataclass
class EqOp(BinOp): pass
@dataclass
class NotEqOp(BinOp): pass
@dataclass
class GtOp(BinOp): pass
@dataclass
class LtOp(BinOp): pass
@dataclass
class GtEqOp(BinOp): pass
@dataclass
class LtEqOp(BinOp): pass

# Logical operators - and, or
@dataclass
class AndOp(BinOp): pass
@dataclass
class OrOp(BinOp): pass
@dataclass
class NotOp(UnaryOp): pass

# Logical operators - identity and membership
@dataclass
class IsOp(BinOp): pass
@dataclass
class IsNotOp(BinOp): pass
@dataclass
class InOp(BinOp): pass
@dataclass
class NotInOp(BinOp): pass

# Bitwise operators - and, or, not, xor
@dataclass
class BitAndOp(BinOp): pass
@dataclass
class BitOrOp(BinOp): pass
@dataclass
class BitNotOp(UnaryOp): pass
@dataclass
class BitXorOp(BinOp): pass

# Bitwise operators - shifts
@dataclass
class BitLShift(BinOp): pass
@dataclass
class BitRShift(BinOp): pass

# Singular instructions

@dataclass
class Break(ASTNode): pass
@dataclass
class Continue(ASTNode): pass
@dataclass
class Pass(ASTNode): pass

@dataclass
class Return(ASTNode):
    value: Expr | None

# Display queries

@dataclass
class Display(ASTNode):
    expr: Expr

# Key-value pairs

@dataclass
class KeyValuePair(ASTNode):
    name: Name
    value: Expr

# Variable definitions

@dataclass
class VariableDef(ASTNode):
    typ: Expr | None
    name: Name
    value: Expr

# Conditionals

@dataclass
class IfStmt(ASTNode):
    condition: Expr
    body: AST
    else_body: AST | None

# Loops

@dataclass
class WhileLoop(ASTNode):
    condition: Expr
    body: AST

@dataclass
class ForLoop(ASTNode):
    var: Name
    iterable: Expr
    body: AST

# Link definitions

@dataclass
class LinkDef(ASTNode):
    name: Name

@dataclass
class InferredLinkDef(LinkDef):
    inferred_name: Name

@dataclass
class ImplicitLinkDef(LinkDef):
    link_names: list[Name]

# Link declarations

@dataclass
class LinkDecl(ASTNode):
    name: Name
    src: Name
    dest: Name
    attributes: list[KeyValuePair]

# Node declarations

@dataclass
class NodeDecl(ASTNode):
    name: Name
    attributes: list[KeyValuePair]

# Attribute definitions

@dataclass
class AttributeDef(ASTNode):
    typ: Expr | None
    name: Name
    constraints: list[Expr]

# Method definitions

@dataclass
class MethodParam(ASTNode):
    typ: Expr | None
    name: Name
    default: Expr | None

@dataclass
class MethodDecl(ASTNode):
    caller: Name | None  # The class, instances on which the method can be called. None = it's a function.
    name: Name
    params: list[MethodParam]
    return_type: Expr | None
    body: AST

# Attribute access

@dataclass
class AttributeAccess(Expr):
    name: Expr
    attr: Name

# Method calls

@dataclass
class MethodCall(Expr):
    method: Expr
    args: list[Expr]
