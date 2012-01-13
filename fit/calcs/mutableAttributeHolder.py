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

from abc import ABCMeta
from abc import abstractproperty
from collections import Mapping

from eos import const
from .affector import Affector
from .condition import ConditionEval


class MutableAttributeHolder:
    """
    Base attribute holder class inherited by all classes that need to keep track of modified attributes.
    This class holds a MutableAttributeMap to keep track of changes.
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def location(self):
        ...

    def __init__(self, invType):
        """ Constructor. Accepts invType"""

        # Which fit this holder is bound to
        self.fit = None

        # Which invType this holder wraps
        self.invType = invType

        # Special dictionary subclass that holds modified attributes and data related to their calculation
        self.attributes = MutableAttributeMap(self)

class MutableAttributeMap(Mapping):
    """MutableAttributeMap class."""

    def __init__(self, holder):
        self.__holder = holder
        # Actual container of calculated attributes
        # Format: attributeID: value
        self.__modifiedAttributes = {}

    def __getitem__(self, key):
        try:
            val = self.__modifiedAttributes[key]
        except KeyError:
            val = self.__modifiedAttributes[key] = self.__calculate(key)
            self.__damageDependantsOnKey(key)
        return val

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        result = key in self.__modifiedAttributes or key in self.__holder.invType.attributes
        return result

    def __iter__(self):
        for k in self.keys():
            yield k

    def keys(self):
        keys = set(self.__modifiedAttributes.keys()).intersection(self.__holder.invType.attributes.keys())
        return keys

    def __delitem__(self, key):
        if key in self.__modifiedAttributes:
            # Clear the value in our calculated attributes dict
            del self.__modifiedAttributes[key]
            # And make sure all other attributes relying on it
            # are cleared too
            self.__damageDependantsOnKey(key)

    def __damageDependantsOnKey(self, key):
        """Clear calculated values of attributes relying on value of current attribute"""
        sourceHolder = self.__holder
        # Go through all infos of current holder
        for info in sourceHolder.invType.getInfos():
            # Skip the ones which do not use attribute being damaged as source
            if info.sourceValue != key or info.sourceType != const.srcAttr:
                continue
            # Gp through all holders targeted by info
            affector = Affector(sourceHolder=sourceHolder, info=info)
            for targetHolder in sourceHolder.fit._getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[info.targetAttributeId]

    def _damageDependantsOnHolder(self):
        sourceHolder = self.__holder
        # Go through all infos of current holder
        for info in sourceHolder.invType.getInfos():
            # Gp through all holders targeted by info
            affector = Affector(sourceHolder=sourceHolder, info=info)
            for targetHolder in sourceHolder.fit._getAffectees(affector):
                # And remove target attribute
                del targetHolder.attributes[info.targetAttributeId]

    def __calculate(self, attrId):
        """
        Run calculations to find the actual value of attribute with ID equal to attrID.
        All other attribute values are assumed to be final.
        This is obviously not always the case,
        if any of the dependencies of this calculation change, this attribute will get invalidated and thus recalculated when its next needed
        """
        holder =  self.__holder
        value = holder.invType.attributes.get(attrId)

        try:
            attributeType = holder.invType.attributeTypes[attrId]
            stackable = attributeType.stackable
            penalized = {}



            for affector in holder.fit._getAffectors(holder):
                sourceHolder, info = affector
                operation = info.operation
                modValue = sourceHolder.attributes[info.sourceValue]

                #Stacking penaltied modifiers get special handling
                if not stackable and sourceHolder.invType.categoryId not in const.penaltyImmuneCats \
                   and operation in (const.optrPreMul, const.optrPostMul, const.optrPostPercent, const.optrPreDiv, const.optrPostDiv):

                    # Compute actual modifier
                    if operation == const.optrPostPercent:
                        modValue = modValue / 100
                    elif operation in (const.optrPreMul, const.optrPostMul):
                        modValue = modValue - 1
                    else:
                        modValue = (1 / modValue) - 1

                    subDict = penalized.get(modValue > 1)
                    if subDict is None:
                        penalized[modValue > 1] = subDict = {}

                    valueSet = subDict.get(operation)
                    if valueSet is None:
                        subDict[operation] = valueSet = []

                    valueSet.append(modValue)

                elif operation in (const.optrPreAssignment, const.optrPostAssignment):
                    value = modValue
                elif operation in (const.optrPreMul, const.optrPostMul):
                    value = value * modValue
                elif operation == const.optrPostPercent:
                    value = value * (1 + modValue / 100)
                elif operation in (const.optrPreDiv, const.optrPostDiv):
                    value = value / modValue
                elif operation == const.optrModAdd:
                    value = value + modValue
                elif operation == const.optrModSub:
                    value = value - modValue

            for k in penalized:
                subDict = penalized[k]
                for operation in subDict:
                    values = sorted(subDict[operation])
                    for i in range(len(values)):
                        value *= 1 + values[i] * const.penaltyBase ** (i ** 2)

            return value
        except KeyError:
            return value
