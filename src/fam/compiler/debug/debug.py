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


from fam.compiler.utils.nodes import AST, ASTNode
from fam.compiler.utils.tokens import Token
from fam.utils import (
    COL_BLUE,
    COL_CYAN,
    COL_END,
    COL_GREEN,
    COL_MAGENTA,
    COL_YELLOW,
    pos_to_line_col,
)


def visualise_tokens(tokens: list[Token], src_code: str | None = None) -> None:
    for i, tok in enumerate(tokens, start=1):
        if src_code is not None:
            # Make a representation of the token that is easier to understand:
            line, col = pos_to_line_col(src_code, tok.start_pos)
            print(f"{COL_BLUE}{i: 6d}.{COL_END} {COL_YELLOW}{tok.typ}{COL_END} {COL_GREEN}{f"'{tok.string.replace('\n', '\\n')}'"}{COL_END} at line {COL_MAGENTA}{line + 1}{COL_END}, position {COL_MAGENTA}{col + 1}{COL_END}")
        else:
            print(f"{COL_BLUE}{i: 6d}.{COL_END} {COL_YELLOW}{tok.typ}{COL_END} {COL_GREEN}{f"'{tok.string.replace('\n', '\\n')}'"}{COL_END} at chars {COL_MAGENTA}{tok.start_pos + 1} - {tok.end_pos + 1}{COL_END}")


def _dump_node(node: ASTNode, padding: int = 0, indent: int = 4):
    node_vars = vars(node)
    end = ':' if any(s for s in node_vars if s not in ("start_pos", "end_pos")) else ''

    print(f"{COL_BLUE}{' ' * padding}{type(node).__name__}{COL_END} @ {COL_MAGENTA}{node.start_pos} - {node.end_pos}{COL_END}{end}")

    for name, value in node_vars.items():
        if name in ("start_pos", "end_pos"):
            continue

        name_str_with_indent = f"{COL_YELLOW}{' ' * (padding + indent)}{name}{COL_END}"

        if value is None:
            print(f"{name_str_with_indent}:\n{' ' * (padding + 2 * indent)}<None>")
            continue

        if isinstance(value, ASTNode):
            print(f"{name_str_with_indent}:")
            _dump_node(value, padding + 2 * indent)
            continue

        if isinstance(value, list) and all(isinstance(e, ASTNode) for e in value):
            if not value:
                print(f"{name_str_with_indent}:\n{' ' * (padding + 2 * indent)}<no elements>")
            else:
                print(f"{name_str_with_indent}:")
                dump_ast(value, padding + 2 * indent)
            continue

        print(f"{' ' * (padding + indent)}{COL_YELLOW}{name}{COL_END}: {COL_CYAN}{value!r}{COL_END}")

def dump_ast(ast: AST, padding: int = 0, indent: int = 4):
    for node in ast:
        _dump_node(node, padding, indent)
