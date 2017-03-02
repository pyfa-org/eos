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


from eos.const.eos import Slot, State
from eos.const.eve import Attribute, Effect, EffectCategory
from eos.util.cached_property import cached_property
from eos.util.repr import make_repr_str
from .custom import customize_type


class Type:
    """
    Type represents any eve type. All characters, ships,
    incursion system-wide effects are actually eve types.
    """

    def __init__(
        self, type_id, group=None, category=None, attributes=None,
        effects=(), default_effect=None
    ):
        self.id = type_id

        # The groupID of the type, integer
        self.group = group

        # The category ID of the type, integer
        self.category = category

        # The attributes of this type, used as base for calculation of modified
        # attributes, thus they should stay immutable
        # Format: {attribute ID: attribute value}
        self.attributes = attributes if attributes is not None else {}

        # Iterable with effects this type has, they describe modifications
        # which this type applies
        self.effects = effects

        # Default effect of eve type, which defines its several major properties
        self.default_effect = default_effect

        customize_type(self)

    @property
    def modifiers(self):
        """ Get all modifiers spawned by eve type effects."""
        modifiers = []
        for effect in self.effects:
            for modifier in effect.modifiers:
                modifiers.append(modifier)
        return modifiers

    # Define attributes which describe eve type skill requirement details
    # Format: {skill eve type attribute ID: skill level attribute ID}
    __skillrq_attrs = {
        Attribute.required_skill_1: Attribute.required_skill_1_level,
        Attribute.required_skill_2: Attribute.required_skill_2_level,
        Attribute.required_skill_3: Attribute.required_skill_3_level,
        Attribute.required_skill_4: Attribute.required_skill_4_level,
        Attribute.required_skill_5: Attribute.required_skill_5_level,
        Attribute.required_skill_6: Attribute.required_skill_6_level
    }

    @cached_property
    def required_skills(self):
        """
        Get skill requirements.

        Return value:
        Dictionary with IDs of skills and corresponding skill levels,
        which are required to use type
        """
        required_skills = {}
        for srq_attr in self.__skillrq_attrs:
            # Skip skill requirement attribute pair if any
            # of them is not available
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
        """
        Get highest state this type is allowed to take.

        Return value:
        State class' attribute value, representing highest state
        """
        # All types can be at least offline,
        # even when they have no effects
        max_state = State.offline
        for effect in self.effects:
            max_state = max(max_state, effect._state)
        return max_state

    @cached_property
    def is_targeted(self):
        """
        Report if type is targeted or not. Targeted types cannot be
        activated w/o target selection.

        Return value:
        Boolean targeted flag
        """
        # Assume type is unable to target by default
        targeted = False
        for effect in self.effects:
            # If any of effects is targeted, then type is targeted
            if effect.category == EffectCategory.target:
                targeted = True
                break
        return targeted

    # Format: {effect ID: slot ID}
    __effect_slot_map = {
        Effect.lo_power: Slot.module_low,
        Effect.hi_power: Slot.module_high,
        Effect.med_power: Slot.module_med,
        Effect.launcher_fitted: Slot.launcher,
        Effect.turret_fitted: Slot.turret,
        Effect.rig_slot: Slot.rig,
        Effect.subsystem: Slot.subsystem
    }

    @cached_property
    def slots(self):
        """
        Get types of slots this type occupies.

        Return value:
        Set with slot types
        """
        # Container for slot types eve type uses
        slots = set()
        for effect in self.effects:
            # Convert effect ID to slot type eve type takes
            try:
                slot = self.__effect_slot_map[effect.id]
            # Silently skip effect if it's not in map
            except KeyError:
                pass
            else:
                slots.add(slot)
        return slots

    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)
