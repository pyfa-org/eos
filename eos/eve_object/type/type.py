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
from eos.const.eve import AttributeId
from eos.data.cachable import BaseCachable
from eos.util.cached_property import cached_property
from eos.util.default import DEFAULT
from eos.util.repr import make_repr_str
from ..custom.type import customize_type


FighterAbility = namedtuple(
    'FighterAbility',
    ('cooldown_time', 'charge_quantity', 'rearm_time')
)


class Type(BaseCachable):
    """Represents eve type with all its metadata.

    All characters, ships, incursion system-wide effects are actually eve types.

    Attributes:
        id: Identifier of the eve type.
        group: Group ID of the eve type.
        category: Category ID of the eve type. Normally it's attribute of group,
            but as we do not need groups as separate objects, categories were
            'demoted' into type attribute.
        attributes: Map with base attribute values for this type in {attribute
            ID: attribute value} format.
        effects: Map with effects this type has in {effect ID: effect} format.
        default_effect: Default effect of the type. When item is activated, it
            gets run.
        fighter_abilities: Map with fighter abilities in {ability ID: (cooldown
            time, charge amount, rearm time) format.
    """

    def __init__(
        self,
        type_id,
        group=None,
        category=None,
        attributes=DEFAULT,
        effects=(),
        default_effect=None,
        fighter_abilities=DEFAULT,
        customize=True
    ):
        self.id = type_id
        self.group = group
        self.category = category
        if attributes is DEFAULT:
            self.attributes = {}
        else:
            self.attributes = attributes
        self.effects = {e.id: e for e in effects}
        self.default_effect = default_effect
        if fighter_abilities is DEFAULT:
            self.fighter_abilities = {}
        else:
            self.fighter_abilities = fighter_abilities
        if customize:
            customize_type(self)

    # Define attributes which describe eve type skill requirement details
    # Format: {skill eve type attribute ID: skill level attribute ID}
    __skillrq_attrs = {
        AttributeId.required_skill_1: AttributeId.required_skill_1_level,
        AttributeId.required_skill_2: AttributeId.required_skill_2_level,
        AttributeId.required_skill_3: AttributeId.required_skill_3_level,
        AttributeId.required_skill_4: AttributeId.required_skill_4_level,
        AttributeId.required_skill_5: AttributeId.required_skill_5_level,
        AttributeId.required_skill_6: AttributeId.required_skill_6_level
    }

    @cached_property
    def required_skills(self):
        """Get skill requirements.

        Returns:
            Map between skill eve type IDs and corresponding skill levels, which
            are required to use type.
        """
        required_skills = {}
        for srq_attr in self.__skillrq_attrs:
            # Skip skill requirement attribute pair if any of them is not
            # available
            try:
                srq = self.attributes[srq_attr]
            except KeyError:
                continue
            try:
                srq_lvl = self.attributes[self.__skillrq_attrs[srq_attr]]
            except KeyError:
                continue
            required_skills[int(srq)] = int(srq_lvl)
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

    # Cache-related methods
    def compress(self):
        return (
            self.id,
            self.group,
            self.category,
            tuple(self.attributes.items()),
            tuple(self.effects.keys()),
            None if self.default_effect is None else self.default_effect.id,
            tuple(self.fighter_abilities.items())
        )

    @classmethod
    def decompress(cls, cache_handler, compressed):
        defeff_id = compressed[5]
        if defeff_id is None:
            default_effect = None
        else:
            default_effect = cache_handler.get_effect(defeff_id)
        return cls(
            type_id=compressed[0],
            group=compressed[1],
            category=compressed[2],
            attributes={k: v for k, v in compressed[3]},
            effects=tuple(
                cache_handler.get_effect(eid)
                for eid in compressed[4]),
            default_effect=default_effect,
            fighter_abilities={k: v for k, v in compressed[6]}
        )

    # Auxiliary methods
    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)
