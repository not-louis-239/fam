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




class FamException(Exception):
    def __init__(self, msg: str, start_pos: int, end_pos: int):
        super().__init__(msg)
        self.msg = msg
        self.start_pos = start_pos
        self.end_pos = end_pos


class FamParseError(FamException):
    """Invalid syntax."""
    pass


class FamIndentationError(FamParseError):
    """Unexpected, missing or otherwise incorrect indentation."""
    pass


class FamTabError(FamIndentationError):
    """Inconsistent use of tabs and spaces in indentation."""
    pass


class FamTypeError(FamException):
    """Bad operand or function type, incorrect arguments supplied to method."""
    pass


class FamConstraintError(FamException):
    """Attribute constraint violated."""
    pass


class FamIndexError(FamException):
    """Index out of range."""
    pass


class FamNameError(FamException):
    """Identifier doesn't exist."""
    pass


class FamAttributeError(FamException):
    """Attribute doesn't exist on specified object."""
    pass


class FamAmbiguityError(FamException):
    """Identifier could not be resolved due to multiple valid references."""
    pass


class FamImportError(FamException):
    """Import failed."""


class FamMissingModuleError(FamImportError):
    """Module not found."""
    pass


class FamCircularImportError(FamImportError):
    """Module attempts to import a module that imports the original module."""
