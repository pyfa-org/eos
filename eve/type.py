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


from eos.const import nulls, Attribute
from eos.calc.state import State
from eos.calc.info.info import InfoContext


class Type:
    """
    Type represents any EVE item. All characters, ships, incursion system-wide effects
    are actually items.
    """

    def __init__(self, typeId, groupId=None, categoryId=None, durationAttributeId=None, dischargeAttributeId=None,
                 rangeAttributeId=None, falloffAttributeId=None, trackingSpeedAttributeId=None, fittableNonSingleton=None,
                 attributes={}, effects=set()):
        # The ID of the type
        self.id = int(typeId) if typeId is not None else None

        # The groupID of the type, integer
        self.groupId = int(groupId) if not groupId in nulls else None

        # The category ID of the type, integer
        self.categoryId = int(categoryId) if not categoryId in nulls else None

        # Defines cycle time
        self._durationAttributeId = int(durationAttributeId) if not durationAttributeId in nulls else None

        # Defines attribute, whose value will be used to drain ship's
        # capacitor each cycle
        self._dischargeAttributeId = int(dischargeAttributeId) if not dischargeAttributeId in nulls else None

        # Attribute with this ID defines optimal range of item
        self._rangeAttributeId = int(rangeAttributeId) if not rangeAttributeId in nulls else None

        # Defines falloff attribute
        self._falloffAttributeId = int(falloffAttributeId) if not falloffAttributeId in nulls else None

        # Defines tracking speed attribute
        self._trackingSpeedAttributeId = int(trackingSpeedAttributeId) if not trackingSpeedAttributeId in nulls else None

        # Defines if multiple items of this type can be added to fit without packaging.
        # We use it to see if charge can be loaded into anything or not.
        self._fittableNonSingleton = bool(fittableNonSingleton) if fittableNonSingleton is not None else None

        # The attributes of this type, used as base for calculation of modified
        # attributes, thus they should stay immutable
        # Format: {attributeId: attributeValue}
        self.attributes = attributes

        # Set of effects this type has, they describe modifications
        # which this type applies
        self.effects = effects

        # Stores required skill IDs as set once calculated
        self.__requiredSkills = None

        # Caches results of max allowed state as integer ID
        self.__maxState = None

    def requiredSkills(self):
        """Detect IDs of required skills based on type's attributes"""
        if self.__requiredSkills is None:
            self.__requiredSkills = set()
            for srqAttrId in Attribute.skillRqMap:
                srq = self.attributes.get(srqAttrId)
                if srq is not None:
                    self.__requiredSkills.add(int(srq))
        return self.__requiredSkills

    def getInfos(self):
        """Get all infos spawned by effects"""
        infos = set()
        for effect in self.effects:
            for info in effect.getInfos():
                infos.add(info)
        return infos

    def getMaxState(self):
        """Return highest state ID this type is allowed to take"""
        if self.__maxState is None:
            # All types can be at least offline,
            # even when they have no effects
            maxState = State.offline
            # We need to iterate through effects of type instead of infos because
            # effect doesn't necessarily generate info, but we need data from all
            # effects to reliably detect max state
            for effect in self.effects:
                # Convert effect category to info context, context into
                # holder state
                context = InfoContext.eve2eos(effect.categoryId)
                effectState = State._context2state(context)
                if effectState is not None:
                    maxState = max(maxState, effectState)
            self.__maxState = maxState
        return self.__maxState
