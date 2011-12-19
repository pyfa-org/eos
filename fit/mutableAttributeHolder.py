#===============================================================================
# Copyright (C) 2011 Diego Duclos
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

import collections

from eos import const
from eos.fit.condition import ConditionEval

from abc import ABCMeta
from abc import abstractproperty

RegistrationInfo = collections.namedtuple("RegistrationInfo", ("sourceHolder", "info"))

class MutableAttributeHolder:
    """
    Base attribute holder class inherited by all classes that need to keep track of modified attributes.
    This class holds a MutableAttributeMap to keep track of changes.
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def location(self):
        ...

    @abstractproperty
    def specific(self):
        ...

    def __init__(self, type):
        """
        Constructor. Accepts a Type
        """
        self.fit = None
        """
        Which fit this holder is bound to
        """
        self.type = type
        """
        Which type this holder wraps
        """

        self.attributes = MutableAttributeMap(self)
        """
        Special dictionary subclass that holds modified attributes and data related to their calculation
        """

    def _register(self):
        """Registers this holder, called when a holder is added to a fit"""
        self.attributes._registerAll()

    def _unregister(self):
        """Unregisters this holder, called when a holder is removed from a fit"""
        self.attributes._unregisterAll()

class MutableAttributeMap(collections.Mapping):
    """
    MutableAttributeMap class, this class is what actually keeps track of modified attribute values and who modified what so undo can work as expected.
    """

    def __init__(self, holder):
        self.__holder = holder
        self.__modifiedAttributes = {}

        # The attribute register keeps track of what effects apply to what attribute
        self.__attributeRegister = {}

    def __getitem__(self, key):
        val = self.__modifiedAttributes.get(key)
        if val is None:
            self.__modifiedAttributes[key] = val = self.__calculate(key)

        return val

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        return key in self.__modifiedAttributes or key in self.__holder.type.attributes

    def __iter__(self):
        for k in self.keys():
            yield k

    def keys(self):
        return set(self.__modifiedAttributes.keys()).intersection(self.__holder.type.attributes.keys())

    def _registerAll(self):
        """
        Populate the attributeRegister completely with what affects us
        and also add ourselves onto anything we affect.

        This is called for newly added holders to populate them entirely
        """
        # Populate our affectors
        holder = self.__holder
        fit = holder.fit

        for registrationInfo in fit._getAffectors(holder):
            self._registerOne(registrationInfo)


        for info in holder.type.getInfos():
            registrationInfo = (holder, info)
            for affectee in fit._getAffectees(registrationInfo):
                affectee.attributes._registerOne(registrationInfo)


    def _registerOne(self, registrationInfo):
        # Add the registrationInfo affecting us into our register
        _, info = registrationInfo
        s = self.__attributeRegister.get(info.targetAttributeId)
        if s is None:
            s = self.__attributeRegister[info.targetAttributeId] = set()

        s.add(registrationInfo)

        # Delete the calculated value for the affected attribute if there is any
        del self[info.targetAttributeId]


    def __delitem__(self, attrId):
        if attrId in self.__modifiedAttributes:
            # Clear the value in our calculated value dict
            del self.__modifiedAttributes[attrId]

            # If we have any dependants, their calculated value needs to be cleared as well
            # Only specific holders can have dependants
            holder = self.__holder
            if holder.specific:
                for depHolder, depInfo in holder.fit._getDependants(holder.location, attrId):
                    del depHolder.attributes[depInfo.sourceAttributeId]

            fit = holder.fit
            # We also need to clear things we affect
            for info in filter(lambda i: i.sourceAttributeId == attrId, holder.type.getInfos()):
                for affectee in fit._getAffectees((holder, info)):
                    del affectee.attributes[info.targetAttributeId]

    def _unregisterAll(self):
        fit = self.__holder.fit
        for info in self.__holder.type.getInfos():
            registrationInfo = (self, info)
            for affectee in fit._getAffectees(registrationInfo):
                affectee.attributes._unregisterOne(registrationInfo)

        del self.__attributeRegister[:]
        del self[:]

    def _unregisterOne(self, registrationInfo):
        _, info = registrationInfo
        self.__attributeRegister[info.targetAttributeId].remove(registrationInfo)
        del self.__modifiedAttributes[info.targetAttributeId]

    def __calculate(self, attrId):
        """
        Run calculations to find the actual value of attribute with ID equal to attrID.
        All other attribute values are assumed to be final.
        This is obviously not always the case,
        if any of the dependencies of this calculation change, this attribute will get invalidated and thus recalculated when its next needed
        """

        # Code note: This method will store intermediate values in the calculated values already
        # Why ? Because some infos affecting an attribute also have a condition on that same attribute
        base = self.__holder.type.attributes.get(attrId)
        keyFunc = lambda registrationInfo: registrationInfo[1].operation

        try:
            attributeType = self.__holder.type.attributeTypes[attrId]
            stackable = attributeType.stackable

            register = sorted(self.__attributeRegister[attrId], key=keyFunc)

            modifiedAttrs = self.__modifiedAttributes
            result = modifiedAttrs[attrId] = base

            penalized = {}



            for registrationInfo in register:
                sourceHolder, info = registrationInfo
                if info.conditions is None or ConditionEval(info).isValid(sourceHolder):
                    operation = info.operation
                    value = sourceHolder.attributes[info.sourceAttributeId]

                    #Stacking penaltied modifiers get special handling
                    if not stackable and sourceHolder.type.categoryId not in const.penaltyImmuneCats \
                       and operation in (const.optrPreMul, const.optrPostMul, const.optrPostPercent, const.optrPreDiv, const.optrPostDiv):

                        # Compute actual modifier
                        if operation == const.optrPostPercent:
                            value = value / 100
                        elif operation in (const.optrPreMul, const.optrPostMul):
                            value = value - 1
                        else:
                            value = (1 / value) - 1

                        subDict = penalized.get(value > 1)
                        if subDict is None:
                            penalized[value > 1] = subDict = {}

                        valueSet = subDict.get(operation)
                        if valueSet is None:
                            subDict[operation] = valueSet = []

                        valueSet.append(value)

                    elif operation in (const.optrPreAssignment, const.optrPostAssignment):
                        result = modifiedAttrs[attrId] = value
                    elif operation in (const.optrPreMul, const.optrPostMul):
                        result = modifiedAttrs[attrId] = result * value
                    elif operation == const.optrPostPercent:
                        result = modifiedAttrs[attrId] = result * (1 + value / 100)
                    elif operation in (const.optrPreDiv, const.optrPostDiv):
                        result = modifiedAttrs[attrId] = result / value
                    elif operation == const.optrModAdd:
                        result = modifiedAttrs[attrId] = result + value
                    elif operation == const.optrModSub:
                        result = modifiedAttrs[attrId] = result - value

            for k in penalized:
                subDict = penalized[k]
                for operation in subDict:
                    values = sorted(subDict[operation])
                    for i in range(len(values)):
                        result *= 1 + values[i] * const.penaltyBase ** (i ** 2)

            return result
        except KeyError:
            return base