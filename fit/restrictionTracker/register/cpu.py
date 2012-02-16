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


from eos.eve.const import Attribute
from eos.fit.attributeCalculator.exception import NoAttributeException
from eos.fit.restrictionTracker.exception import CpuException
from eos.fit.restrictionTracker.registerAbc import RestrictionRegister


class CpuRegister(RestrictionRegister):
    def __init__(self, fit):
        self.__fit = fit
        self.__cpuUsers = set()

    def registerHolder(self, holder):
        if not Attribute.cpu in holder.item.attributes:
            return
        self.__cpuUsers.add(holder)
        self.validate()

    def unregisterHolder(self, holder):
        self.__cpuUsers.discard(holder)

    def validate(self):
        cpuUse = 0
        for cpuUser in self.__cpuUsers:
            cpuUse += cpuUser.attributes[Attribute.cpu]
        shipHolder = self.__fit.ship
        try:
            shipHolderAttribs = shipHolder.attributes
        except AttributeError:
            cpuOutput = 0
        else:
            try:
                cpuOutput = shipHolderAttribs[Attribute.cpuOutput]
            except NoAttributeException:
                cpuOutput = 0
        if cpuUse > cpuOutput:
            taintedHolders = set()
            taintedHolders.update(self.__cpuUsers)
            raise CpuException(taintedHolders)
