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

from eos.const.eos import Restriction
from eos.fit.restriction.exception import RestrictionValidationError
from eos.fit.restriction.restriction.base import BaseRestriction
from .error_data import SlotQuantityErrorData


class StatsAssistedSlotRestriction(BaseRestriction, metaclass=ABCMeta):

    def __init__(self, fit):
        self._fit = fit

    @property
    @abstractmethod
    def _slot_stats(self):
        ...

    def validate(self):
        stats = self._slot_stats
        if stats.used > stats.total:
            tainted_items = {}
            for item in stats._users:
                tainted_items[item] = SlotQuantityErrorData(
                    used=stats.used, total=stats.total)
            raise RestrictionValidationError(tainted_items)


class TurretSlotRestriction(StatsAssistedSlotRestriction):
    """Quantity of turrets should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    type = Restriction.turret_slot

    @property
    def _slot_stats(self):
        return self._fit.stats.turret_slots


class LauncherSlotRestriction(StatsAssistedSlotRestriction):
    """Quantity of launchers should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    type = Restriction.launcher_slot

    @property
    def _slot_stats(self):
        return self._fit.stats.launcher_slots


class LaunchedDroneRestriction(StatsAssistedSlotRestriction):
    """Quantity of launched drones should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    type = Restriction.launched_drone

    @property
    def _slot_stats(self):
        return self._fit.stats.launched_drones


class FighterSquadSupportRestriction(StatsAssistedSlotRestriction):
    """Quantity of support fighter squads should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    type = Restriction.fighter_squad_support

    @property
    def _slot_stats(self):
        return self._fit.stats.fighter_squads_support


class FighterSquadLightRestriction(StatsAssistedSlotRestriction):
    """Quantity of light fighter squads should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    type = Restriction.fighter_squad_light

    @property
    def _slot_stats(self):
        return self._fit.stats.fighter_squads_light


class FighterSquadHeavyRestriction(StatsAssistedSlotRestriction):
    """Quantity of heavy fighter squads should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    type = Restriction.fighter_squad_heavy

    @property
    def _slot_stats(self):
        return self._fit.stats.fighter_squads_heavy
