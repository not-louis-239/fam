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
from enum import StrEnum


class TokenType(StrEnum):
    # In order of priority...

    # Keywords
    DEFINE = "Define"
    DEFAULT = "Default"
    METHOD = "Method"
    RETURN = "Return"
    DISPLAY = "Display"
    PASS = "Pass"
    IF = "If"
    ELSE = "Else"

    # Core type keywords
    NODE = "Node"
    LINK = "Link"
    FROM = "From"
    VARIABLE = "Variable"
    ATTRIBUTE = "Attribute"
    CONSTRAINTS = "Constraints"

    # Language constants
    NONE = "None"
    TRUE = "True"
    FALSE = "False"

    # Modifier keywords
    INFERRED = "Inferred"
    IMPLICIT = "Implicit"

    # Logical operators
    BIN_IS = "BinIs"
    BIN_NOT = "BinNot"

    # Names
    NAME = "Name"

    # Literals
    STRING = "String"
    DATE = "Date"
    DURATION = "Duration"
    INTEGER = "Integer"
    REAL = "Real"

    # Operations
    ARROW_RIGHT = "ArrowRight"
    ARROW_DOUBLE = "ArrowDouble"
    ARROW_IMPLICATION = "ArrowImplication"
    EQUALS = "Equals"

    # Binary operations
    BIN_ADD = "BinAdd"
    BIN_SUB = "BinSub"
    BIN_MUL = "BinMul"
    BIN_DIV = "BinDiv"
    BIN_MODULO = "BinModulo"
    BIN_BIT_OR = "BinOr"
    BIN_EQ = "BinEq"
    BIN_GREATER_THAN = "BinGreaterThan"
    BIN_LESS_THAN = "BinLessThan"
    BIN_GREATER_EQ = "BinGreaterEq"
    BIN_LESS_EQ = "BinLessEq"

    # Whitespace
    NEWLINE = "Newline"
    INDENT = "Indent"
    DEDENT = "Dedent"

    # Punctuation
    DOT = "Dot"
    COLON = "Colon"
    COMMA = "Comma"
    L_PAREN = "LParen"
    R_PAREN = "RParen"
    L_SQ_BRAC = "LSqBrac"
    R_SQ_BRAC = "RSqBrac"
    L_BRACE = "LBrace"
    R_BRACE = "RBrace"


@dataclass
class Token:
    typ: TokenType
    string: str

    # Metadata is attached by the lexer, not the compiler itself
    start_pos: int = -1
    end_pos: int = -1