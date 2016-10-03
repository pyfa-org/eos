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


from collections import namedtuple

from eos.const.eos import Restriction, Slot
from eos.const.eve import Attribute, Group, Category
from eos.fit.restriction_tracker.exception import RegisterValidationError
from eos.fit.holder.item import (
    Booster, Character, Charge, Drone, EffectBeacon, Implant,
    ModuleHigh, ModuleMed, ModuleLow, Rig, Ship, Skill, Stance, Subsystem
)

from .abc import RestrictionRegister


HolderClassErrorData = namedtuple('HolderClassErrorData', ('holder_class', 'expected_classes'))


CLASS_VALIDATORS = {
    Booster: lambda item: (
        item.category == Category.implant and
        Attribute.boosterness in item.attributes
    ),
    Character: lambda item: item.group == Group.character,
    Charge: lambda item: item.category == Category.charge,
    Drone: lambda item: item.category == Category.drone,
    EffectBeacon: lambda item: item.group == Group.effect_beacon,
    Implant: lambda item: (
        item.category == Category.implant and
        Attribute.implantness in item.attributes
    ),
    ModuleHigh: lambda item: (
        item.category == Category.module and
        Slot.module_high in item.slots
    ),
    ModuleMed: lambda item: (
        item.category == Category.module and
        Slot.module_med in item.slots
    ),
    ModuleLow: lambda item: (
        item.category == Category.module and
        Slot.module_low in item.slots
    ),
    Rig: lambda item: (
        item.category == Category.module and
        Slot.rig in item.slots
    ),
    Ship: lambda item: item.category == Category.ship,
    Skill: lambda item: item.category == Category.skill,
    Stance: lambda item: item.group == Group.ship_modifier,
    Subsystem: lambda item: (
        item.category == Category.subsystem and
        Slot.subsystem in item.slots
    )
}


class HolderClassRegister(RestrictionRegister):
    """
    Implements restriction:
    Check that item is wrapped by corresponding holder class
    instance (e.g. that cybernetic subprocessor is represented
    by Implant class instance).

    Details:
    To determine class matching to item, attributes only of
    original item are used.
    """

    def __init__(self):
        # Container for tracked holders
        self.__holders = set()

    def register_holder(self, holder):
        # Yes, we're tracking all of them
        self.__holders.add(holder)

    def unregister_holder(self, holder):
        self.__holders.discard(holder)

    def validate(self):
        tainted_holders = {}
        for holder in self.__holders:
            # Get validator function for class of passed holder.
            # If it is not found or fails, seek for 'right'
            # holder types for the item
            try:
                validator_func = CLASS_VALIDATORS[type(holder)]
            except KeyError:
                tainted_holders[holder] = self.__get_error_data(holder)
            else:
                if validator_func(holder.item) is not True:
                    tainted_holders[holder] = self.__get_error_data(holder)
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    def __get_error_data(self, holder):
        expected_classes = []
        # Cycle through our class validator dictionary and
        # seek for acceptable classes for this item
        for holder_class, validator_func in CLASS_VALIDATORS.items():
            if validator_func(holder.item) is True:
                expected_classes.append(holder_class)
        error_data = HolderClassErrorData(
            holder_class=type(holder),
            expected_classes=tuple(expected_classes)
        )
        return error_data

    @property
    def restriction_type(self):
        return Restriction.holder_class
