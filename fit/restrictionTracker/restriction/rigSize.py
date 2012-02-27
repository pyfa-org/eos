#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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
#===============================================================================


from collections import namedtuple

from eos.const import Restriction
from eos.eve.const import Attribute
from eos.fit.restrictionTracker.exception import RegisterValidationError
from eos.fit.restrictionTracker.register import RestrictionRegister


RigSizeErrorData = namedtuple("RigSizeErrorData", ("allowedSize", "holderSize"))


class RigSizeRegister(RestrictionRegister):
    """
    Implements restriction:
    If ship requires rigs of certain size, rigs of other size cannot
    be used.

    Details:
    If required rig size is None, holders which specify any rig size
    cannot be added to fit.
    For validation, original value of rigSize attribute is taken.
    """

    def __init__(self, tracker):
        self._tracker = tracker
        # Container for holders which have rig size restriction
        self.__restrictedHolders = set()

    def registerHolder(self, holder):
        # Register only holders which have attribute,
        # which restricts rig size, and have it as not None
        if holder.item.attributes.get(Attribute.rigSize) is None:
            return
        self.__restrictedHolders.add(holder)

    def unregisterHolder(self, holder):
        self.__restrictedHolders.discard(holder)

    def validate(self):
        shipHolder = self._tracker._fit.ship
        # Do not apply restriction when fit doesn't
        # have ship
        try:
            shipItem = shipHolder.item
        except AttributeError:
            return
        # If ship doesn't have restriction attribute or it's None,
        # allow all rigs - skip validation
        allowedRigSize = shipItem.attributes.get(Attribute.rigSize)
        if allowedRigSize is None:
            return
        taintedHolders = {}
        for holder in self.__restrictedHolders:
            holderRigSize = holder.item.attributes[Attribute.rigSize]
            # If rig size specification on holder and ship differs,
            # then holder is tainted
            if holderRigSize != allowedRigSize:
                taintedHolders[holder] = RigSizeErrorData(allowedSize=allowedRigSize,
                                                          holderSize=holderRigSize)
        if taintedHolders:
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return Restriction.rigSize
