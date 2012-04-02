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


from eos.exception import EosError


# Exception classes used by modifier builder
class ModifierBuilderError(EosError):
    """
    All exceptions raised by modifier builder are based on this class.
    """
    pass


class TreeFetchingError(ModifierBuilderError):
    """
    Raised when modifier builder encounters expression fetching error.
    """
    pass


class TreeParsingError(ModifierBuilderError):
    """
    Raised when action builder encounters some expected error.
    """
    pass


class TreeParsingUnexpectedError(ModifierBuilderError):
    """
    Raised when action builder encounters some unhandled error.
    """
    pass


class UnusedActionError(ModifierBuilderError):
    """
    Raised when some actions are not marked as used after
    generating modifiers out of them.
    """
    pass


# Exception classes used by action builder
class ActionBuilderError(EosError):
    """
    All exceptions raised by action builder are either represented
    by this class or based on it.
    """
    pass

class ActionValidationError(ActionBuilderError):
    """
    Raised when some action generated out of expression tree
    is invalid.
    """
    pass
