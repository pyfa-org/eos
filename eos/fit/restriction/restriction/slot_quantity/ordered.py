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


class HighSlotRestriction(BaseRestriction):
    """Quantity of high-slot items should not exceed limit.

    Details:
        Items which are not loaded are considered as occupying slot.
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
        Items which are not loaded are considered as occupying slot.
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
        Items which are not loaded are considered as occupying slot.
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
