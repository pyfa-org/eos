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


import math

from eos.const.eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.util.cached_property import cached_property
from eos.util.repr import make_repr_str
from .cycle import CycleInfo, CycleSequence


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
            Each modifier instance must belong to only one effect, otherwise
            attribute calculation may be improper in several edge cases.
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
            return item.autocharges.get(self.id)
        try:
            return item.charge
        except AttributeError:
            return None

    def get_autocharge_type_id(self, item):
        """Return ID of type which should be used as base for autocharge.

        Autocharges are automatically loaded charges which are defined by
        effects. If None is returned, it means this effect defines no
        autocharge.
        """
        return None

    def get_cycles_until_reload(self, item):
        """Get how many cycles effect can run until it has to be reloaded.

        If effect cannot be cycled, returns None.
        """
        return math.inf

    def get_reload_time(self, item):
        """Get effect reload time in seconds.

        If effect cannot be reloaded, returns None.
        """
        try:
            return item.reload_time
        except AttributeError:
            return None

    # Getters for effect-referenced attributes
    def get_duration(self, item):
        time_ms = self.__safe_get_attr_value(item, self.duration_attr_id)
        # Time is specified in milliseconds, but we want to return seconds
        try:
            return time_ms / 1000
        except TypeError:
            return time_ms

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

    # Cycle-related getters
    def get_forced_inactive_time(self, item):
        time_ms = item.attrs.get(AttrId.module_reactivation_delay)
        try:
            return time_ms / 1000
        except TypeError:
            return 0

    def get_cycle_parameters(self, item, reload):
        """Get cycle parameters for specific effect on specific item.

        Args:
            item: Item which carries current effect.
            reload: Boolean flag which controls if we should take reload into
                consideration or not.

        Returns:
            Cycle parameters described by CycleInfo or CycleSequence class
            instances.
        """
        cycles_until_reload = self.get_cycles_until_reload(item) or 0
        # Module cannot cycle at all
        if cycles_until_reload <= 0:
            return None
        active_time = self.get_duration(item) or 0
        forced_inactive_time = self.get_forced_inactive_time(item) or 0
        reload_time = self.get_reload_time(item)
        # Effects which cannot be reloaded have the same processing whether
        # caller wants to take reload time into account or not
        if reload_time is None and cycles_until_reload < math.inf:
            final_cycles = 1
            early_cycles = cycles_until_reload - final_cycles
            # Single cycle until effect cannot run anymore
            if early_cycles == 0:
                return CycleInfo(active_time, 0, 1)
            # Multiple cycles with the same parameters
            if forced_inactive_time == 0:
                return CycleInfo(active_time, 0, cycles_until_reload)
            # Multiple cycles with different parameters
            return CycleSequence((
                CycleInfo(active_time, forced_inactive_time, early_cycles),
                CycleInfo(active_time, 0, final_cycles)
            ), 1)
        # Module cycles the same way all the time in 3 cases:
        # 1) caller doesn't want to take into account reload time
        # 2) effect does not have to reload anything to keep running
        # 3) effect has enough time to reload during inactivity periods
        if (
            not reload or
            cycles_until_reload == math.inf or
            forced_inactive_time >= reload_time
        ):
            return CycleInfo(active_time, forced_inactive_time, math.inf)
        # We've got to take reload into consideration
        else:
            final_cycles = 1
            early_cycles = cycles_until_reload - final_cycles
            # If effect has to reload after each its cycle, then its parameters
            # are the same all the time
            if early_cycles == 0:
                return CycleInfo(active_time, reload_time, math.inf)
            return CycleSequence((
                CycleInfo(active_time, forced_inactive_time, early_cycles),
                CycleInfo(active_time, reload_time, final_cycles)
            ), math.inf)

    # Auxiliary methods
    def __repr__(self):
        spec = ['id']
        return make_repr_str(self, spec)
