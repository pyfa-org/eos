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

from eos.const import Attribute


class InvType:
    """
    InvType represents any EVE item. All characters, ships, incursion system-wide effects
    are actually items.
    """

    def __init__(self, typeId, groupId=None, categoryId=None, fittableNonSingleton=None, attributes={}, effects=set()):
        # The ID of the type
        self.id = int(typeId) if typeId is not None else None

        # The groupID of the type, integer
        self.groupId = int(groupId) if groupId is not None else None

        # The category ID of the type, integer
        self.categoryId = int(categoryId) if categoryId is not None else None

        # Defines if multiple items can be added to fit without packaging.
        # We use it to see if charge can be loaded into anything or not.
        self.fittableNonSingleton = bool(fittableNonSingleton) if fittableNonSingleton is not None else None

        # The attributes of this type, used as base for calculation of modified
        # attributes, thus they should stay immutable
        # Format: {attributeId: attributeValue}
        self.attributes = attributes

        # Set of effects this type has, they describe modifications
        # which this invType applies
        self.effects = effects

        # Stores required skill IDs as set once calculated
        self.__requiredSkills = None

    def requiredSkills(self):
        """Detect IDs of required skills based on invType's attributes"""
        if self.__requiredSkills is None:
            self.__requiredSkills = set()
            for srqAttrId in Attribute.skillRqMap:
                srq = self.attributes.get(srqAttrId)
                if srq is not None:
                    self.__requiredSkills.add(int(srq))
        return self.__requiredSkills
