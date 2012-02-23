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
from eos.dataHandler.exception import AttributeFetchError
from eos.eve.const import Category, Attribute
from .exception import BaseValueError, EveAttributeError, OperatorError, SourceTypeError, SourceValueError


# Stacking penalty base constant, used in attribute calculations
penaltyBase = 1 / exp((1 / 2.67) ** 2)

# Items belonging to these categories never have
# their effects stacking penalized
penaltyImmuneCategories = (Category.ship, Category.charge, Category.skill, Category.implant, Category.subsystem)

# Tuple with penalizable operators
penalizableOperators = (Operator.preMul, Operator.postMul, Operator.postPercent, Operator.preDiv, Operator.postDiv)

# Map which helps to normalize modifiers
normalizationMap = {Operator.preAssignment: lambda val: val,
                    Operator.preMul: lambda val: val,
                    Operator.preDiv: lambda val: 1 / val,
                    Operator.modAdd: lambda val: val,
                    Operator.modSub: lambda val: -val,
                    Operator.postMul: lambda val: val,
                    Operator.postDiv: lambda val: 1 / val,
                    Operator.postPercent: lambda val: val / 100 + 1,
                    Operator.postAssignment: lambda val: val}

# List operator types, according to their already normalized values
assignments = (Operator.preAssignment, Operator.postAssignment)
additions = (Operator.modAdd, Operator.modSub)
multiplications = (Operator.preMul, Operator.preDiv, Operator.postMul, Operator.postDiv, Operator.postPercent)


class MutableAttributeMap:
    """
    Calculate, store and provide access to modified attribute values.

    Positional arguments:
    holder -- holder, to which this map is assigned
    """

    __slots__ = ("__holder", "__modifiedAttributes")

    def __init__(self, holder):
        # Reference to holder for internal needs
        self.__holder = holder
        # Actual container of calculated attributes
        # Format: {attribute ID: value}
        self.__modifiedAttributes = {}

    def __getitem__(self, attrId):
        # Special handling for skill level attribute
        if attrId == Attribute.skillLevel:
            # Attempt to return level attribute of holder
            try:
                val = self.__holder.level
            # Try regular way of getting attribute, if accessing
            # level attribute failed
            except AttributeError:
                pass
            else:
                return val
        # If carrier holder isn't assigned to any fit, then
        # we can use just item's original attributes
        if self.__holder.fit is None:
            val = self.__holder.item.attributes[attrId]
            return val
        # If value is stored, it's considered valid
        try:
            val = self.__modifiedAttributes[attrId]
        # Else, we have to run full calculation process
        except KeyError:
            try:
                val = self.__modifiedAttributes[attrId] = self.__calculate(attrId)
            except BaseValueError as e:
                msg = "unable to find base value for attribute {} on item {}".format(e.args[0], self.__holder.item.id)
                signature = (BaseValueError, self.__holder.item.id, e.args[0])
                self.__holder.fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
                raise KeyError(attrId) from e
            except EveAttributeError as e:
                msg = "unable to fetch metadata for attribute {}, requested for item {}".format(e.args[0], self.__holder.item.id)
                signature = (EveAttributeError, self.__holder.item.id, e.args[0])
                self.__holder.fit._eos._logger.error(msg, childName="attributeCalculator", signature=signature)
                raise KeyError(attrId) from e
            self.__holder.fit._linkTracker.clearHolderAttributeDependents(self.__holder, attrId)
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
            self.__holder.fit._linkTracker.clearHolderAttributeDependents(self.__holder, attrId)

    def __setitem__(self, attrId, value):
        # Write value and clear all attributes relying on it
        self.__modifiedAttributes[attrId] = value
        self.__holder.fit._linkTracker.clearHolderAttributeDependents(self.__holder, attrId)

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

        Possible exceptions:
        AbsentAttributeBaseException -- attribute cannot be
        calculated, as its base value is not available
        """
        # Attribute object for attribute being calculated
        dataHandler = self.__holder.fit._eos._dataHandler
        try:
            attrMeta = dataHandler.getAttribute(attrId)
        # Raise error if it cannot be found
        except AttributeFetchError as e:
            raise EveAttributeError(attrId) from e
        # Base attribute value which we'll use for modification
        baseAttribDict = self.__holder.item.attributes
        try:
            result = baseAttribDict[attrId]
        # If attribute isn't available on base item,
        # base off its default value
        except KeyError:
            result = attrMeta.defaultValue
            # If no default value is available, raise error
            if result is None:
                raise BaseValueError(attrId)
        # Container for non-penalized modifiers
        # Format: {operator: [values]}
        normalMods = {}
        # Container for penalized modifiers
        # Format: {operator: [values]}
        penalizedMods = {}
        # Now, go through all affectors affecting our holder
        for affector in self.__holder.fit._linkTracker.getAffectors(self.__holder, attrId=attrId):
            try:
                sourceHolder, info = affector
                operator = info.operator
                # Decide if it should be stacking penalized or not, based on stackable property,
                # source item category and operator
                penalize = (not attrMeta.stackable and not sourceHolder.item.categoryId in penaltyImmuneCategories
                            and operator in penalizableOperators)
                # If source value is attribute reference, get its value
                if info.sourceType == SourceType.attribute:
                    modValue = sourceHolder.attributes[info.sourceValue]
                # For value modifications, just use stored in info value
                elif info.sourceType == SourceType.value:
                    modValue = info.sourceValue
                else:
                    raise SourceTypeError(info.sourceType)
                # Check modValue for correctness
                if modValue is None:
                    raise SourceValueError(modValue)
                # Normalize operations to just three types:
                # assignments, additions, multiplications
                try:
                    normalize = normalizationMap[operator]
                # Raise error on any unknown operator types
                except KeyError as e:
                    raise OperatorError(operator) from e
                modValue = normalize(modValue)
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
            # Handle operator and source type failure
            except OperatorError as e:
                msg = "malformed info on item {}: unknown operator {}".format(sourceHolder.item.id, e.args[0])
                signature = (OperatorError, sourceHolder.item.id, e.args[0])
                self.__holder.fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
                continue
            except SourceTypeError as e:
                msg = "malformed info on item {}: unknown source type {}".format(sourceHolder.item.id, e.args[0])
                signature = (SourceTypeError, sourceHolder.item.id, e.args[0])
                self.__holder.fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
                continue
            except SourceValueError as e:
                msg = "malformed source value {} on item {}".format(e.args[0], sourceHolder.item.id)
                signature = (SourceValueError, sourceHolder.item.id, e.args[0])
                self.__holder.fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
                continue
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
            if operator in assignments:
                result = max(modList) if attrMeta.highIsGood is True else min(modList)
            elif operator in additions:
                for modVal in modList:
                    result += modVal
            elif operator in multiplications:
                for modVal in modList:
                    result *= modVal
        # If attribute has upper cap, do not let
        # its value to grow above it
        if attrMeta.maxValue is not None:
            result = min(result, attrMeta.maxValue)
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
