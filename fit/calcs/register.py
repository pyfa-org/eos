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
            elif info.location == const.locOther:
                raise RuntimeError("other is not supported location for direct item modification")
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
        # First off, check passed location against list of valid locations
        allowedLocations = (const.locChar, const.locShip, const.locSpace, const.locSelf)
        if not targetLocation in allowedLocations:
            raise RuntimeError("unsupported location (ID {}) for massive filtered modifications".format(targetLocation))
        # Reference to self is sparingly used on ship effects, so we must convert
        # it to real location
        elif targetLocation == const.locSelf:
            if sourceHolder is self.__fit.ship:
                return const.locShip
            elif sourceHolder is self.__fit.character:
                return const.locChar
            else:
                raise RuntimeError("reference to self on unexpected holder during processing of massive filtered modification")
        # Just return untouched location for all other valid cases
        else:
            return targetLocation

    def __contextizeSkillrqId(self, affector):
        """Convert typeID self-reference into real typeID"""
        skillId = affector.info.filterValue
        if skillId == const.selfTypeID:
            skillId = affector.sourceHolder.invType.id
        return skillId

    def registerAffectee(self, targetHolder):
        """Add passed holder to register's affectee maps"""
        for key, affecteeMap in self.__getAffecteeMaps(targetHolder):
            # Add data to map; also, make sure to initialize set if it's not there
            value = affecteeMap.get(key)
            if value is None:
                value = affecteeMap[key] = set()
            value.add(targetHolder)

    def unregisterAffectee(self, targetHolder):
        """Remove passed holder from register's affectee maps"""
        for key, affecteeMap in self.__getAffecteeMaps(targetHolder):
            # For affectee maps, item we're going to remove always should be there,
            # so we're not doing any additional checks
            affecteeMap[key].remove(targetHolder)

    def registerAffector(self, affector):
        """Add passed affector to register's affector maps"""
        info = affector.info
        # Register keeps track of only local duration modifiers
        if info.type != const.infoDuration or info.gang is not False:
            return
        affectorMap, key = self.__getAffectorMap(affector)
        # Actually add data to map
        value = affectorMap.get(key)
        if value is None:
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
                raise RuntimeError("other is not supported location for direct item modification")
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
