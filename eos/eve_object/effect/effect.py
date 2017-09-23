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


from eos.const.eos import State
from eos.const.eve import EffectCategory
from eos.data.cachable import BaseCachable
from eos.util.cached_property import cached_property
from eos.util.repr import make_repr_str
from ..custom.effect import customize_effect
from ..modifier import DogmaModifier


class Effect(BaseCachable):
    """
    Represents a single effect. Effects are the building blocks which describe what its carrier
    does with other items.
    """

    def __init__(
        self, effect_id, category=None, is_offensive=None, is_assistance=None,
        duration_attribute=None, discharge_attribute=None, range_attribute=None,
        falloff_attribute=None, tracking_speed_attribute=None,
        fitting_usage_chance_attribute=None, build_status=None,
        modifiers=(), customize=True
    ):
        self.id = effect_id

        # Effect category actually describes type of effect, which determines
        # when it is applied - always, when item is active, overloaded, etc.
        self.category = category

        # Whether the effect is offensive (e.g. guns)
        self.is_offensive = bool(is_offensive) if is_offensive is not None else None

        # Whether the effect is helpful (e.g. remote repairers)
        self.is_assistance = bool(is_assistance) if is_assistance is not None else None

        # If effect is default effect of eve type, attribute with this ID
        # on item defines cycle time
        self.duration_attribute = duration_attribute

        # If effect is default effect of eve type, attribute with this ID
        # on item defines ship's cap drained per cycle
        self.discharge_attribute = discharge_attribute

        # If effect needs to know its optimal range, attribute value on
        # item referenced by this ID will contain it
        self.range_attribute = range_attribute

        # If effect needs to know its falloff range, attribute value on
        # item referenced by this ID will contain it
        self.falloff_attribute = falloff_attribute

        # If effect needs to know its tracking speed, attribute value on
        # item referenced by this ID will contain it
        self.tracking_speed_attribute = tracking_speed_attribute

        # Refers attribute, which determines chance of effect
        # getting applied when its carrier is added to fit
        self.fitting_usage_chance_attribute = fitting_usage_chance_attribute

        # Stores expression->modifiers parsing status
        self.build_status = build_status

        # Stores Modifiers which are assigned to given effect
        self.modifiers = modifiers

        if customize:
            customize_effect(self)

    # Format: {effect category ID: state ID}
    __effect_state_map = {
        EffectCategory.passive: State.offline,
        EffectCategory.active: State.active,
        EffectCategory.target: State.active,
        EffectCategory.online: State.online,
        EffectCategory.overload: State.overload,
        EffectCategory.system: State.offline
    }

    @cached_property
    def _state(self):
        """
        Return state of effect - if eve type takes this state or
        higher, effect activates.
        """
        return self.__effect_state_map[self.category]

    # Getters for effect-referenced attributes
    def get_cycle_time(self, item):
        raw_time = self.__safe_get_attr(item, self.duration_attribute)
        # Time is specified in milliseconds, but we want to return seconds
        try:
            return raw_time / 1000
        except TypeError:
            return raw_time

    def get_cap_use(self, item):
        return self.__safe_get_attr(item, self.discharge_attribute)

    def get_optimal_range(self, item):
        return self.__safe_get_attr(item, self.range_attribute)

    def get_falloff_range(self, item):
        return self.__safe_get_attr(item, self.falloff_attribute)

    def get_tracking_speed(self, item):
        return self.__safe_get_attr(item, self.tracking_speed_attribute)

    def get_fitting_usage_chance(self, item):
        return self.__safe_get_attr(item, self.fitting_usage_chance_attribute)

    @staticmethod
    def __safe_get_attr(item, attr_id):
        if attr_id is None:
            return None
        return item.attributes.get(attr_id)

    # Cache-related methods
    def compress(self):
        return (
            self.id,
            self.category,
            self.is_offensive,
            self.is_assistance,
            self.duration_attribute,
            self.discharge_attribute,
            self.range_attribute,
            self.falloff_attribute,
            self.tracking_speed_attribute,
            self.fitting_usage_chance_attribute,
            self.build_status,
            tuple(m.compress() for m in self.modifiers if isinstance(m, DogmaModifier))
        )

    @classmethod
    def decompress(cls, cache_handler, compressed):
        return cls(
            effect_id=compressed[0],
            category=compressed[1],
            is_offensive=compressed[2],
            is_assistance=compressed[3],
            duration_attribute=compressed[4],
            discharge_attribute=compressed[5],
            range_attribute=compressed[6],
            falloff_attribute=compressed[7],
            tracking_speed_attribute=compressed[8],
            fitting_usage_chance_attribute=compressed[9],
            build_status=compressed[10],
            modifiers=tuple(DogmaModifier.decompress(cache_handler, cm) for cm in compressed[11])
        )

    # Auxiliary methods
    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)
