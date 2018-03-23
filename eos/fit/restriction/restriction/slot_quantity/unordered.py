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


class RigSlotRestriction(BaseRestriction):
    """Quantity of rig items should not exceed limit.

    Details:
        Items which are not loaded are considered as occupying slot.
    """

    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        used, total = self._fit.stats.rig_slots
        if used > total:
            tainted_items = {}
            for item in self._fit.rigs:
                tainted_items[item] = SlotQuantityErrorData(
                    used=used, total=total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.rig_slot


class SubsystemSlotRestriction(BaseRestriction):
    """Quantity of subsystem items should not exceed limit.

    Details:
        Items which are not loaded are considered as occupying slot.
    """

    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        used, total = self._fit.stats.subsystem_slots
        if used > total:
            tainted_items = {}
            for item in self._fit.subsystems:
                tainted_items[item] = SlotQuantityErrorData(
                    used=used, total=total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.subsystem_slot


class FighterSquadRestriction(BaseRestriction):
    """Quantity of fighter squads should not exceed limit.

    Details:
        Items which are not loaded are considered as occupying slot.
    """

    def __init__(self, fit):
        self._fit = fit

    def validate(self):
        used, total = self._fit.stats.fighter_squads
        if used > total:
            tainted_items = {}
            for item in self._fit.fighters:
                tainted_items[item] = SlotQuantityErrorData(
                    used=used, total=total)
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.fighter_squad
