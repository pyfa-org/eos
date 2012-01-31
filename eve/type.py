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


from eos.const import nulls, Attribute, Effect, EffectCategory
from eos.fit.calc.info.info import InfoState


class Slot:
    """Slot type ID holder"""
    moduleHigh = 1
    moduleMed = 2
    moduleLow = 3
    rig = 4
    subsystem = 5
    turret = 6
    launcher = 7

    @classmethod
    def _effectToSlot(cls, effectId):
        """
        Convert effect to slot item uses.

        Positional arguments:
        effectId -- effect ID

        Return value:
        ID of slot, which corresponds to passed effect,
        or None if no corresponding slot was found
        """
        # Format: {effect ID: slot ID}
        conversionMap = {Effect.loPower: Slot.moduleLow,
                         Effect.hiPower: Slot.moduleHigh,
                         Effect.medPower: Slot.moduleMed,
                         Effect.launcherFitted: Slot.launcher,
                         Effect.turretFitted: Slot.turret,
                         Effect.rigSlot: Slot.rig,
                         Effect.subSystem: Slot.subsystem}
        try:
            result = conversionMap[effectId]
        except KeyError:
            result = None
        return result


class Type:
    """
    Type represents any EVE item. All characters, ships,
    incursion system-wide effects are actually items.
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

        # Cache targeted flag
        self.__targeted = None

        # Cached set with slot types
        self.__slots = None

    @property
    def requiredSkills(self):
        """
        Get skill requirements.

        Return value:
        Set with IDs of skills which are required to use type
        """
        if self.__requiredSkills is None:
            self.__requiredSkills = set()
            for srqAttrId in Attribute.skillRqMap:
                srq = self.attributes.get(srqAttrId)
                if srq is not None:
                    self.__requiredSkills.add(int(srq))
        return self.__requiredSkills

    @property
    def infos(self):
        """
        Get all infos spawned by effects.

        Return value:
        Set with Info objects generated by type's effects
        """
        infos = set()
        for effect in self.effects:
            for info in effect.infos:
                infos.add(info)
        return infos

    @property
    def maxState(self):
        """
        Get highest state this type is allowed to take.

        Return value:
        State class' attribute value, representing highest state
        """
        if self.__maxState is None:
            # All types can be at least offline,
            # even when they have no effects
            maxState = InfoState.offline
            for effect in self.effects:
                # Convert effect category to state
                effectState = InfoState._effectCategoryToState(effect.categoryId)
                if effectState is not None:
                    maxState = max(maxState, effectState)
            self.__maxState = maxState
        return self.__maxState

    @property
    def isTargeted(self):
        """
        Report if type is targeted or not. Targeted types cannot be
        activated w/o target selection.

        Return value:
        Boolean targeted flag
        """
        if self.__targeted is None:
            # Assume type is not targeted by default
            targeted = False
            for effect in self.effects:
                # If any of effects is targeted, then type is targeted
                if effect.categoryId == EffectCategory.target:
                    targeted = True
            self.__targeted = targeted
        return self.__targeted

    @property
    def slots(self):
        """
        Get types of slots this type occupies.

        Return value:
        Set with slot types
        """
        if self.__slots is None:
            # Container for slot types item uses
            slots = set()
            for effect in self.effects:
                # Convert effect ID to slot type item takes
                slot = Slot._effectToSlot(effect.Id)
                if slot is not None:
                    slots.add(slot)
            self.__slots = slots
        return self.__slots
