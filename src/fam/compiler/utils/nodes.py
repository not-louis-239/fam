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


from dataclasses import dataclass

# Base AST node definition
@dataclass
class ASTNode:
    # start and end position in the original source code
    # this is for error reporting
    start_pos: int
    end_pos: int


type AST = list[ASTNode]

# Expressions

@dataclass
class Expr(ASTNode):
    pass

@dataclass
class Name(Expr):
    string: str

# Literals

@dataclass
class Literal(ASTNode):
    pass

@dataclass
class Date(Literal):
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int

@dataclass
class Duration(Literal):
    day: int
    hour: int
    minute: int
    second: int

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

# Binary operators

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
class ModuloOp(BinOp): pass

# Comparative binary operators
@dataclass
class EqOp(BinOp): pass
@dataclass
class GtOp(BinOp): pass
@dataclass
class GtEqOp(BinOp): pass
@dataclass
class LtOp(BinOp): pass
@dataclass
class LtEqOp(BinOp): pass

# Logical operators
@dataclass
class BitOrOp(BinOp): pass
@dataclass
class AndOp(BinOp): pass
@dataclass
class IdentityOp(BinOp): pass

# Attribute clauses

@dataclass
class Attribute(ASTNode):
    name: Name
    value: Expr

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
class LinkDecl:
    name: Name
    src: Name
    dest: Name
    attributes: list[Attribute]

# Node declarations

@dataclass
class NodeDecl:
    name: Name
    attributes: list[Attribute]

# Method definitions

@dataclass
class MethodParam(ASTNode):
    typ: Name
    name: Name
    default: Expr | None

@dataclass
class MethodDecl:
    name: Name
    caller: Name | None  # The class, instances on which the method can be called. None = it's a function.
    params: list[MethodParam]
    body: AST

# Method calls

@dataclass
class MethodCall:
    name: Name
    args: Expr
    kwargs: dict[Name, Expr]
