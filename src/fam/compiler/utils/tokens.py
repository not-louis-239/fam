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

    # Core keywords
    DEFINE = "Define"
    DISPLAY = "Display"
    IMPORT = "Import"

    # Control flow - conditionals
    IF = "If"
    ELSE = "Else"
    ELSE_IF = "ElseIf"

    # Control flow - loops
    WHILE = "While"
    FOR = "For"
    IN = "In"
    BREAK = "Break"
    CONTINUE = "Continue"
    PASS = "Pass"

    # Control flow - functions
    METHOD = "Method"
    RETURN = "Return"

    # Core type keywords
    NODE = "Node"
    LINK = "Link"
    VARIABLE = "Variable"
    ATTRIBUTE = "Attribute"

    # Core modifier keywords
    DEFAULT = "Default"
    FROM = "From"
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
    BIN_IS_NOT = "BinIsNot"
    UN_NOT = "BinNot"
    BIN_AND = "BinAnd"
    BIN_OR = "BinOr"

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
    ASSIGNMENT = "Equals"

    # Binary operations
    BIN_ADD = "BinAdd"
    BIN_SUB = "BinSub"
    BIN_MUL = "BinMul"
    BIN_DIV = "BinDiv"
    BIN_FLOOR_DIV = "BinFloorDiv"
    BIN_MODULO = "BinModulo"
    BIN_POW = "BinPow"

    # Bitwise operators
    BIN_BIT_AND = "BinBitAnd"
    BIN_BIT_OR = "BinBitOr"
    BIN_BIT_NOT = "BinBitNot"
    BIN_BIT_XOR = "BinBitXor"

    # Bitwise shifts
    BIN_L_SHIFT = "BinLShift"
    BIN_R_SHIFT = "BinRShift"

    # Chainable comparators
    BIN_EQ = "BinEq"
    BIN_NOT_EQ = "BinNotEq"
    BIN_GREATER_THAN = "BinGreaterThan"
    BIN_LESS_THAN = "BinLessThan"
    BIN_GREATER_EQ = "BinGreaterEq"
    BIN_LESS_EQ = "BinLessEq"

    # Whitespace
    NEWLINE = "Newline"
    INDENT = "Indent"
    DEDENT = "Dedent"

    # Punctuation - delimiters
    DOT = "Dot"
    COLON = "Colon"
    COMMA = "Comma"

    # Punctuation - brackets
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