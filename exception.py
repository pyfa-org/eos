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


class EosException(Exception):
    """All public exceptions raised by Eos are based on this class"""
    pass


class ModifierBuilderException(EosException):
    """
    Exception of this type is raised when modifier builder
    encounters some 'known' error and wants to notify caller
    """
    pass


class ConditionBuilderException(EosException):
    """
    Exception of this type is raised when condition atom builder
    encounters some 'known' error and wants to notify caller
    """
    pass


class TargetException(EosException):
    """Raised when passed target is invalid"""
    pass


class ItemFittingException(EosException):
    """
    Not used directly, subclassed by more specific exceptions
    which specify exact reason why item cannot be fit.
    """
    pass


class NoSlotAttributeException(ItemFittingException):
    """
    Raised on attempt to add holder to slot-based container, if holder's
    item doesn't have attribute which is used as slot index.
    """
    pass


class SlotOccupiedException(ItemFittingException):
    """
    Raised on attempt to add holder to slot-based container, if slot
    to which holder should be added is already occupied by another holder.
    """
    pass
