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

from eos.const.eos import Restriction
from eos.const.eve import Attribute
from eos.fit.restriction_tracker.exception import RegisterValidationError
from .abc import RestrictionRegister


RigSizeErrorData = namedtuple('RigSizeErrorData', ('holder_size', 'allowed_size'))


class RigSizeRegister(RestrictionRegister):
    """
    Implements restriction:
    If ship requires rigs of certain size, rigs of other size cannot
    be used.

    Details:
    For validation, original value of rig_size attribute is taken.
    """

    def __init__(self, fit):
        self._fit = fit
        # Container for holders which have rig size restriction
        self.__restricted_holders = set()

    def register_holder(self, holder):
        # Register only holders which have attribute,
        # which restricts rig size
        if Attribute.rig_size not in holder.item.attributes:
            return
        self.__restricted_holders.add(holder)

    def unregister_holder(self, holder):
        self.__restricted_holders.discard(holder)

    def validate(self):
        ship_holder = self._fit.ship
        # Do not apply restriction when fit doesn't
        # have ship
        try:
            ship_item = ship_holder.item
        except AttributeError:
            return
        # If ship doesn't have restriction attribute,
        # allow all rigs - skip validation
        try:
            allowed_rig_size = ship_item.attributes[Attribute.rig_size]
        except KeyError:
            return
        tainted_holders = {}
        for holder in self.__restricted_holders:
            holder_rig_size = holder.item.attributes[Attribute.rig_size]
            # If rig size specification on holder and ship differs,
            # then holder is tainted
            if holder_rig_size != allowed_rig_size:
                tainted_holders[holder] = RigSizeErrorData(
                    holder_size=holder_rig_size,
                    allowed_size=allowed_rig_size
                )
        if tainted_holders:
            raise RegisterValidationError(tainted_holders)

    @property
    def restriction_type(self):
        return Restriction.rig_size
