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


from eos.const import Location, FilterType, InvType
from eos.util.keyedSet import KeyedSet
from .exception import BadContainerException, UnsupportedFilterException, UnsupportedDirectLocationException, UnsupportedFilteredLocationException


class LinkRegister:
    """
    Keep track of links between holders, which is required for efficient
    partial attribute recalculation.

    Positional arguments:
    fit -- Fit object to which register is assigned
    """

    def __init__(self, fit):
        # The fit we're keeping track of things for
        self.__fit = fit

        # Keep track of holders belonging to certain location
        # Format: {location: {targetHolders}}
        self.__affecteeLocation = KeyedSet()

        # Keep track of holders belonging to certain location and group
        # Format: {(location, group): {targetHolders}}
        self.__affecteeLocationGroup = KeyedSet()

        # Keep track of holders belonging to certain location and having certain skill requirement
        # Format: {(location, skill): {targetHolders}}
        self.__affecteeLocationSkill = KeyedSet()

        # Keep track of affectors influencing all holders belonging to certain location
        # Format: {location: {affectors}}
        self.__affectorLocation = KeyedSet()

        # Keep track of affectors influencing holders belonging to certain location and group
        # Format: {(location, group): {affectors}}
        self.__affectorLocationGroup = KeyedSet()

        # Keep track of affectors influencing holders belonging to certain location and having certain skill requirement
        # Format: {(location, skill): {affectors}}
        self.__affectorLocationSkill = KeyedSet()

        # Keep track of affectors influencing holders directly
        # Format: {targetHolder: {affectors}}
        self.__activeDirectAffectors = KeyedSet()

        # Keep track of affectors which influence locOther, but are disabled
        # as their target location is not available
        # Format: {sourceHolder: {affectors}}
        self.__disabledDirectAffectors = KeyedSet()

    def __getAffecteeMaps(self, targetHolder):
        """
        Helper for affectee register/unregister methods.

        Positional arguments:
        targetHolder -- holder, for which affectee maps are requested

        Return value:
        List of (key, affecteeMap) tuples, where key should be used to access
        data set (appropriate to passed targetHolder) in affecteeMap
        """
        # Container which temporarily holds (key, map) tuples
        affecteeMaps = []
        location = targetHolder._location
        if location is not None:
            affecteeMaps.append((location, self.__affecteeLocation))
            group = targetHolder.item.groupId
            if group is not None:
                affecteeMaps.append(((location, group), self.__affecteeLocationGroup))
            for skill in targetHolder.item.requiredSkills:
                affecteeMaps.append(((location, skill), self.__affecteeLocationSkill))
        return affecteeMaps

    def __getAffectorMap(self, affector):
        """
        Helper for affector register/unregister methods.

        Positional arguments:
        affector -- affector, for which affector map are requested

        Return value:
        (key, affectorMap) tuple, where key should be used to access
        data set (appropriate to passed affector) in affectorMap

        Possible exceptions:
        BadContainerException -- raised if affector's info specifies filtered
        modification and target location refers self, but affector's holder
        isn't in position to be target for filtered modifications
        UnsupportedDirectLocationException -- raised when affector's info
        target location is not supported for direct modification
        UnsupportedFilteredLocationException -- raised when affector's info
        target location is not supported for filtered modification
        UnsupportedFilterException -- raised when affector's info filter type
        is not supported
        """
        sourceHolder, info = affector
        # For each filter type, define affector map and key to use
        if info.filterType is None:
            # For single item modifications, we need to properly pick
            # target holder (it's key) based on location
            if info.location == Location.self_:
                affectorMap = self.__activeDirectAffectors
                key = sourceHolder
            elif info.location == Location.character:
                char = self.__fit.character
                if char is not None:
                    affectorMap = self.__activeDirectAffectors
                    key = char
                else:
                    affectorMap = self.__disabledDirectAffectors
                    key = sourceHolder
            elif info.location == Location.ship:
                ship = self.__fit.ship
                if ship is not None:
                    affectorMap = self.__activeDirectAffectors
                    key = ship
                else:
                    affectorMap = self.__disabledDirectAffectors
                    key = sourceHolder
            # When other location is referenced, it means direct reference to module's charge
            # or to charge's module-container
            elif info.location == Location.other:
                try:
                    otherHolder = sourceHolder._other
                except AttributeError:
                    otherHolder = None
                if otherHolder is not None:
                    affectorMap = self.__activeDirectAffectors
                    key = otherHolder
                # When no reference available, it means that e.g. charge may be
                # unavailable for now; use disabled affectors map for these
                else:
                    affectorMap = self.__disabledDirectAffectors
                    key = sourceHolder
            else:
                raise UnsupportedDirectLocationException(info.location)
        # For massive modifications, compose key, making sure reference to self
        # is converted into appropriate real location
        elif info.filterType == FilterType.all_:
            affectorMap = self.__affectorLocation
            location = self.__contextizeFilterLocation(affector)
            key = location
        elif info.filterType == FilterType.group:
            affectorMap = self.__affectorLocationGroup
            location = self.__contextizeFilterLocation(affector)
            key = (location, info.filterValue)
        elif info.filterType == FilterType.skill:
            affectorMap = self.__affectorLocationSkill
            location = self.__contextizeFilterLocation(affector)
            skill = self.__contextizeSkillrqId(affector)
            key = (location, skill)
        else:
            raise UnsupportedFilterException(info.filterType)
        return key, affectorMap

    def __contextizeFilterLocation(self, affector):
        """
        Convert location self-reference to real location, like character or ship.
        Used only in modifications of multiple filtered holders, direct modifications
        are processed out of the context of this method.

        Positional arguments:
        affector -- affector, whose info refers location in question

        Return value:
        Real contextized location

        Possible exceptions:
        BadContainerException -- raised if affector's info refers self, but affector's
        holder isn't in position to be target for massive filtered modifications
        UnsupportedFilteredLocationException -- raised when affector's info
        target location is not supported for filtered modification
        """
        sourceHolder = affector.sourceHolder
        targetLocation = affector.info.location
        # Reference to self is sparingly used on ship effects, so we must convert
        # it to real location
        if targetLocation == Location.self_:
            if sourceHolder is self.__fit.ship:
                return Location.ship
            elif sourceHolder is self.__fit.character:
                return Location.character
            else:
                raise BadContainerException
        # Just return untouched location for all other valid cases
        elif targetLocation in (Location.character, Location.ship, Location.space):
            return targetLocation
        # Raise error if location is invalid
        else:
            raise UnsupportedFilteredLocationException(targetLocation)

    def __contextizeSkillrqId(self, affector):
        """
        Convert typeID self-reference into real typeID.

        Positional arguments:
        affector -- affector, whose info refers some type via ID

        Return value:
        Real typeID, taken from affector's holder carrier
        """
        skillId = affector.info.filterValue
        if skillId == InvType.self_:
            skillId = affector.sourceHolder.item.id
        return skillId

    def __enableDirectSpec(self, targetHolder, targetLocation):
        """
        Enable temporarily disabled affectors, directly targeting holder in
        specific location.

        Positional arguments:
        targetHolder -- holder which is being registered
        targetLocation -- location, to which holder is being registered
        """
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
        """
        Disable affectors, directly targeting holder in specific location.

        Positional arguments:
        targetHolder -- holder which is being unregistered
        """
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
        """
        Enable temporarily disabled affectors, directly targeting passed holder,
        originating from holder in "other" location.

        Positional arguments:
        targetHolder -- holder which is being registered
        """
        try:
            otherHolder = targetHolder._other
        except AttributeError:
            otherHolder = None
        # If passed holder doesn't have other location (charge's module
        # or module's charge), do nothing
        if otherHolder is None:
            return
        # Get all disabled affectors which should influence our targetHolder
        affectorsToEnable = set()
        for affector in self.__disabledDirectAffectors.getData(otherHolder):
            info = affector.info
            if info.location == Location.other and info.filterType is None:
                affectorsToEnable.add(affector)
        # Bail if we have nothing to do
        if len(affectorsToEnable) == 0:
            return
        # Move all of them to direct modification dictionary
        self.__activeDirectAffectors.addData(targetHolder, affectorsToEnable)
        self.__disabledDirectAffectors.rmData(otherHolder, affectorsToEnable)

    def __disableDirectOther(self, targetHolder):
        """
        Disable affectors, directly targeting passed holder, originating from
        holder in "other" location.

        Positional arguments:
        targetHolder -- holder which is being unregistered
        """
        try:
            otherHolder = targetHolder._other
        except AttributeError:
            otherHolder = None
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
        """
        Add passed target holder to register's maps, so it can be affected by
        other holders properly.

        Positional arguments:
        targetHolder -- holder to register

        Keyword arguments:
        enableDirect -- when some location specification is passed, register
        checks if there're any modifications which should directly apply to
        holder in that location (or, in case with "other" location, originate
        from holder in that location and apply to passed targetHolder) and
        enables them (default None)
        """
        for key, affecteeMap in self.__getAffecteeMaps(targetHolder):
            # Add data to map
            affecteeMap.addData(key, {targetHolder})
        # Check if we have affectors which should directly influence passed holder,
        # but are disabled
        directEnablers = {Location.ship: (self.__enableDirectSpec, (targetHolder, Location.ship), {}),
                          Location.character: (self.__enableDirectSpec, (targetHolder, Location.character), {}),
                          Location.other: (self.__enableDirectOther, (targetHolder,), {})}
        try:
            method, args, kwargs = directEnablers[enableDirect]
        except KeyError:
            pass
        else:
            method(*args, **kwargs)

    def unregisterAffectee(self, targetHolder, disableDirect=None):
        """
        Remove passed target holder from register's maps, so holders affecting
        it "know" that its modification is no longer needed.

        Positional arguments:
        targetHolder -- holder to unregister

        Keyword arguments:
        disableDirect -- when some location specification is passed, register
        checks if there're any modifications which are directly applied to
        holder in that location (or, in case with "other" location, originate
        from holder in that location and apply to passed targetHolder) and
        disables them (default None)
        """
        for key, affecteeMap in self.__getAffecteeMaps(targetHolder):
            affecteeMap.rmData(key, {targetHolder})
        # When removing holder from register, make sure to move modifiers which
        # originate from other holders and directly affect it to disabled map
        directEnablers = {Location.ship: (self.__disableDirectSpec, (targetHolder,), {}),
                          Location.character: (self.__disableDirectSpec, (targetHolder,), {}),
                          Location.other: (self.__disableDirectOther, (targetHolder,), {})}
        try:
            method, args, kwargs = directEnablers[disableDirect]
        except KeyError:
            pass
        else:
            method(*args, **kwargs)

    def registerAffector(self, affector):
        """
        Add passed affector to register's affector maps, so that new holders
        added to fit know that they should be affected by it.

        Positional arguments:
        affector -- duration affector to register
        """
        try:
            key, affectorMap = self.__getAffectorMap(affector)
            # Actually add data to map
            affectorMap.addData(key, {affector})
        except UnsupportedFilterException as e:
            msg = "malformed info on item {}: invalid filter type {}".format(affector.sourceHolder.item.id, e.args[0])
            signature = (UnsupportedFilterException, affector.sourceHolder.item.id, e.args[0])
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
        except BadContainerException:
            msg = "malformed info on item {}: invalid reference to self for filtered modification".format(affector.sourceHolder.item.id)
            signature = (BadContainerException, affector.sourceHolder.item.id)
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
        except UnsupportedDirectLocationException as e:
            msg = "malformed info on item {}: unsupported target location {} for direct modification".format(affector.sourceHolder.item.id, e.args[0])
            signature = (UnsupportedDirectLocationException, affector.sourceHolder.item.id, e.args[0])
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
        except UnsupportedFilteredLocationException as e:
            msg = "malformed info on item {}: unsupported target location {} for filtered modification".format(affector.sourceHolder.item.id, e.args[0])
            signature = (UnsupportedFilteredLocationException, affector.sourceHolder.item.id, e.args[0])
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)

    def unregisterAffector(self, affector):
        """
        Remove passed affector from register's affector maps, so that
        holders-affectees "know" that they're no longer affected by it.

        Positional arguments:
        affector -- duration affector to unregister
        """
        try:
            key, affectorMap = self.__getAffectorMap(affector)
            affectorMap.rmData(key, {affector})
        # Following block handles exceptions; all of them must be handled
        # when registering affector too, thus they won't appear in log
        # if logger's handler suppresses messages with duplicate
        # signature
        except UnsupportedFilterException as e:
            msg = "malformed info on item {}: invalid filter type {}".format(affector.sourceHolder.item.id, e.args[0])
            signature = (UnsupportedFilterException, affector.sourceHolder.item.id, e.args[0])
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
        except BadContainerException:
            msg = "malformed info on item {}: invalid reference to self for filtered modification".format(affector.sourceHolder.item.id)
            signature = (BadContainerException, affector.sourceHolder.item.id)
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
        except UnsupportedDirectLocationException as e:
            msg = "malformed info on item {}: unsupported target location {} for direct modification".format(affector.sourceHolder.item.id, e.args[0])
            signature = (UnsupportedDirectLocationException, affector.sourceHolder.item.id, e.args[0])
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
        except UnsupportedFilteredLocationException as e:
            msg = "malformed info on item {}: unsupported target location {} for filtered modification".format(affector.sourceHolder.item.id, e.args[0])
            signature = (UnsupportedFilteredLocationException, affector.sourceHolder.item.id, e.args[0])
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)

    def getAffectees(self, affector):
        """
        Get all holders influenced by passed affector.

        Positional arguments:
        affector -- affector, for which we're seeking for affectees

        Return value:
        Set with holders, being influenced by affector
        """
        sourceHolder, info = affector
        affectees = set()
        try:
            # For direct modification, make set out of single target location
            if info.filterType is None:
                if info.location == Location.self_:
                    target = {sourceHolder}
                elif info.location == Location.character:
                    char = self.__fit.character
                    target = {char} if char is not None else None
                elif info.location == Location.ship:
                    ship = self.__fit.ship
                    target = {ship} if ship is not None else None
                elif info.location == Location.other:
                    try:
                        otherHolder = sourceHolder._other
                    except AttributeError:
                        otherHolder = None
                    target = {otherHolder} if otherHolder is not None else None
                else:
                    raise UnsupportedDirectLocationException(info.location)
            # For filtered modifications, pick appropriate dictionary and get set
            # with target holders
            elif info.filterType == FilterType.all_:
                key = self.__contextizeFilterLocation(affector)
                target = self.__affecteeLocation.getData(key)
            elif info.filterType == FilterType.group:
                location = self.__contextizeFilterLocation(affector)
                key = (location, info.filterValue)
                target = self.__affecteeLocationGroup.getData(key)
            elif info.filterType == FilterType.skill:
                location = self.__contextizeFilterLocation(affector)
                skill = self.__contextizeSkillrqId(affector)
                key = (location, skill)
                target = self.__affecteeLocationSkill.getData(key)
            else:
                raise UnsupportedFilterException(info.filterType)
            # Add our set to affectees
            if target is not None:
                affectees.update(target)
        # If passed affector has already been registered and logger prefers
        # to suppress messages with duplicate signatures, following error handling
        # won't produce new log entries
        except UnsupportedFilterException as e:
            msg = "malformed info on item {}: invalid filter type {}".format(sourceHolder.item.id, e.args[0])
            signature = (UnsupportedFilterException, sourceHolder.item.id, e.args[0])
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
        except BadContainerException:
            msg = "malformed info on item {}: invalid reference to self for filtered modification".format(sourceHolder.item.id)
            signature = (BadContainerException, sourceHolder.item.id)
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
        except UnsupportedDirectLocationException as e:
            msg = "malformed info on item {}: unsupported target location {} for direct modification".format(sourceHolder.item.id, e.args[0])
            signature = (UnsupportedDirectLocationException, sourceHolder.item.id, e.args[0])
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
        except UnsupportedFilteredLocationException as e:
            msg = "malformed info on item {}: unsupported target location {} for filtered modification".format(sourceHolder.item.id, e.args[0])
            signature = (UnsupportedFilteredLocationException, sourceHolder.item.id, e.args[0])
            self.__fit._eos._logger.warning(msg, childName="attributeCalculator", signature=signature)
        return affectees

    def getAffectors(self, targetHolder):
        """
        Get all affectors, which influence passed holder.

        Positional arguments:
        targetHolder -- holder, for which we're seeking for affecting it
        affectors

        Return value:
        Set with affectors, incluencing targetHolder
        """
        affectors = set()
        # Add all affectors which directly affect it
        affectors.update(self.__activeDirectAffectors.getData(targetHolder))
        # Then all affectors which affect location of passed holder
        location = targetHolder._location
        affectors.update(self.__affectorLocation.getData(location))
        # All affectors which affect location and group of passed holder
        group = targetHolder.item.groupId
        affectors.update(self.__affectorLocationGroup.getData((location, group)))
        # Same, but for location & skill requirement of passed holder
        for skill in targetHolder.item.requiredSkills:
            affectors.update(self.__affectorLocationSkill.getData((location, skill)))
        return affectors
