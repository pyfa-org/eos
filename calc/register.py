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

class DataSetMap(dict):
    """
    Dictionary-like class, with couple of methods which make it easier to
    use it as set storage
    """

    def addData(self, key, data):
        """Adds data set to dictionary with proper creation jobs"""
        try:
            value = self[key]
        except KeyError:
            value = self[key] = set()
        value.update(data)

    def rmData(self, key, data):
        """Remove data set from dictionary with proper cleanup jobs"""
        try:
            value = self[key]
        except KeyError:
            return
        else:
            value.difference_update(data)
            if len(value) == 0:
                del self[key]

    def getData(self, key):
        """Get data set with safe fallback"""
        data = self.get(key, set())
        return data

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
        self.__affecteeLocation = DataSetMap()

        # Keep track of holders belonging to certain location and group
        # Format: (location, group): set(targetHolders)
        self.__affecteeLocationGroup = DataSetMap()

        # Keep track of holders belonging to certain location and having certain skill requirement
        # Format: (location, skill): set(targetHolders)
        self.__affecteeLocationSkill = DataSetMap()

        # Keep track of affectors influencing all holders belonging to certain location
        # Format: location: set(affectors)
        self.__affectorLocation = DataSetMap()

        # Keep track of affectors influencing holders belonging to certain location and group
        # Format: (location, group): set(affectors)
        self.__affectorLocationGroup = DataSetMap()

        # Keep track of affectors influencing holders belonging to certain location and having certain skill requirement
        # Format: (location, skill): set(affectors)
        self.__affectorLocationSkill = DataSetMap()

        # Keep track of affectors influencing holders directly
        # Format: targetHolder: set(affectors)
        self.__activeDirectAffectors = DataSetMap()

        # Keep track of affectors which influence locOther, but are disabled
        # as their target location is not available
        # Format: sourceHolder: set(affectors)
        self.__disabledDirectAffectors = DataSetMap()

    def __getAffecteeMaps(self, targetHolder):
        """
        Helper for affectee register/unregister methods, provides (key, map)
        list to use according to passed holder
        """
        # Container which temporarily holds (key, map) tuples
        affecteeMaps = []
        location = targetHolder.location
        if location is not None:
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
            if info.location == const.locSelf:
                affectorMap = self.__activeDirectAffectors
                key = sourceHolder
            elif info.location == const.locChar:
                char = self.__fit.character
                if char is not None:
                    affectorMap = self.__activeDirectAffectors
                    key = char
                else:
                    affectorMap = self.__disabledDirectAffectors
                    key = sourceHolder
            elif info.location == const.locShip:
                ship = self.__fit.ship
                if ship is not None:
                    affectorMap = self.__activeDirectAffectors
                    key = ship
                else:
                    affectorMap = self.__disabledDirectAffectors
                    key = sourceHolder
            elif info.location == const.locTgt:
                raise RuntimeError("target is not supported location for direct item modification")
            # When other location is referenced, it means direct reference to module's charge
            # or to charge's module-container
            elif info.location == const.locOther:
                otherHolder = getattr(sourceHolder, "other", None)
                if otherHolder is not None:
                    affectorMap = self.__activeDirectAffectors
                    key = otherHolder
                # When no reference available, it means that e.g. charge may be
                # unavailable for now; use disabled affectors map for these
                else:
                    affectorMap = self.__disabledDirectAffectors
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

    def __enableDirectSpec(self, targetHolder, targetLocation):
        """Enable temporarily disabled affectors, targeting specific location"""
        affectorsToEnable = set()
        # Cycle through all disabled direct affectors
        for affectorSet in self.__disabledDirectAffectors.values():
            for affector in affectorSet:
                info = affector.info
                # Mark affector as to-be-enabled only when it specifically
                # targets passed target location, and not holders assigned
                # to it
                if info.location == targetLocation and info.filterType is None:
                    affectorsToEnable.add(affector)
        # Bail if we have nothing to do
        if len(affectorsToEnable) == 0:
            return
        # Move all of them to direct modification dictionary
        self.__activeDirectAffectors.addData(targetHolder, affectorsToEnable)
        for affector in affectorsToEnable:
            self.__disabledDirectAffectors.rmData(affector.sourceHolder, {affector})

    def __disableDirectSpec(self, targetHolder):
        """Disable affectors, targeting specific location"""
        affectorsToDisable = set()
        # Check all affectors, targeting passed holder
        for affector in self.__activeDirectAffectors.getData(targetHolder):
            # Mark them as to-be-disabled only if they originate from
            # other holder, else they should be removed with passed holder
            if affector.sourceHolder is not targetHolder:
                affectorsToDisable.add(affector)
        if len(affectorsToDisable) == 0:
            return
        # Move data from map to map
        for affector in affectorsToDisable:
            self.__disabledDirectAffectors.addData(affector.sourceHolder, {affector})
        self.__activeDirectAffectors.rmData(targetHolder, affectorsToDisable)

    def __enableDirectOther(self, targetHolder):
        """Enable temporarily disabled affectors, targeting "other" location"""
        otherHolder = getattr(targetHolder, "other", None)
        # If passed holder doesn't have other location (charge's module
        # or module's charge), do nothing
        if otherHolder is None:
            return
        # Get all disabled affectors which should influence our targetHolder
        affectorsToEnable = set()
        for affector in self.__disabledDirectAffectors.getData(otherHolder):
            info = affector.info
            if info.location == const.locOther and info.filterType is None:
                affectorsToEnable.add(affector)
        # Bail if we have nothing to do
        if len(affectorsToEnable) == 0:
            return
        # Move all of them to direct modification dictionary
        self.__activeDirectAffectors.addData(targetHolder, affectorsToEnable)
        self.__disabledDirectAffectors.rmData(otherHolder, affectorsToEnable)

    def __disableDirectOther(self, targetHolder):
        """Disabled affectors, targeting "other" location"""
        otherHolder = getattr(targetHolder, "other", None)
        if otherHolder is None:
            return
        affectorsToDisable = set()
        # Go through all affectors influencing holder being unregistered
        for affector in self.__activeDirectAffectors.getData(targetHolder):
            # If affector originates from otherHolder, mark it as
            # to-be-disabled
            if affector.sourceHolder is otherHolder:
                affectorsToDisable.add(affector)
        # Do nothing if we have no such affectors
        if len(affectorsToDisable) == 0:
            return
        # If we have, move them from map to map
        self.__disabledDirectAffectors.addData(otherHolder, affectorsToDisable)
        self.__activeDirectAffectors.rmData(targetHolder, affectorsToDisable)

    def registerAffectee(self, targetHolder, enableDirect=None):
        """Add passed target holder to register's maps"""
        for key, affecteeMap in self.__getAffecteeMaps(targetHolder):
            # Add data to map
            affecteeMap.addData(key, {targetHolder})
        # Check if we have affectors which should directly influence passed holder,
        # but are disabled
        directEnablers = {const.locShip: (self.__enableDirectSpec, (targetHolder, const.locShip), {}),
                          const.locChar: (self.__enableDirectSpec, (targetHolder, const.locChar), {}),
                          const.locOther: (self.__enableDirectOther, (targetHolder,), {})}
        try:
            method, args, kwargs = directEnablers[enableDirect]
        except KeyError:
            pass
        else:
            method(*args, **kwargs)

    def unregisterAffectee(self, targetHolder, disableDirect=None):
        """Remove passed target holder from register's maps"""
        for key, affecteeMap in self.__getAffecteeMaps(targetHolder):
            affecteeMap.rmData(key, {targetHolder})
        # When removing holder from register, make sure to move modifiers which
        # originate from other holders and directly affect it to disabled map
        directEnablers = {const.locShip: (self.__disableDirectSpec, (targetHolder,), {}),
                          const.locChar: (self.__disableDirectSpec, (targetHolder,), {}),
                          const.locOther: (self.__disableDirectOther, (targetHolder,), {})}
        try:
            method, args, kwargs = directEnablers[disableDirect]
        except KeyError:
            pass
        else:
            method(*args, **kwargs)

    def registerAffector(self, affector):
        """Add passed affector to register's affector maps"""
        info = affector.info
        # Register keeps track of only local duration modifiers
        if info.type != const.infoDuration or info.gang is not False:
            return
        affectorMap, key = self.__getAffectorMap(affector)
        # Actually add data to map
        affectorMap.addData(key, {affector})

    def unregisterAffector(self, affector):
        """Remove affector from register's affector maps"""
        info = affector.info
        if info.type != const.infoDuration or info.gang is not False:
            return
        affectorMap, key = self.__getAffectorMap(affector)
        affectorMap.rmData(key, {affector})

    def getAffectees(self, affector):
        """Get all holders influenced by passed affector"""
        sourceHolder, info = affector
        affectees = set()
        # For direct modification, make set out of single target location
        if info.filterType is None:
            if info.location == const.locSelf:
                target = {sourceHolder}
            elif info.location == const.locChar:
                char = self.__fit.character
                target = {char} if char is not None else None
            elif info.location == const.locShip:
                ship = self.__fit.ship
                target = {ship} if ship is not None else None
            elif info.location == const.locTgt:
                raise RuntimeError("target is not supported location for direct item modification")
            elif info.location == const.locOther:
                otherHolder = getattr(sourceHolder, "other", None)
                target = {otherHolder} if otherHolder is not None else None
            else:
                raise RuntimeError("unknown location (ID {}) passed for direct item modification".format(info.location))
        # For filtered modifications, pick appropriate dictionary and get set
        # with target holders
        elif info.filterType == const.filterAll:
            key = self.__contextizeLocation(sourceHolder, info.location)
            target = self.__affecteeLocation.getData(key)
        elif info.filterType == const.filterGroup:
            location = self.__contextizeLocation(sourceHolder, info.location)
            key = (location, info.filterValue)
            target = self.__affecteeLocationGroup.getData(key)
        elif info.filterType == const.filterSkill:
            location = self.__contextizeLocation(sourceHolder, info.location)
            skill = self.__contextizeSkillrqId(affector)
            key = (location, skill)
            target = self.__affecteeLocationSkill.getData(key)
        # Add our set to affectees
        if target is not None:
            affectees.update(target)
        return affectees

    def getAffectors(self, targetHolder):
        """Get all affectors, which influence passed holder"""
        affectors = set()
        # Add all affectors which directly affect it
        affectors.update(self.__activeDirectAffectors.getData(targetHolder))
        # Then all affectors which affect location of passed holder
        location = targetHolder.location
        affectors.update(self.__affectorLocation.getData(location))
        # All affectors which affect location and group of passed holder
        group = targetHolder.invType.groupId
        affectors.update(self.__affectorLocationGroup.getData((location, group)))
        # Same, but for location & skill requirement of passed holder
        for skill in targetHolder.invType.requiredSkills():
            affectors.update(self.__affectorLocationSkill.getData((location, skill)))
        return affectors
