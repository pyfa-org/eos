# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
            effects=(), default_effect=None, abilities_data=None, required_skills=None):
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
        if required_skills is None:
            required_skills = {}
        self.required_skills = required_skills

    @cached_property
    def effects_data(self):
        """Get extended effect data."""
        effects_data = {}
        for ability_id, ability_data in self.abilities_data.items():
            effect_id = fighter_ability_map[ability_id]
            effects_data[effect_id] = ability_data
        return effects_data

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
