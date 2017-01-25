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


from collections import namedtuple

from eos.const.eos import Restriction, Slot
from eos.const.eve import Attribute, Group, Category
from eos.fit.item import *
from .base import BaseRestrictionRegister
from ..exception import RegisterValidationError


HolderClassErrorData = namedtuple('HolderClassErrorData', ('holder_class', 'expected_classes'))


CLASS_VALIDATORS = {
    Booster: lambda eve_type: (
        eve_type.category == Category.implant and
        Attribute.boosterness in eve_type.attributes
    ),
    Character: lambda eve_type: eve_type.group == Group.character,
    Charge: lambda eve_type: eve_type.category == Category.charge,
    Drone: lambda eve_type: eve_type.category == Category.drone,
    EffectBeacon: lambda eve_type: eve_type.group == Group.effect_beacon,
    Implant: lambda eve_type: (
        eve_type.category == Category.implant and
        Attribute.implantness in eve_type.attributes
    ),
    ModuleHigh: lambda eve_type: (
        eve_type.category == Category.module and
        Slot.module_high in eve_type.slots
    ),
    ModuleMed: lambda eve_type: (
        eve_type.category == Category.module and
        Slot.module_med in eve_type.slots
    ),
    ModuleLow: lambda eve_type: (
        eve_type.category == Category.module and
        Slot.module_low in eve_type.slots
    ),
    Rig: lambda eve_type: (
        eve_type.category == Category.module and
        Slot.rig in eve_type.slots
    ),
    Ship: lambda eve_type: eve_type.category == Category.ship,
    Skill: lambda eve_type: eve_type.category == Category.skill,
    Stance: lambda eve_type: eve_type.group == Group.ship_modifier,
    Subsystem: lambda eve_type: (
        eve_type.category == Category.subsystem and
        Slot.subsystem in eve_type.slots
    )
}


class HolderClassRestrictionRegister(BaseRestrictionRegister):
    """
    Implements restriction:
    Check that EVE type is wrapped by corresponding holder class
    instance (e.g. that cybernetic subprocessor is represented
    by Implant class instance).

    Details:
    To determine item class matching to EVE type, only EVE type
    attributes are used.
    """

    def __init__(self):
        # Container for tracked holders
        self.__holders = set()

    def register_item(self, holder):
        # Yes, we're tracking all of them
        self.__holders.add(holder)

    def unregister_item(self, holder):
        self.__holders.discard(holder)

    def validate(self):
        tainted_holders = {}
        for holder in self.__holders:
            # Get validator function for class of passed holder.
            # If it is not found or fails, seek for 'right'
            # item class for the EVE type
            try:
                validator_func = CLASS_VALIDATORS[type(holder)]
            except KeyError:
                tainted_holders[holder] = self.__get_error_data(holder)
            else:
                if validator_func(holder._eve_type) is not True:
                    tainted_holders[holder] = self.__get_error_data(holder)
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    def __get_error_data(self, holder):
        expected_classes = []
        # Cycle through our class validator dictionary and
        # seek for acceptable classes for this EVE type
        for holder_class, validator_func in CLASS_VALIDATORS.items():
            if validator_func(holder._eve_type) is True:
                expected_classes.append(holder_class)
        error_data = HolderClassErrorData(
            holder_class=type(holder),
            expected_classes=set(expected_classes)
        )
        return error_data

    @property
    def restriction_type(self):
        return Restriction.holder_class
