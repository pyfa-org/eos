# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


from eos.exception import EosError


# Exception classes used by effect to modifier converter
class Effect2ModifiersError(EosError):
    """
    All exceptions raised by effect-to-modifier converter are
    based on this class.
    """
    pass


class TreeParsingUnexpectedError(Effect2ModifiersError):
    """
    Raised when effect-to-modifier converter encounters some
    unhandled error.
    """
    pass


# Exception classes used by expression tree to action converter
class ETree2ActionError(EosError):
    """
    All exceptions raised by expression-to-action converter
    are either represented by this class or based on it.
    """
    pass


class ExpressionFetchError(ETree2ActionError):
    """
    Raised when expression-to-action converter is unable to find
    expression requested by any of its components.
    """
    pass


class ActionValidationError(ETree2ActionError):
    """
    Raised when some action generated out of expression tree
    is invalid.
    """
    pass
