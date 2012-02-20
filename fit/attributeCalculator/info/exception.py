#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
#===============================================================================


from eos.exception import EosException


# Exception classes used by info builder
class InfoBuilderException(EosException):
    """
    All exceptions raised by info builder are based on this class.
    """
    pass


class TreeParsingError(InfoBuilderException):
    """
    Raised when modifier builder encounters some expected error.
    """
    pass


class TreeParsingUnexpectedError(InfoBuilderException):
    """
    Raised when modifier builder encounters some unhandled error.
    """
    pass


class ModifierValidationError(InfoBuilderException):
    """
    Raised when some modifier generated out of expression tree
    is invalid.
    """
    pass


class UnusedModifierError(InfoBuilderException):
    """
    Raised when some modifiers are not marked as used after
    generating infos out of them.
    """
    pass


# Exception classes used by modifier builder
class ModifierBuilderException(EosException):
    """
    All exceptions raised by modifier builder are either represented
    by this class or based on it.
    """
    pass


# Exception classes used by condition builder
class ConditionBuilderException(EosException):
    """
    All exceptions raised by condition builder are either represented
    by this class or based on it.
    """
    pass
