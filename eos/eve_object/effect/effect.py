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
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.util.cached_property import cached_property
from eos.util.repr import make_repr_str


class Effect:
    """Represents single eve effect.

    Effects are the building blocks which describe what its carrier does with
    other items.

    Attributes:
        id: Identifier of the effect.
        category_id: Defines effect category, which influences when and how
            effect is applied - always, when item is active, overloaded, etc.
        is_offensive: Whether effect is offensive (e.g. guns).
        is_assistance: Whether the effect is assistance (e.g. remote repairers).
        duration_attr_id: Value of attribute with this ID on carrier item
            defines effect cycle time.
        discharge_attr_id: Value of attribute with this ID on carrier item
            defines how much cap does this effect take per cycle.
        range_attr_id: Value of attribute with this ID on carrier item defines
            max range where effect is applied to its full potency.
        falloff_attr_id: Value of attribute with this ID on carrier item defines
            additional range where effect is still applied, but with diminished
            potency.
        tracking_speed_attr_id: Value of attribute with this ID on carrier item
            defines tracking speed which reduces effect efficiency vs targets
            which are small and have decent angular velocity.
        fitting_usage_chance_attr_id: Value of attribute with this ID on carrier
            item defines chance of this effect being applied when item is added
            to fit, e.g. booster side-effects.
        build_status: Effect-to-modifier build status.
        modifiers: Iterable with modifiers. It's actually not effect which
            describes modifications this item does, but these child objects.
    """

    def __init__(
            self, effect_id, category_id=None, is_offensive=False,
            is_assistance=False, duration_attr_id=None,
            discharge_attr_id=None, range_attr_id=None,
            falloff_attr_id=None, tracking_speed_attr_id=None,
            fitting_usage_chance_attr_id=None, build_status=None,
            modifiers=()):
        self.id = effect_id
        self.category_id = category_id
        self.is_offensive = bool(is_offensive)
        self.is_assistance = bool(is_assistance)
        self.duration_attr_id = duration_attr_id
        self.discharge_attr_id = discharge_attr_id
        self.range_attr_id = range_attr_id
        self.falloff_attr_id = falloff_attr_id
        self.tracking_speed_attr_id = tracking_speed_attr_id
        self.fitting_usage_chance_attr_id = fitting_usage_chance_attr_id
        self.build_status = build_status
        self.modifiers = modifiers

    # Format: {effect category ID: state ID}
    __effect_state_map = {
        EffectCategoryId.passive: State.offline,
        EffectCategoryId.active: State.active,
        EffectCategoryId.target: State.active,
        EffectCategoryId.online: State.online,
        EffectCategoryId.overload: State.overload,
        EffectCategoryId.system: State.offline}

    @cached_property
    def _state(self):
        """Returns 'state' of effect.

        It means if carrier item takes this state or higher, effect activates.

        Returns:
            State in the form of ID, as defined in State enum.
        """
        return self.__effect_state_map[self.category_id]

    # Getters for charge-related entities
    def get_charge(self, item):
        """Get charge which should be used by this effect."""
        if self.get_autocharge_type_id(item) is not None:
            charge = item.autocharges.get(self.id)
        else:
            charge = item.charge
        return charge

    def get_autocharge_type_id(self, _):
        return None

    def get_cycles_until_reload(self, _):
        return None

    # Getters for effect-referenced attributes
    def get_duration(self, item):
        raw_time = self.__safe_get_attr_value(item, self.duration_attr_id)
        # Time is specified in milliseconds, but we want to return seconds
        try:
            return raw_time / 1000
        except TypeError:
            return raw_time

    def get_cap_use(self, item):
        return self.__safe_get_attr_value(item, self.discharge_attr_id)

    def get_optimal_range(self, item):
        return self.__safe_get_attr_value(item, self.range_attr_id)

    def get_falloff_range(self, item):
        return self.__safe_get_attr_value(item, self.falloff_attr_id)

    def get_tracking_speed(self, item):
        return self.__safe_get_attr_value(
            item, self.tracking_speed_attr_id)

    def get_fitting_usage_chance(self, item):
        return self.__safe_get_attr_value(
            item, self.fitting_usage_chance_attr_id)

    @staticmethod
    def __safe_get_attr_value(item, attr_id):
        if attr_id is None:
            return None
        return item.attrs.get(attr_id)

    # Misc getters
    def get_reactivation_delay(self, item):
        raw_time = item.attrs.get(AttrId.module_reactivation_delay)
        try:
            return raw_time / 1000
        except TypeError:
            return raw_time

    # Auxiliary methods
    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)
