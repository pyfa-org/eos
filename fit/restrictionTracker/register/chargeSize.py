#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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

from eos.const.eos import Restriction
from eos.const.eve import Attribute
from eos.fit.restrictionTracker.exception import RegisterValidationError
from .abc import RestrictionRegister


ChargeSizeErrorData = namedtuple('ChargeSizeErrorData', ('holderSize', 'allowedSize'))


class ChargeSizeRegister(RestrictionRegister):
    """
    Implements restriction:
    If holder can fit charges and specifies size of charges it
    can fit, other sizes cannot be loaded into it.

    Details:
    If container specifies size and holder doesn't specify it,
    charge is not allowed to be loaded.
    If container does not specify size, charge of any size
    can be loaded.
    To determine allowed size and charge size, original item
    attributes are used.
    """

    def __init__(self):
        self.__restrictedContainers = set()

    def registerHolder(self, holder):
        # Ignore container holders without charge attribute
        if not hasattr(holder, 'charge'):
            return
        # And without size specification
        if Attribute.chargeSize not in holder.item.attributes:
            return
        self.__restrictedContainers.add(holder)

    def unregisterHolder(self, holder):
        self.__restrictedContainers.discard(holder)

    def validate(self):
        taintedHolders = {}
        # Go through containers with charges, and if their
        # sizes mismatch - taint charge holders
        for container in self.__restrictedContainers:
            charge = container.charge
            if charge is None:
                continue
            containerSize = container.item.attributes[Attribute.chargeSize]
            chargeSize = charge.item.attributes.get(Attribute.chargeSize)
            if containerSize != chargeSize:
                taintedHolders[charge] = ChargeSizeErrorData(holderSize=chargeSize,
                                                             allowedSize=containerSize)
        if taintedHolders:
            raise RegisterValidationError(taintedHolders)

    @property
    def restrictionType(self):
        return Restriction.chargeSize
