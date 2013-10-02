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

from eos.const.eos import Restriction, Slot
from eos.const.eve import Attribute, Group, Category
from eos.fit.holder.item import *
from eos.fit.restrictionTracker.exception import RegisterValidationError
from .abc import RestrictionRegister


HolderClassErrorData = namedtuple('HolderClassErrorData', ('holderClass', 'expectedClasses'))


classValidators = {Booster: lambda item: (item.categoryId == Category.implant and
                                          Attribute.boosterness in item.attributes),
                   Character: lambda item: item.groupId == Group.character,
                   Charge: lambda item: item.categoryId == Category.charge,
                   Drone: lambda item: item.categoryId == Category.drone,
                   EffectBeacon: lambda item: item.groupId == Group.effectBeacon,
                   Implant: lambda item: (item.categoryId == Category.implant and
                                          Attribute.implantness in item.attributes),
                   Module: lambda item: (item.categoryId == Category.module and
                                         (Slot.moduleHigh in item.slots or
                                          Slot.moduleMed in item.slots or
                                          Slot.moduleLow in item.slots)),
                   Rig: lambda item: (item.categoryId == Category.module and
                                      Slot.rig in item.slots),
                   Ship: lambda item: item.categoryId == Category.ship,
                   Skill: lambda item: item.categoryId == Category.skill,
                   Subsystem: lambda item: (item.categoryId == Category.subsystem and
                                            Slot.subsystem in item.slots)}


class HolderClassRegister(RestrictionRegister):
    """
    Implements restriction:
    Check that item is wrapped by corresponding holder class
    instance (e.g. that cybernetic subprocessor is represented
    by Implant class instance).

    Details:
    To determine class matching to item, attributes only of
    original item are used.
    """

    def __init__(self):
        # Container for tracked holders
        self.__holders = set()

    def registerHolder(self, holder):
        # Yes, we're tracking all of them
        self.__holders.add(holder)

    def unregisterHolder(self, holder):
        self.__holders.discard(holder)

    def validate(self):
        taintedHolders = {}
        for holder in self.__holders:
            # Get validator function for class of passed holder.
            # If it is not found or fails, seek for 'right'
            # holder types for the item
            try:
                validatorFunc = classValidators[type(holder)]
            except KeyError:
                taintedHolders[holder] = self.__getErrorData(holder)
            else:
                if validatorFunc(holder.item) is not True:
                    taintedHolders[holder] = self.__getErrorData(holder)
        if taintedHolders:
            raise RegisterValidationError(taintedHolders)


    def __getErrorData(self, holder):
        expectedClasses = []
        # Cycle through our class validator dictionary and
        # seek for acceptable classes for this item
        for holderClass, validatorFunc in classValidators.items():
            if validatorFunc(holder.item) is True:
                expectedClasses.append(holderClass)
        expectedClasses = tuple(expectedClasses)
        errorData = HolderClassErrorData(holderClass=type(holder),
                                         expectedClasses=expectedClasses)
        return errorData

    @property
    def restrictionType(self):
        return Restriction.holderClass
