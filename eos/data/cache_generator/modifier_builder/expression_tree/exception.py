# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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


__all__ = [
    'UnknownRootOperandError',
    'UnknownPrimaryOperandError',
    'UnexpectedHandlingError'
]


from eos.exception import EosError


class Etree2ModifiersError(EosError):
    """
    All exceptions raised by expression-to-modifier converter
    are based on this class.
    """
    pass


class UnknownRootOperandError(Etree2ModifiersError):
    """
    Raised when root operand cannot be handled by converter.
    """
    pass


class UnknownPrimaryOperandError(Etree2ModifiersError):
    """
    Raised when non-root operand which is supposed to define
    modifiers cannot be handled by converter.
    """
    pass


class UnexpectedHandlingError(Etree2ModifiersError):
    """
    Raised when handler fails to compose modifier.
    """
    pass
