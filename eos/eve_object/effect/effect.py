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


from eos.const.eos import State
from eos.const.eve import EffectCategoryId
from eos.data.cachable import BaseCachable
from eos.util.cached_property import cached_property
from eos.util.repr import make_repr_str
from ..custom.effect import customize_effect
from ..modifier import DogmaModifier


class Effect(BaseCachable):
    """Represents single eve effect.

    Effects are the building blocks which describe what its carrier does with
    other items.

    Attributes:
        id: Identifier of the effect.
        category: Defines effect category, which influences when and how effect
            is applied - always, when item is active, overloaded, etc.
        is_offensive: Whether effect is offensive (e.g. guns).
        is_assistance: Whether the effect is assistance (e.g. remote repairers).
        duration_attribute: Value of attribute with this ID on carrier item
            defines effect cycle time.
        discharge_attribute: Value of attribute with this ID on carrier item
            defines how much cap does this effect take per cycle.
        range_attribute: Value of attribute with this ID on carrier item defines
            max range where effect is applied to its full potency.
        falloff_attribute: Value of attribute with this ID on carrier item
            defines additional range where effect is still applied, but with
            diminished potency.
        tracking_speed_attribute: Value of attribute with this ID on carrier
            item defines tracking speed which reduces effect efficiency vs
            targets which are small and have decent angular velocity.
        fitting_usage_chance_attribute: Value of attribute with this ID on
            carrier item defines chance of this effect being applied when item
            is added to fit, e.g. booster side-effects.
        build_status: Effect->modifier build status.
        modifiers: Iterable with modifiers. It's actually not effect which
            describes modifications this item does, but these child objects.
    """

    def __init__(
        self,
        effect_id,
        category=None,
        is_offensive=False,
        is_assistance=False,
        duration_attribute=None,
        discharge_attribute=None,
        range_attribute=None,
        falloff_attribute=None,
        tracking_speed_attribute=None,
        fitting_usage_chance_attribute=None,
        build_status=None,
        modifiers=(),
        customize=True
    ):
        self.id = effect_id
        self.category = category
        self.is_offensive = bool(is_offensive)
        self.is_assistance = bool(is_assistance)
        self.duration_attribute = duration_attribute
        self.discharge_attribute = discharge_attribute
        self.range_attribute = range_attribute
        self.falloff_attribute = falloff_attribute
        self.tracking_speed_attribute = tracking_speed_attribute
        self.fitting_usage_chance_attribute = fitting_usage_chance_attribute
        self.build_status = build_status
        self.modifiers = modifiers
        if customize:
            customize_effect(self)

    # Format: {effect category ID: state ID}
    __effect_state_map = {
        EffectCategoryId.passive: State.offline,
        EffectCategoryId.active: State.active,
        EffectCategoryId.target: State.active,
        EffectCategoryId.online: State.online,
        EffectCategoryId.overload: State.overload,
        EffectCategoryId.system: State.offline
    }

    @cached_property
    def _state(self):
        """Returns 'state' of effect.

        It means if carrier item takes this state or higher, effect activates.

        Returns:
            State in the form of ID, as defined in State enum.
        """
        return self.__effect_state_map[self.category]

    # Getters for effect-referenced attributes
    def get_duration(self, item):
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
            tuple(
                m.compress()
                for m in self.modifiers
                if isinstance(m, DogmaModifier))
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
            modifiers=tuple(
                DogmaModifier.decompress(cache_handler, cm)
                for cm in compressed[11])
        )

    # Auxiliary methods
    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)
