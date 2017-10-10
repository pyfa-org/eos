# ==============================================================================
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
# ==============================================================================


from collections import namedtuple

from eos.const.eos import Restriction
from eos.const.eve import AttributeId, CategoryId, EffectId, GroupId
from eos.fit.item import *
from eos.fit.pubsub.message import InstrItemAdd, InstrItemRemove
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


ItemClassErrorData = namedtuple(
    'ItemClassErrorData',
    ('item_class', 'expected_classes')
)


CLASS_VALIDATORS = {
    Booster: lambda eve_type: (
        eve_type.category == CategoryId.implant and
        AttributeId.boosterness in eve_type.attributes
    ),
    Character: lambda eve_type: eve_type.group == GroupId.character,
    Charge: lambda eve_type: eve_type.category == CategoryId.charge,
    Drone: lambda eve_type: eve_type.category == CategoryId.drone,
    EffectBeacon: lambda eve_type: eve_type.group == GroupId.effect_beacon,
    FighterSquad: lambda eve_type: (
        eve_type.category == CategoryId.fighter and (
            AttributeId.fighter_squadron_is_heavy in eve_type.attributes or
            AttributeId.fighter_squadron_is_light in eve_type.attributes or
            AttributeId.fighter_squadron_is_support in eve_type.attributes
        )
    ),
    Implant: lambda eve_type: (
        eve_type.category == CategoryId.implant and
        AttributeId.implantness in eve_type.attributes
    ),
    ModuleHigh: lambda eve_type: (
        eve_type.category == CategoryId.module and
        EffectId.hi_power in eve_type.effects
    ),
    ModuleMed: lambda eve_type: (
        eve_type.category == CategoryId.module and
        EffectId.med_power in eve_type.effects
    ),
    ModuleLow: lambda eve_type: (
        eve_type.category == CategoryId.module and
        EffectId.lo_power in eve_type.effects
    ),
    Rig: lambda eve_type: (
        eve_type.category == CategoryId.module and
        EffectId.rig_slot in eve_type.effects
    ),
    Ship: lambda eve_type: eve_type.category == CategoryId.ship,
    Skill: lambda eve_type: eve_type.category == CategoryId.skill,
    Stance: lambda eve_type: eve_type.group == GroupId.ship_modifier,
    Subsystem: lambda eve_type: (
        eve_type.category == CategoryId.subsystem and
        EffectId.subsystem in eve_type.effects
    )
}


class ItemClassRestrictionRegister(BaseRestrictionRegister):
    """Check that eve type is wrapped by corresponding item class instance.


    For example, cybernetic subprocessor should be represented by Implant class
    instance.

    Details:
        To determine item class matching to eve type, only eve type attributes
            are used.
    """

    def __init__(self, msg_broker):
        self.__items = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_item_addition(self, message):
        self.__items.add(message.item)

    def _handle_item_removal(self, message):
        self.__items.discard(message.item)

    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal
    }

    def validate(self):
        tainted_items = {}
        for item in self.__items:
            # Get validator function for class of passed item. If it is not
            # found or fails, seek for 'right' item class for the eve type
            try:
                validator_func = CLASS_VALIDATORS[type(item)]
            except KeyError:
                tainted_items[item] = self.__get_error_data(item)
            else:
                if validator_func(item._eve_type) is not True:
                    tainted_items[item] = self.__get_error_data(item)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    def __get_error_data(self, item):
        expected_classes = []
        # Cycle through our class validator dictionary and seek for acceptable
        # classes for this eve type
        for item_class, validator_func in CLASS_VALIDATORS.items():
            if validator_func(item._eve_type) is True:
                expected_classes.append(item_class)
        error_data = ItemClassErrorData(
            item_class=type(item),
            expected_classes=set(expected_classes)
        )
        return error_data

    @property
    def type(self):
        return Restriction.item_class
