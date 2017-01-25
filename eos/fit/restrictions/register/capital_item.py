# ===============================================================================
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
# ===============================================================================


from collections import namedtuple

from eos.const.eos import Restriction, ModifierDomain
from eos.const.eve import Attribute
from .base import BaseRestrictionRegister
from ..exception import RegisterValidationError


# Holders of volume bigger than this are considered as capital
MAX_SUBCAP_VOLUME = 3500


CapitalItemErrorData = namedtuple('CapitalItemErrorData', ('holder_volume', 'max_subcap_volume'))


class CapitalItemRestrictionRegister(BaseRestrictionRegister):
    """
    Implements restriction:
    To fit holders with volume bigger than 4000, ship must
    have IsCapitalShip attribute set to 1.

    Details:
    Only holders belonging to ship are tracked.
    For validation, EVE type volume value is taken. If
    volume attribute is absent, holder is not restricted.
    """

    def __init__(self, fit):
        self._fit = fit
        # Container for all tracked holders
        self.__capital_holders = set()

    def register_item(self, holder):
        # Ignore holders which do not belong to ship
        if holder._domain != ModifierDomain.ship:
            return
        # Ignore holders with no volume attribute and holders with
        # volume which satisfies us regardless of ship type
        try:
            holder_volume = holder._eve_type.attributes[Attribute.volume]
        except KeyError:
            return
        if holder_volume <= MAX_SUBCAP_VOLUME:
            return
        self.__capital_holders.add(holder)

    def unregister_item(self, holder):
        self.__capital_holders.discard(holder)

    def validate(self):
        # Skip validation only if ship has special
        # special attribute set to 1
        ship_holder = self._fit.ship
        try:
            ship_eve_type = ship_holder._eve_type
        except AttributeError:
            pass
        else:
            if ship_eve_type.attributes.get(Attribute.is_capital_size):
                return
        # If we got here, then we're dealing with non-capital
        # ship, and all registered holders are tainted
        if self.__capital_holders:
            tainted_holders = {}
            for holder in self.__capital_holders:
                holder_volume = holder._eve_type.attributes[Attribute.volume]
                tainted_holders[holder] = CapitalItemErrorData(
                    holder_volume=holder_volume,
                    max_subcap_volume=MAX_SUBCAP_VOLUME
                )
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return Restriction.capital_item
