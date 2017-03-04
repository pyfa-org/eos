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


from eos.exception import EosError


class ItemContainerError(EosError):
    """
    Custom exceptions thrown by item containers are based
    on this class.
    """
    ...


class ItemAlreadyAssignedError(ItemContainerError):
    """
    Raised on attempt to add item, when
    it's already assigned to fit.
    """
    ...


class ItemFitMismatchError(ItemContainerError):
    """
    Raised during removal of item, when item's fit reference
    does not reference fit item being removed from.
    """
    ...


class SlotTakenError(ItemContainerError):
    """
    When attempt to overwrite another item in ordered container
    is detected, this exception is raised.
    """
    ...
