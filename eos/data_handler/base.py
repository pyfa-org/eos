# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
# ==============================================================================


from abc import ABCMeta
from abc import abstractmethod


class BaseDataHandler(metaclass=ABCMeta):
    """Abstract base class for data handlers.

    Data handlers fetch 'raw' data from external source. Its abstract methods
    are named against data structures (usually tables) they request, returning
    iterable with rows, each row being dictionary in {field name: field value}
    format.
    """

    @abstractmethod
    def get_evetypes(self):
        """
        Fields:
            typeID
            groupID
            capacity
            mass
            radius
            volume
        """
        ...

    @abstractmethod
    def get_evegroups(self):
        """
        Fields:
            groupID
            categoryID
        """
        ...

    @abstractmethod
    def get_dgmattribs(self):
        """
        Fields:
            attributeID
            maxAttributeID
            defaultValue
            highIsGood
            stackable
        """
        ...

    @abstractmethod
    def get_dgmtypeattribs(self):
        """
        Fields:
            typeID
            attributeID
            value
        """
        ...

    @abstractmethod
    def get_dgmeffects(self):
        """
        Fields:
            effectID
            effectCategory
            isOffensive
            isAssistance
            durationAttributeID
            dischargeAttributeID
            rangeAttributeID
            falloffAttributeID
            trackingSpeedAttributeID
            fittingUsageChanceAttributeID
            resistanceID
            preExpression
            postExpression
            modifierInfo
        """
        ...

    @abstractmethod
    def get_dgmtypeeffects(self):
        """
        Fields:
            typeID
            effectID
            isDefault
        """
        ...

    @abstractmethod
    def get_dgmexpressions(self):
        """
        Fields:
            expressionID
            operandID
            arg1
            arg2
            expressionValue
            expressionTypeID
            expressionGroupID
            expressionAttributeID
        """
        ...

    @abstractmethod
    def get_typefighterabils(self):
        """
        Fields:
            typeID
            abilityID
            cooldownSeconds
            chargeCount
        """
        ...

    @abstractmethod
    def get_version(self):
        """Get version of data.

        Returns:
            String with version.
        """
        ...
