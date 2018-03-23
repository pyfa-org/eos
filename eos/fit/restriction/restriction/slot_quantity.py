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


from abc import ABCMeta
from abc import abstractmethod
from collections import namedtuple

from eos.const.eos import Restriction
from .base import BaseRestriction
from ..exception import RestrictionValidationError


SlotQuantityErrorData = namedtuple(
    'SlotQuantityErrorData', ('used', 'total'))


class BaseSlotRestriction(BaseRestriction, metaclass=ABCMeta):

    def __init__(self, fit):
        self._fit = fit

    @property
    @abstractmethod
    def _stat_name(self):
        ...


class UnorderedSlotRestriction(BaseSlotRestriction):
    """Base class for all unordered slot quantity restrictions."""

    def validate(self):
        stats = getattr(self._fit.stats, self._stat_name)
        used = stats.used
        total = stats.total or 0
        # If quantity of items which take this slot is bigger than quantity of
        # available slots, then all items which use this slot are tainted
        if used > total:
            tainted_items = {}
            for item in stats._users:
                tainted_items[item] = SlotQuantityErrorData(
                    used=used, total=total)
            raise RestrictionValidationError(tainted_items)


class HighSlotRestriction(BaseRestriction):
    """Quantity of high-slot items should not exceed limit.

    Details:
        Container with high slot items is used for validation.
        Only items which are positioned outside of slots provided by ship raise
            error.
    """

    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        used, total = self._fit.stats.high_slots
        if used > total:
            tainted_items = {}
            for item in self._fit.modules.high[total:]:
                tainted_items[item] = SlotQuantityErrorData(
                    used=used, total=total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.high_slot


class MediumSlotRestriction(BaseRestriction):
    """Quantity of medium-slot items should not exceed limit.

    Details:
        Container with medium slot items is used for validation.
        Only items which are positioned outside of slots provided by ship raise
            error.
    """

    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        used, total = self._fit.stats.med_slots
        if used > total:
            tainted_items = {}
            for item in self._fit.modules.med[total:]:
                tainted_items[item] = SlotQuantityErrorData(
                    used=used, total=total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.medium_slot


class LowSlotRestriction(BaseRestriction):
    """Quantity of low-slot items should not exceed limit.

    Details:
        Container with low slot items is used for validation.
        Only items which are positioned outside of slots provided by ship raise
            error.
    """

    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        used, total = self._fit.stats.low_slots
        if used > total:
            tainted_items = {}
            for item in self._fit.modules.low[total:]:
                tainted_items[item] = SlotQuantityErrorData(
                    used=used, total=total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.low_slot


class RigSlotRestriction(UnorderedSlotRestriction):
    """Quantity of rig items should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    _stat_name = 'rig_slots'

    @property
    def type(self):
        return Restriction.rig_slot


class SubsystemSlotRestriction(UnorderedSlotRestriction):
    """Quantity of subsystem items should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    _stat_name = 'subsystem_slots'

    @property
    def type(self):
        return Restriction.subsystem_slot


class TurretSlotRestriction(UnorderedSlotRestriction):
    """Quantity of turrets should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    _stat_name = 'turret_slots'

    @property
    def type(self):
        return Restriction.turret_slot


class LauncherSlotRestriction(UnorderedSlotRestriction):
    """Quantity of launchers should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    _stat_name = 'launcher_slots'

    @property
    def type(self):
        return Restriction.launcher_slot


class LaunchedDroneRestriction(UnorderedSlotRestriction):
    """Quantity of launched drones should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    _stat_name = 'launched_drones'

    @property
    def type(self):
        return Restriction.launched_drone


class FighterSquadRestriction(UnorderedSlotRestriction):
    """Quantity of fighter squads should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    _stat_name = 'fighter_squads'

    @property
    def type(self):
        return Restriction.fighter_squad


class FighterSquadSupportRestriction(UnorderedSlotRestriction):
    """Quantity of support fighter squads should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    _stat_name = 'fighter_squads_support'

    @property
    def type(self):
        return Restriction.fighter_squad_support


class FighterSquadLightRestriction(UnorderedSlotRestriction):
    """Quantity of light fighter squads should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    _stat_name = 'fighter_squads_light'

    @property
    def type(self):
        return Restriction.fighter_squad_light


class FighterSquadHeavyRestriction(UnorderedSlotRestriction):
    """Quantity of heavy fighter squads should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    _stat_name = 'fighter_squads_heavy'

    @property
    def type(self):
        return Restriction.fighter_squad_heavy
