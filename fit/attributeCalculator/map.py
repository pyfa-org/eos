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


from math import exp

from eos.const import Operator, SourceType
from eos.eve.const import Category, Attribute


# Stacking penalty base constant, used in attribute calculations
penaltyBase = 1 / exp((1 / 2.67) ** 2)


class MutableAttributeMap:
    """
    Calculate, store and provide access to modified attribute values.

    Positional arguments:
    holder -- holder, to which this map is assigned
    """

    def __init__(self, holder):
        # Reference to holder for internal needs
        self.__holder = holder
        # Actual container of calculated attributes
        # Format: {attribute ID: value}
        self.__modifiedAttributes = {}

    def __getitem__(self, attrId):
        # If value is stored, it's considered valid
        try:
            val = self.__modifiedAttributes[attrId]
        # Else, we have to run full calculation process
        except KeyError:
            val = self.__modifiedAttributes[attrId] = self.__calculate(attrId)
            self.__holder.fit.linkTracker._clearHolderAttributeDependents(self.__holder, attrId)
        return val

    def __len__(self):
        return len(self.keys())

    def __contains__(self, attrId):
        # Seek for attribute in both modified attribute container
        # and original item attributes
        result = attrId in self.__modifiedAttributes or attrId in self.__holder.item.attributes
        return result

    def __iter__(self):
        for k in self.keys():
            yield k

    def __delitem__(self, attrId):
        # Clear the value in our calculated attributes dictionary
        try:
            del self.__modifiedAttributes[attrId]
        # Do nothing if it wasn't calculated
        except KeyError:
            pass
        # And make sure all other attributes relying on it
        # are cleared too
        else:
            self.__holder.fit.linkTracker._clearHolderAttributeDependents(self.__holder, attrId)

    def __setitem__(self, attrId, value):
        # This method is added to allow direct skill level changes
        if attrId != Attribute.skillLevel:
            raise RuntimeError("changing any attribute besides skillLevel is prohibited")
        # Write value and clear all attributes relying on it
        self.__modifiedAttributes[attrId] = value
        self.__holder.fit.linkTracker._clearHolderAttributeDependents(self.__holder, attrId)

    def keys(self):
        keys = set(self.__modifiedAttributes.keys()).intersection(self.__holder.item.attributes.keys())
        return keys

    def clear(self):
        self.__modifiedAttributes.clear()

    def __calculate(self, attrId):
        """
        Run calculations to find the actual value of attribute.

        Positional arguments:
        attrId -- ID of attribute to be calculated

        Return value:
        Calculated attribute value
        """
        # Base attribute value which we'll use for modification
        result = self.__holder.item.attributes.get(attrId)
        # Attribute metadata
        attrMeta = self.__holder.fit._attrMetaGetter(attrId)
        # Container for non-penalized modifiers
        # Format: {operator: {values}}
        normalMods = {}
        # Container for penalized modifiers
        # Format: {operator: {values}}
        penalizedMods = {}
        # Now, go through all affectors affecting our holder
        for affector in self.__holder.fit.linkTracker.getAffectors(self.__holder):
            sourceHolder, info = affector
            # Skip affectors who do not target attribute being calculated
            if info.targetAttributeId != attrId:
                continue
            operator = info.operator
            # If source value is attribute reference
            if info.sourceType == SourceType.attribute:
                # Get its value
                modValue = sourceHolder.attributes[info.sourceValue]
                # And decide if it should be stacking penalized or not, based on stackable property,
                # source item category and operator
                penaltyImmuneCategories = {Category.ship, Category.charge, Category.skill, Category.implant, Category.subsystem}
                penalizableOperators = {Operator.preMul, Operator.postMul, Operator.postPercent, Operator.preDiv, Operator.postDiv}
                penalize = (not attrMeta.stackable and sourceHolder.item.categoryId not in penaltyImmuneCategories
                            and operator in penalizableOperators)
            # For value modifications, just use stored in info value and avoid its penalization
            else:
                modValue = info.sourceValue
                penalize = False
            # Normalize addition/subtraction, so it's always
            # acts as addition
            if operator == Operator.modSub:
                modValue = -modValue
            # Normalize multiplicative modifiers, converting them into form of
            # multiplier
            elif operator in {Operator.preDiv, Operator.postDiv}:
                modValue = 1 / modValue
            elif operator == Operator.postPercent:
                modValue = modValue / 100 + 1
            # Add value to appropriate dictionary
            if penalize is True:
                try:
                    modList = penalizedMods[operator]
                except KeyError:
                    modList = penalizedMods[operator] = []
            else:
                try:
                    modList = normalMods[operator]
                except KeyError:
                    modList = normalMods[operator] = []
            modList.append(modValue)
        # When data gathering was finished, process penalized modifiers
        # They are penalized on per-operator basis
        for operator, modList in penalizedMods.items():
            penalizedValue = self.__penalizeValues(modList)
            try:
                modList = normalMods[operator]
            except KeyError:
                modList = normalMods[operator] = []
            modList.append(penalizedValue)
        # Calculate result of normal dictionary, according to operator order
        for operator in sorted(normalMods):
            modList = normalMods[operator]
            # Pick best modifier for assignments, based on highIsGood value
            if operator in (Operator.preAssignment, Operator.postAssignment):
                result = max(modList) if attrMeta.highIsGood is True else min(modList)
            elif operator in (Operator.modAdd, Operator.modSub):
                for modVal in modList:
                    result += modVal
            elif operator in (Operator.preMul, Operator.preDiv, Operator.postMul,
                              Operator.postDiv, Operator.postPercent):
                for modVal in modList:
                    result *= modVal
        return result

    def __penalizeValues(self, modList):
        """
        Calculate aggregated factor of passed factors, taking into
        consideration stacking penalty.

        Positional argument:
        modList -- list of factors

        Return value:
        Final aggregated factor of passed modList
        """
        # Gather positive modifiers into one chain, negative
        # into another
        chainPositive = []
        chainNegative = []
        for modVal in modList:
            # Transform value into form of multiplier - 1 for ease of
            # stacking chain calculation
            modVal -= 1
            if modVal >= 0:
                chainPositive.append(modVal)
            else:
                chainNegative.append(modVal)
        # Strongest modifiers always go first
        chainPositive.sort(reverse=True)
        chainNegative.sort()
        # Base final multiplier on 1
        listResult = 1
        for chain in (chainPositive, chainNegative):
            # Same for intermediate per-chain result
            chainResult = 1
            for position, modifier in enumerate(chain):
                # Ignore 12th modifier and further as non-significant
                if position > 10:
                    break
                # Apply stacking penalty based on modifier position
                chainResult *= 1 + modifier * penaltyBase ** (position ** 2)
            listResult *= chainResult
        return listResult
