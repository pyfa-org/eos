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


from collections import namedtuple

from eos.const.eos import Restriction
from .base import BaseRestriction
from ..exception import RestrictionValidationError


LoadedItemErrorData = namedtuple('LoadedItemErrorData', ())


class LoadedItemRestriction(BaseRestriction):
    """Check that all items on fit are loaded.

    Details:
        Autocharges are not restricted.
    """

    type = Restriction.loaded_item

    def __init__(self, fit):
        self.__fit = fit

    def validate(self):
        tainted_items = {}
        # User has no direct control over autoitems, so skip them
        for item in self.__fit._item_iter(skip_autoitems=True):
            if not item._is_loaded:
                tainted_items[item] = LoadedItemErrorData()
        if tainted_items:
            raise RestrictionValidationError(tainted_items)
