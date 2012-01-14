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

class Register():
    """
    Keep track of links between fit's local holders, which is required for efficient
    partial attribute recalculation
    """

    def __init__(self, fit):
        # The fit we're keeping track of things for
        self.__fit = fit

        # Keep track of holders belonging to certain location
        # Format: location: set(targetHolders)
        self.__affecteeLocation = {}

        # Keep track of holders belonging to certain location and group
        # Format: (location, group): set(targetHolders)
        self.__affecteeLocationGroup = {}

        # Keep track of holders belonging to certain location and having certain skill requirement
        # Format: (location, skill): set(targetHolders)
        self.__affecteeLocationSkill = {}

        # Keep track of affectors influencing all holders belonging to certain location
        # Format: location: set(affectors)
        self.__affectorLocation = {}

        # Keep track of affectors influencing holders belonging to certain location and group
        # Format: (location, group): set(affectors)
        self.__affectorLocationGroup = {}

        # Keep track of affectors influencing holders belonging to certain location and having certain skill requirement
        # Format: (location, skill): set(affectors)
        self.__affectorLocationSkill = {}

        # Keep track of affectors influencing holders directly
        # Format: targetHolder: set(affectors)
        self.__affectorHolder = {}

        # Keep track of affectors which influence locOther, but are disabled
        # as other location is not available
        # Format: sourceHolder: set(affectors)
        self.__disabledOtherAffectors = {}

    def __getAffecteeMaps(self, targetHolder):
        """
        Helper for affectee register/unregister methods, provides (key, map)
        list to use according to passed holder
        """
        location = targetHolder.location
        # Container which temporarily holds (key, map) tuples
        affecteeMaps = []
        affecteeMaps.append((location, self.__affecteeLocation))
        group = targetHolder.invType.groupId
        if group is not None:
            affecteeMaps.append(((location, group), self.__affecteeLocationGroup))
        for skill in targetHolder.invType.requiredSkills():
            affecteeMaps.append(((location, skill), self.__affecteeLocationSkill))
        return affecteeMaps

    def __getAffectorMap(self, affector):
        """
        Helper for affector register/unregister methods, provides key and
        map to use according to passed affector
        """
        sourceHolder, info = affector
        # For each filter type, define affector map and key to use
        if info.filterType is None:
            # For single item modifications, we need to properly pick
            # target holder (it's key) based on location
            affectorMap = self.__affectorHolder
            if info.location == const.locSelf:
                key = sourceHolder
            elif info.location == const.locChar:
                key = self.__fit.character
            elif info.location == const.locShip:
                key = self.__fit.ship
            elif info.location == const.locTgt:
                raise RuntimeError("target is not supported location for direct item modification")
            # When other location is referenced, it means direct reference to module's charge
            # or to charge's module-container
            elif info.location == const.locOther:
                otherHolder = getattr(sourceHolder, "other", None)
                if otherHolder is not None:
                    key = otherHolder
                # When no reference available, it means that e.g. charge may be
                # unavailable for now; use disabled affectors map for these
                else:
                    affectorMap = self.__disabledOtherAffectors
                    key = sourceHolder
            else:
                raise RuntimeError("unknown location (ID {}) passed for direct item modification".format(info.location))
        # For massive modifications, compose key, making sure reference to self
        # is converted into appropriate real location
        elif info.filterType == const.filterAll:
            affectorMap = self.__affectorLocation
            location = self.__contextizeLocation(sourceHolder, info.location)
            key = location
        elif info.filterType == const.filterGroup:
            affectorMap = self.__affectorLocationGroup
            location = self.__contextizeLocation(sourceHolder, info.location)
            key = (location, info.filterValue)
        elif info.filterType == const.filterSkill:
            affectorMap = self.__affectorLocationSkill
            location = self.__contextizeLocation(sourceHolder, info.location)
            skill = self.__contextizeSkillrqId(affector)
            key = (location, skill)
        return affectorMap, key

    def __contextizeLocation(self, sourceHolder, targetLocation):
        """
        Converts location self-reference to real location, like character or ship,
        used only in modifications of multiple filtered holders
        """
        # Reference to self is sparingly used on ship effects, so we must convert
        # it to real location
        if targetLocation == const.locSelf:
            if sourceHolder is self.__fit.ship:
                return const.locShip
            elif sourceHolder is self.__fit.character:
                return const.locChar
            else:
                raise RuntimeError("reference to self on unexpected holder during processing of massive filtered modification")
        # Just return untouched location for all other valid cases
        elif targetLocation in (const.locChar, const.locShip, const.locSpace):
            return targetLocation
        # Raise error if location is invalid
        else:
            raise RuntimeError("unsupported location (ID {}) for massive filtered modifications".format(targetLocation))

    def __contextizeSkillrqId(self, affector):
        """Convert typeID self-reference into real typeID"""
        skillId = affector.info.filterValue
        if skillId == const.selfTypeID:
            skillId = affector.sourceHolder.invType.id
        return skillId

    def registerAffectee(self, targetHolder):
        """Add passed holder to register's maps"""
        for key, affecteeMap in self.__getAffecteeMaps(targetHolder):
            # Add data to map; also, make sure to initialize set if it's not there
            try:
                value = affecteeMap[key]
            except KeyError:
                value = affecteeMap[key] = set()
            value.add(targetHolder)
        # Check if we have other location (charge's module/module's charge) holder,
        # also check if our holder which is being registered should be affected by it
        # We do this step in affectee registration because it should occur only once,
        # when holder is added to the fit
        otherHolder = getattr(targetHolder, "other", None)
        if otherHolder is not None and otherHolder in self.__disabledOtherAffectors:
            # Get all disabled affectors which should influence our targetHolder
            affectorsToEnable = self.__disabledOtherAffectors[otherHolder]
            # Move all of them to direct modification dictionary
            try:
                targetHolderDirectAffectors = self.__affectorHolder[targetHolder]
            except KeyError:
                targetHolderDirectAffectors = self.__affectorHolder[targetHolder] = set()
            targetHolderDirectAffectors.update(affectorsToEnable)
            # And remove from disabled other affectors from dictionary altogether
            del self.__disabledOtherAffectors[otherHolder]

    def unregisterAffectee(self, targetHolder):
        """Remove passed holder from register's maps"""
        for key, affecteeMap in self.__getAffecteeMaps(targetHolder):
            # For affectee maps, item we're going to remove always should be there,
            # so we're not doing any additional checks
            value = affecteeMap[key]
            value.remove(targetHolder)
            # Remove items with empty sets from dictionaries
            if len(value) == 0:
                del affecteeMap[key]
        # Like we do in registration, we have to do similar things, but in reverse
        # way: check if holder being unregistered was influenced by affector belonging
        # to otherHolder via locOther location. If it was affected, we should move
        # such affector to disabledOtherAffectors so it can be re-used in future
        otherHolder = getattr(targetHolder, "other", None)
        if otherHolder is not None:
            affectorsToDisable = set()
            # Go through all affectors influencing holder being unregistered
            for affector in self.__affectorHolder.get(targetHolder, set()):
                # If affector originates from other holder, mark it as
                # to-be-disabled
                if affector.sourceHolder is otherHolder:
                    affectorsToDisable.add(affector)
            if len(affectorsToDisable) > 0:
                try:
                    disabledOtherAffectors = self.__disabledOtherAffectors[otherHolder]
                except KeyError:
                    disabledOtherAffectors = self.__disabledOtherAffectors[otherHolder] = set()
                disabledOtherAffectors.update(affectorsToDisable)
                value = self.__affectorHolder[targetHolder]
                value.difference_update(affectorsToDisable)
                if len(value) == 0:
                    del self.__affectorHolder[targetHolder]

    def registerAffector(self, affector):
        """Add passed affector to register's affector maps"""
        info = affector.info
        # Register keeps track of only local duration modifiers
        if info.type != const.infoDuration or info.gang is not False:
            return
        affectorMap, key = self.__getAffectorMap(affector)
        # Actually add data to map
        try:
            value = affectorMap[key]
        except KeyError:
            value = affectorMap[key] = set()
        value.add((affector))

    def unregisterAffector(self, affector):
        """Remove affector from register's affector maps"""
        info = affector.info
        if info.type != const.infoDuration or info.gang is not False:
            return
        affectorMap, key = self.__getAffectorMap(affector)
        # As affector addition can be conditional, we're not guaranteed that
        # affector is there, so we have to make full set of checks on removal
        # attempt
        value = affectorMap.get(key)
        # Do nothing if value doesn't contain set
        if value is not None:
            # Do not raise exception when there's no our affector in set
            try:
                value.remove(affector)
            except KeyError:
                pass
            # When no entries in set remain, clean up to
            # not stockpile garbage
            if len(value) == 0:
                del affectorMap[key]

    def getAffectees(self, affector):
        """Get all holders influenced by passed affector"""
        sourceHolder, info = affector
        affectees = set()
        # For direct modification, make set out of single target location
        if info.filterType is None:
            if info.location == const.locSelf:
                target = {sourceHolder}
            elif info.location == const.locChar:
                target = {self.__fit.character}
            elif info.location == const.locShip:
                target = {self.__fit.ship}
            elif info.location == const.locTgt:
                raise RuntimeError("target is not supported location for direct item modification")
            elif info.location == const.locOther:
                otherHolder = getattr(sourceHolder, "other", None)
                if otherHolder is not None:
                    target = {otherHolder}
                else:
                    target = None
            else:
                raise RuntimeError("unknown location (ID {}) passed for direct item modification".format(info.location))
        # For filtered modifications, pick appropriate dictionary and get set
        # with target holders
        elif info.filterType == const.filterAll:
            key = self.__contextizeLocation(sourceHolder, info.location)
            target = self.__affecteeLocation.get(key, set())
        elif info.filterType == const.filterGroup:
            location = self.__contextizeLocation(sourceHolder, info.location)
            key = (location, info.filterValue)
            target = self.__affecteeLocationGroup.get(key, set())
        elif info.filterType == const.filterSkill:
            location = self.__contextizeLocation(sourceHolder, info.location)
            skill = self.__contextizeSkillrqId(affector)
            key = (location, skill)
            target = self.__affecteeLocationSkill.get(key, set())
        # Add our set to affectees
        if target is not None:
            affectees.update(target)
        return affectees

    def getAffectors(self, targetHolder):
        """Get all affectors, which influence passed holder"""
        affectors = set()
        # Add all affectors which directly affect it
        affectors.update(self.__affectorHolder.get(targetHolder, set()))
        # Then all affectors which affect location of passed holder
        location = targetHolder.location
        affectors.update(self.__affectorLocation.get(location, set()))
        # All affectors which affect location and group of passed holder
        group = targetHolder.invType.groupId
        affectors.update(self.__affectorLocationGroup.get((location, group), set()))
        # Same, but for location & skill requirement of passed holder
        for skill in targetHolder.invType.requiredSkills():
            affectors.update(self.__affectorLocationSkill.get((location, skill), set()))
        return affectors
