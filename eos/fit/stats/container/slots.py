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


from eos.util.volatile_cache import InheritableVolatileMixin, volatile_property


class EntitySlots(InheritableVolatileMixin):
    """
    Generic functionality for classes which track amount
    of used slots against provided slots
    """

    def __init__(self, fit, consumption_register, slot_carrier, slot_attr):
        InheritableVolatileMixin.__init__(self)
        self._fit = fit
        self.__consumption_register = consumption_register
        self.__slot_carrier = slot_carrier
        self.__slot_attr = slot_attr

    @volatile_property
    def used(self):
        return self.__consumption_register.slots_used

    @volatile_property
    def total(self):
        # Get amount of provided slots, setting it to None
        # if fitting doesn't have ship assigned,
        # or ship doesn't have slot attribute
        slot_carrier_item = getattr(self._fit, self.__slot_carrier)
        try:
            slot_carrier_attribs = slot_carrier_item.attributes
        except AttributeError:
            return None
        else:
            try:
                return int(slot_carrier_attribs[self.__slot_attr])
            except KeyError:
                return None


class ShipSlots(EntitySlots):
    """
    Class for providing amount of used and available
    slots on ship.
    """

    def __init__(self, fit, container, slot_attr):
        EntitySlots.__init__(self, fit, container, 'ship', slot_attr)


class CharSlots(EntitySlots):
    """
    Class for providing amount of used and available
    slots on character.
    """

    def __init__(self, fit, container, slot_attr):
        EntitySlots.__init__(self, fit, container, 'character', slot_attr)
