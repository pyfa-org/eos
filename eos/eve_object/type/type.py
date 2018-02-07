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

from eos.const.eos import State
from eos.const.eve import AttrId
from eos.const.eve import fighter_ability_map
from eos.util.cached_property import cached_property
from eos.util.repr import make_repr_str


AbilityData = namedtuple('AbilityData', ('cooldown_time', 'charge_quantity'))


class Type:
    """Represents item type with all its metadata.

    All characters, ships, incursion system-wide effects are based on item
    types.

    Attributes:
        id: Identifier of the item type.
        group_id: Group ID of the item type.
        category_id: Category ID of the item type. Normally it's attribute of
            group, but as we do not need groups as separate objects, categories
            were 'demoted' into type attribute.
        attrs: Map with base attribute values for this type in {attribute
            ID: attribute value} format.
        effects: Map with effects this type has in {effect ID: effect} format.
        default_effect: Default effect of the type. When item is activated, it
            gets run.
        abilities_data: Type-specific data for abilities in {ability ID:
            (cooldown time, charge quantity)} format.
    """

    def __init__(
            self, type_id, group_id=None, category_id=None, attrs=None,
            effects=(), default_effect=None, abilities_data=None):
        self.id = type_id
        self.group_id = group_id
        self.category_id = category_id
        if attrs is None:
            attrs = {}
        self.attrs = attrs
        self.effects = {e.id: e for e in effects}
        self.default_effect = default_effect
        if abilities_data is None:
            abilities_data = {}
        self.abilities_data = abilities_data

    @cached_property
    def effects_data(self):
        """Get extended effect data."""
        effects_data = {}
        for ability_id, ability_data in self.abilities_data.items():
            effect_id = fighter_ability_map[ability_id]
            effects_data[effect_id] = ability_data
        return effects_data

    # Define attributes which describe item type skill requirement details
    # Format: {skill type attribute ID: skill level attribute ID}
    __skillrq_attrs = {
        AttrId.required_skill_1: AttrId.required_skill_1_level,
        AttrId.required_skill_2: AttrId.required_skill_2_level,
        AttrId.required_skill_3: AttrId.required_skill_3_level,
        AttrId.required_skill_4: AttrId.required_skill_4_level,
        AttrId.required_skill_5: AttrId.required_skill_5_level,
        AttrId.required_skill_6: AttrId.required_skill_6_level}

    @cached_property
    def required_skills(self):
        """Get skill requirements.

        Returns:
            Map between skill type IDs and corresponding skill levels, which are
            required to use this item type.
        """
        required_skills = {}
        for skill_attr_id in self.__skillrq_attrs:
            # Skip skill requirement attribute pair if any of them is not
            # available
            try:
                skill_type_id = self.attrs[skill_attr_id]
            except KeyError:
                continue
            try:
                skill_lvl = self.attrs[self.__skillrq_attrs[skill_attr_id]]
            except KeyError:
                continue
            required_skills[int(skill_type_id)] = int(skill_lvl)
        return required_skills

    @cached_property
    def max_state(self):
        """Get highest state this type is allowed to take.

        Returns:
            State in the form of ID, as defined in State enum.
        """
        # All types can be at least offline, even when they have no effects
        max_state = State.offline
        for effect in self.effects.values():
            max_state = max(max_state, effect._state)
        return max_state

    # Auxiliary methods
    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)
