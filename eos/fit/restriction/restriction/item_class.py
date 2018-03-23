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
from eos.const.eve import AttrId
from eos.const.eve import EffectId
from eos.const.eve import TypeCategoryId
from eos.const.eve import TypeGroupId
from eos.fit.item import Booster
from eos.fit.item import Character
from eos.fit.item import Charge
from eos.fit.item import Drone
from eos.fit.item import EffectBeacon
from eos.fit.item import FighterSquad
from eos.fit.item import Implant
from eos.fit.item import ModuleHigh
from eos.fit.item import ModuleLow
from eos.fit.item import ModuleMed
from eos.fit.item import Rig
from eos.fit.item import Ship
from eos.fit.item import Skill
from eos.fit.item import Stance
from eos.fit.item import Subsystem
from .base import BaseRestriction
from ..exception import RestrictionValidationError


ItemClassErrorData = namedtuple(
    'ItemClassErrorData', ('item_class', 'allowed_classes'))


CLASS_VALIDATORS = {
    Booster: lambda item_type:
        item_type.category_id == TypeCategoryId.implant and
        AttrId.boosterness in item_type.attrs,
    Character: lambda item_type:
        item_type.group_id == TypeGroupId.character,
    Charge: lambda item_type:
        item_type.category_id == TypeCategoryId.charge,
    Drone: lambda item_type:
        item_type.category_id == TypeCategoryId.drone,
    EffectBeacon: lambda item_type:
        item_type.group_id == TypeGroupId.effect_beacon,
    FighterSquad: lambda item_type:
        item_type.category_id == TypeCategoryId.fighter and (
            AttrId.fighter_squadron_is_heavy in item_type.attrs or
            AttrId.fighter_squadron_is_light in item_type.attrs or
            AttrId.fighter_squadron_is_support in item_type.attrs),
    Implant: lambda item_type:
        item_type.category_id == TypeCategoryId.implant and
        AttrId.implantness in item_type.attrs,
    ModuleHigh: lambda item_type:
        item_type.category_id == TypeCategoryId.module and
        EffectId.hi_power in item_type.effects,
    ModuleMed: lambda item_type:
        item_type.category_id == TypeCategoryId.module and
        EffectId.med_power in item_type.effects,
    ModuleLow: lambda item_type:
        item_type.category_id == TypeCategoryId.module and
        EffectId.lo_power in item_type.effects,
    Rig: lambda item_type:
        item_type.category_id == TypeCategoryId.module and
        EffectId.rig_slot in item_type.effects,
    Ship: lambda item_type:
        item_type.category_id == TypeCategoryId.ship,
    Skill: lambda item_type:
        item_type.category_id == TypeCategoryId.skill,
    Stance: lambda item_type:
        item_type.group_id == TypeGroupId.ship_modifier,
    Subsystem: lambda item_type:
        item_type.category_id == TypeCategoryId.subsystem and
        EffectId.subsystem in item_type.effects}


class ItemClassRestrictionRegister(BaseRestriction):
    """Check that item type is wrapped by corresponding item class instance.

    For example, cybernetic subprocessor should be represented by Implant class
    instance.

    Details:
        To determine item class matching to item type, only item type attributes
            are used.
    """

    type = Restriction.item_class

    def __init__(self, fit):
        self.__fit = fit

    def validate(self):
        tainted_items = {}
        for item in self.__fit._loaded_item_iter():
            # Get validator function for class of passed item. If it is not
            # found or fails, seek for 'right' item class for the item type
            try:
                validator_func = CLASS_VALIDATORS[type(item)]
            except KeyError:
                tainted_items[item] = self.__get_error_data(item)
            else:
                if validator_func(item._type) is not True:
                    tainted_items[item] = self.__get_error_data(item)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    def __get_error_data(self, item):
        allowed_classes = set()
        # Cycle through our class validator dictionary and seek for acceptable
        # classes for this item type
        for item_class, validator_func in CLASS_VALIDATORS.items():
            if validator_func(item._type) is True:
                allowed_classes.add(item_class)
        error_data = ItemClassErrorData(
            item_class=type(item),
            allowed_classes=frozenset(allowed_classes))
        return error_data
