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


from eos.const.eos import Restriction
from eos.fit.restriction.exception import RestrictionValidationError
from eos.fit.restriction.restriction.base import BaseRestriction
from .error_data import SlotQuantityErrorData


class TurretSlotRestriction(BaseRestriction):
    """Quantity of turrets should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        stats = self._fit.stats.turret_slots
        if stats.used > stats.total:
            tainted_items = {}
            for item in stats._users:
                tainted_items[item] = SlotQuantityErrorData(
                    used=stats.used, total=stats.total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.turret_slot


class LauncherSlotRestriction(BaseRestriction):
    """Quantity of launchers should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        stats = self._fit.stats.launcher_slots
        if stats.used > stats.total:
            tainted_items = {}
            for item in stats._users:
                tainted_items[item] = SlotQuantityErrorData(
                    used=stats.used, total=stats.total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.launcher_slot


class LaunchedDroneRestriction(BaseRestriction):
    """Quantity of launched drones should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        stats = self._fit.stats.launched_drones
        if stats.used > stats.total:
            tainted_items = {}
            for item in stats._users:
                tainted_items[item] = SlotQuantityErrorData(
                    used=stats.used, total=stats.total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.launched_drone


class FighterSquadSupportRestriction(BaseRestriction):
    """Quantity of support fighter squads should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        stats = self._fit.stats.fighter_squads_support
        if stats.used > stats.total:
            tainted_items = {}
            for item in stats._users:
                tainted_items[item] = SlotQuantityErrorData(
                    used=stats.used, total=stats.total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.fighter_squad_support


class FighterSquadLightRestriction(BaseRestriction):
    """Quantity of light fighter squads should not exceed limit.

    Details:
        For validation, stats module data is used.
    """

    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        stats = self._fit.stats.fighter_squads_light
        if stats.used > stats.total:
            tainted_items = {}
            for item in stats._users:
                tainted_items[item] = SlotQuantityErrorData(
                    used=stats.used, total=stats.total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.fighter_squad_light


class FighterSquadHeavyRestriction(BaseRestriction):
    """Quantity of heavy fighter squads should not exceed limit.

    Details:
        For validation, stats module data is used.
    """
    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        stats = self._fit.stats.fighter_squads_heavy
        if stats.used > stats.total:
            tainted_items = {}
            for item in stats._users:
                tainted_items[item] = SlotQuantityErrorData(
                    used=stats.used, total=stats.total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.fighter_squad_heavy
