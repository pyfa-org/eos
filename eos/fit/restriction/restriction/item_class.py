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


ItemClassErrorData = namedtuple('ItemClassErrorData', ('item_class', 'expected_classes'))


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


class ItemClassRestrictionRegister(BaseRestrictionRegister):
    """
    Implements restriction:
    Check that eve type is wrapped by corresponding item class
    instance (e.g. that cybernetic subprocessor is represented
    by Implant class instance).

    Details:
    To determine item class matching to eve type, only eve type
    attributes are used.
    """

    def __init__(self):
        self.__items = set()

    def register_item(self, item):
        self.__items.add(item)

    def unregister_item(self, item):
        self.__items.discard(item)

    def validate(self):
        tainted_items = {}
        for item in self.__items:
            # Get validator function for class of passed item.
            # If it is not found or fails, seek for 'right'
            # item class for the eve type
            try:
                validator_func = CLASS_VALIDATORS[type(item)]
            except KeyError:
                tainted_items[item] = self.__get_error_data(item)
            else:
                if validator_func(item._eve_type) is not True:
                    tainted_items[item] = self.__get_error_data(item)
        if tainted_items:
            raise RegisterValidationError(tainted_items)

    def __get_error_data(self, item):
        expected_classes = []
        # Cycle through our class validator dictionary and
        # seek for acceptable classes for this eve type
        for item_class, validator_func in CLASS_VALIDATORS.items():
            if validator_func(item._eve_type) is True:
                expected_classes.append(item_class)
        error_data = ItemClassErrorData(
            item_class=type(item),
            expected_classes=set(expected_classes)
        )
        return error_data

    @property
    def restriction_type(self):
        return Restriction.item_class
