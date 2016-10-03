# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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
# ===============================================================================


from collections import namedtuple

from eos.const.eos import Domain, Restriction
from eos.const.eve import Type, Attribute
from eos.fit.restriction_tracker.exception import RegisterValidationError
from .abc import RestrictionRegister


# Holders of volume bigger than this
# are considered as capital
MAX_SUBCAP_VOLUME = 500


CapitalItemErrorData = namedtuple('CapitalItemErrorData', ('holder_volume', 'max_allowed_volume'))


class CapitalItemRegister(RestrictionRegister):
    """
    Implements restriction:
    To fit holders with volume bigger than 500, ship must
    have Capital Ships skill requirement.

    Details:
    Only holders belonging to ship are tracked.
    For validation, unmodified volume value is taken. If
    volume attribute is absent, holder is not validated.
    """

    def __init__(self, fit):
        self._fit = fit
        # Container for all tracked holders
        self.__capital_holders = set()

    def register_holder(self, holder):
        # Ignore holders which do not belong to ship
        if holder._domain != Domain.ship:
            return
        # Ignore holders with no volume attribute and holders with
        # volume which satisfies us regardless of ship type
        try:
            holder_volume = holder.item.attributes[Attribute.volume]
        except KeyError:
            return
        if holder_volume <= MAX_SUBCAP_VOLUME:
            return
        self.__capital_holders.add(holder)

    def unregister_holder(self, holder):
        self.__capital_holders.discard(holder)

    def validate(self):
        # Skip validation only if ship has capital
        # ships requirement, else carry on
        ship_holder = self._fit.ship
        try:
            ship_item = ship_holder.item
        except AttributeError:
            pass
        else:
            if Type.capital_ships in ship_item.required_skills:
                return
        # If we got here, then we're dealing with non-capital
        # ship, and all registered holders are tainted
        if self.__capital_holders:
            tainted_holders = {}
            for holder in self.__capital_holders:
                holder_volume = holder.item.attributes[Attribute.volume]
                tainted_holders[holder] = CapitalItemErrorData(
                    holder_volume=holder_volume,
                    max_allowed_volume=MAX_SUBCAP_VOLUME
                )
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return Restriction.capital_item
