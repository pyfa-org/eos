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

from eos import const

class InvType:
    """
    A type, the basic building blocks of EVE. Everything that can do something is a type.
    Each type is built out of several effects and attributes.
    This class is typically reused by the dataHandler if the same id is requested multiple times.
    As such, there shouldn't be ANY fit-specific data on it
    """

    def __init__(self, id, categoryId, groupId, effects, attributes):
        # The id of the type, typically, this is the one taken from the SDD from CCP.
        # Can be anything if you're defining your own types, as long as it's hashable
        self.id = id

        # The categoryId of the type, used for stacking penalty calculations. Should be
        # integer, typically an already existing category
        self.categoryId = categoryId

        # The groupID of the type, this is used for filtering purposes in the expressions.
        # Should be integer, you usually want to use an already existing group if you're defining
        # your own types so effects can apply to it
        self.groupId = groupId

        # Set of effects this type has, these will be ran when
        # module using this type gets added onto a fit
        # Format: set(effects)
        self.effects = effects

        # The attributes of this type, these are used by the effects
        # to apply their bonuses onto when they're ran
        # Format: {attributeId: attributeValue}
        self.attributes = attributes

        # Stores required skill IDs as set once calculated
        self.__requiredSkills = None

    def requiredSkills(self):
        if self.__requiredSkills is None:
            attributes = self.attributes
            self.__requiredSkills = set()
            for v in const.attrSkillRqMap:
                req = attributes.get(v)
                if req is not None:
                    self.__requiredSkills.add(int(req))
        return self.__requiredSkills
