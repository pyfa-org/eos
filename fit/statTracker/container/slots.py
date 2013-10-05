#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


class EntitySlots:
    """
    Generic functionality for classes which track amount
    of used slots against provided slots
    """

    def __init__(self, fit, container, slotCarrier, slotAttr):
        self._fit = fit
        self.__container = container
        self.__slotCarrier = slotCarrier
        self.__slotAttr = slotAttr

    @property
    def used(self):
        return len(self.__container)

    @property
    def total(self):
        # Get amount of provided slots, setting it to None
        # if fitting doesn't have ship assigned,
        # or ship doesn't have slot attribute
        shipHolder = getattr(self._fit, self.__slotCarrier)
        try:
            shipHolderAttribs = shipHolder.attributes
        except AttributeError:
            return None
        else:
            try:
                return int(shipHolderAttribs[self.__slotAttr])
            except KeyError:
                return None


class ShipSlots(EntitySlots):
    """
    Class for providing amount of used and available
    slots on ship.
    """

    def __init__(self, fit, container, slotAttr):
        EntitySlots.__init__(self, fit, container, 'ship', slotAttr)


class CharSlots(EntitySlots):
    """
    Class for providing amount of used and available
    slots on character.
    """

    def __init__(self, fit, container, slotAttr):
        EntitySlots.__init__(self, fit, container, 'character', slotAttr)
