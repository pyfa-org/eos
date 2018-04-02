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
from eos.restriction.exception import RestrictionValidationError
from eos.restriction.restriction.base import BaseRestriction
from .error_data import SlotQuantityErrorData


class OrderedSlotRestriction(BaseRestriction, metaclass=ABCMeta):

    def __init__(self, fit):
        self._fit = fit

    @property
    @abstractmethod
    def _slot_stats(self):
        ...

    @property
    @abstractmethod
    def _container(self):
        ...

    def validate(self):
        used, total = self._slot_stats
        if used > total:
            tainted_items = {}
            for item in self._container[total:]:
                tainted_items[item] = SlotQuantityErrorData(
                    used=used, total=total)
            raise RestrictionValidationError(tainted_items)


class HighSlotRestriction(OrderedSlotRestriction):
    """Quantity of high-slot items should not exceed limit.

    Details:
        Items which are not loaded are considered as occupying slot.
        Only items which are positioned outside of slots provided by ship raise
            error.
    """

    type = Restriction.high_slot

    @property
    def _slot_stats(self):
        return self._fit.stats.high_slots

    @property
    def _container(self):
        return self._fit.modules.high


class MidSlotRestriction(OrderedSlotRestriction):
    """Quantity of mid-slot items should not exceed limit.

    Details:
        Items which are not loaded are considered as occupying slot.
        Only items which are positioned outside of slots provided by ship raise
            error.
    """

    type = Restriction.mid_slot

    @property
    def _slot_stats(self):
        return self._fit.stats.mid_slots

    @property
    def _container(self):
        return self._fit.modules.mid


class LowSlotRestriction(OrderedSlotRestriction):
    """Quantity of low-slot items should not exceed limit.

    Details:
        Items which are not loaded are considered as occupying slot.
        Only items which are positioned outside of slots provided by ship raise
            error.
    """

    type = Restriction.low_slot

    @property
    def _slot_stats(self):
        return self._fit.stats.low_slots

    @property
    def _container(self):
        return self._fit.modules.low
