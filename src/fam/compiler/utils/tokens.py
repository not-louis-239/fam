

from dataclasses import dataclass
from enum import StrEnum


class TokenType(StrEnum):
    # In order of priority...

    # Keywords
    DEFINE = "Define"
    METHOD = "Method"
    RETURN = "Return"
    DISPLAY = "Display"
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
    BIN_OR = "BinOr"
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
    L_PAREN = "LParen"
    R_PAREN = "RParen"


@dataclass
class Token:
    typ: TokenType
    string: str

    # Metadata is attached by the lexer, not the compiler itself
    start_pos: int = -1
    end_pos: int = -1