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


from eos.const.eos import State
from eos.const.eve import EffectCategory
from eos.util.cached_property import CachedProperty


class Effect:
    """
    Represents a single effect. Effects are the building blocks which describe what its carrier
    does with other items.
    """

    def __init__(
        self,
        effect_id=None,
        category=None,
        is_offensive=None,
        is_assistance=None,
        duration_attribute=None,
        discharge_attribute=None,
        range_attribute=None,
        falloff_attribute=None,
        tracking_speed_attribute=None,
        fitting_usage_chance_attribute=None,
        build_status=None,
        modifiers=()
    ):
        self.id = effect_id

        # Effect category actually describes type of effect, which determines
        # when it is applied - always, when item is active, overloaded, etc.
        self.category = category

        # Whether the effect is offensive (e.g. guns)
        self.is_offensive = bool(is_offensive) if is_offensive is not None else None

        # Whether the effect is helpful (e.g. remote repairers)
        self.is_assistance = bool(is_assistance) if is_assistance is not None else None

        # If effect is default effect of active holder, attribute
        # with this ID on holder defines cycle time
        self.duration_attribute = duration_attribute

        # If effect is default effect of active holder, attribute
        # with this ID on holder defines ship's cap drained per cycle
        self.discharge_attribute = discharge_attribute

        # If effect needs to know its optimal range, attribute value on
        # holder referenced by this ID will contain it
        self.range_attribute = range_attribute

        # If effect needs to know its falloff range, attribute value on
        # holder referenced by this ID will contain it
        self.falloff_attribute = falloff_attribute

        # If effect needs to know its tracking speed, attribute value on
        # holder referenced by this ID will contain it
        self.tracking_speed_attribute = tracking_speed_attribute

        # Refers attribute, which determines chance of effect
        # getting applied when its carrier is added to fit
        self.fitting_usage_chance_attribute = fitting_usage_chance_attribute

        # Stores expression->modifiers parsing status
        self.build_status = build_status

        # Stores Modifiers which are assigned to given effect
        self.modifiers = modifiers

    # Format: {effect category ID: state ID}
    __effect_state_map = {
        EffectCategory.passive: State.offline,
        EffectCategory.active: State.active,
        EffectCategory.target: State.active,
        EffectCategory.online: State.online,
        EffectCategory.overload: State.overload,
        EffectCategory.system: State.offline
    }

    @CachedProperty
    def _state(self):
        """
        Return state of effect - if holder takes this state or
        higher, effect activates.
        """
        return self.__effect_state_map[self.category]
