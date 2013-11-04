#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


from eos.const.eos import Location, FilterType
from eos.util.keyed_set import KeyedSet
from .exception import DirectLocationError, FilteredLocationError, FilteredSelfReferenceError, FilterTypeError


class LinkRegister:
    """
    Keep track of currently existing links between affectors
    (Affector objects) and affectees (holders). This is hard
    requirement for efficient partial attribute recalculation.
    Register is not aware of links between specific attributes,
    doesn't know anything about states and contexts, just
    affectors and affectees.

    Positional arguments:
    fit -- fit, to which this register is bound to
    """

    def __init__(self, fit):
        # Link tracker which is assigned to fit we're
        # keeping data for
        self._fit = fit

        # Keep track of holders belonging to certain location
        # Format: {location: {targetHolders}}
        self.__affectee_location = KeyedSet()

        # Keep track of holders belonging to certain location and group
        # Format: {(location, group): {targetHolders}}
        self.__affectee_location_group = KeyedSet()

        # Keep track of holders belonging to certain location and having certain skill requirement
        # Format: {(location, skill): {targetHolders}}
        self.__affectee_location_skill = KeyedSet()

        # Keep track of affectors influencing all holders belonging to certain location
        # Format: {location: {affectors}}
        self.__affector_location = KeyedSet()

        # Keep track of affectors influencing holders belonging to certain location and group
        # Format: {(location, group): {affectors}}
        self.__affector_location_group = KeyedSet()

        # Keep track of affectors influencing holders belonging to certain location and having certain skill requirement
        # Format: {(location, skill): {affectors}}
        self.__affector_location_skill = KeyedSet()

        # Keep track of affectors influencing holders directly
        # Format: {targetHolder: {affectors}}
        self.__active_direct_affectors = KeyedSet()

        # Keep track of affectors which influence something directly,
        # but are disabled as their target location is not available
        # Format: {source_holder: {affectors}}
        self.__disabled_direct_affectors = KeyedSet()

    def register_affectee(self, target_holder):
        """
        Add passed target holder to register's maps, so it can be affected by
        other holders properly.

        Positional arguments:
        target_holder -- holder to register
        """
        for key, affectee_map in self.__get_affectee_maps(target_holder):
            # Add data to map
            affectee_map.add_data(key, target_holder)
        # Check if we have affectors which should directly influence passed holder,
        # but are disabled; enable them if there're any
        enable_direct = self.__get_holder_direct_location(target_holder)
        if enable_direct is None:
            return
        if enable_direct == Location.other:
            self.__enable_direct_other(target_holder)
        elif enable_direct in (Location.character, Location.ship):
            self.__enable_direct_spec(target_holder, enable_direct)

    def unregister_affectee(self, target_holder):
        """
        Remove passed target holder from register's maps, so holders affecting
        it "know" that its modification is no longer needed.

        Positional arguments:
        target_holder -- holder to unregister
        """
        for key, affectee_map in self.__get_affectee_maps(target_holder):
            affectee_map.rm_data(key, target_holder)
        # When removing holder from register, make sure to move modifiers which
        # originate from 'other' holders and directly affect it to disabled map
        disable_direct = self.__get_holder_direct_location(target_holder)
        if disable_direct is None:
            return
        if disable_direct == Location.other:
            self.__disable_direct_other(target_holder)
        elif disable_direct in (Location.character, Location.ship):
            self.__disable_direct_spec(target_holder)

    def register_affector(self, affector):
        """
        Add passed affector to register's affector maps, so that new holders
        added to fit know that they should be affected by it.

        Positional arguments:
        affector -- affector to register
        """
        try:
            key, affector_map = self.__get_affector_map(affector)
            # Actually add data to map
            affector_map.add_data(key, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)

    def unregister_affector(self, affector):
        """
        Remove passed affector from register's affector maps, so that
        holders-affectees "know" that they're no longer affected by it.

        Positional arguments:
        affector -- affector to unregister
        """
        try:
            key, affector_map = self.__get_affector_map(affector)
            affector_map.rm_data(key, affector)
        # Following block handles exceptions; all of them must be handled
        # when registering affector too, thus they won't appear in log
        # if logger's handler suppresses messages with duplicate
        # signature
        except Exception as e:
            self.__handle_affector_errors(e, affector)

    def get_affectees(self, affector):
        """
        Get all holders influenced by passed affector.

        Positional arguments:
        affector -- affector, for which we're seeking for affectees

        Return value:
        Set with holders, being influenced by affector
        """
        source_holder, modifier = affector
        affectees = set()
        try:
            # For direct modification, make set out of single target location
            if modifier.filter_type is None:
                if modifier.location == Location.self_:
                    target = {source_holder}
                elif modifier.location == Location.character:
                    char = self._fit.character
                    target = {char} if char is not None else None
                elif modifier.location == Location.ship:
                    ship = self._fit.ship
                    target = {ship} if ship is not None else None
                elif modifier.location == Location.other:
                    other_holder = self.__get_other_linked_holder(source_holder)
                    target = {other_holder} if other_holder is not None else None
                else:
                    raise DirectLocationError(modifier.location)
            # For filtered modifications, pick appropriate dictionary and get set
            # with target holders
            elif modifier.filter_type == FilterType.all_:
                key = self.__contextize_filter_location(affector)
                target = self.__affectee_location.get(key) or set()
            elif modifier.filter_type == FilterType.group:
                location = self.__contextize_filter_location(affector)
                key = (location, modifier.filter_value)
                target = self.__affectee_location_group.get(key) or set()
            elif modifier.filter_type == FilterType.skill:
                location = self.__contextize_filter_location(affector)
                skill = affector.modifier.filter_value
                key = (location, skill)
                target = self.__affectee_location_skill.get(key) or set()
            elif modifier.filter_type == FilterType.skill_self:
                location = self.__contextize_filter_location(affector)
                skill = affector.source_holder.item.id
                key = (location, skill)
                target = self.__affectee_location_skill.get(key) or set()
            else:
                raise FilterTypeError(modifier.filter_type)
            # Add our set to affectees
            if target is not None:
                affectees.update(target)
        # If passed affector has already been registered and logger prefers
        # to suppress messages with duplicate signatures, following error handling
        # won't produce new log entries
        except Exception as e:
            self.__handle_affector_errors(e, affector)
        return affectees

    def get_affectors(self, target_holder):
        """
        Get all affectors, which influence passed holder.

        Positional arguments:
        target_holder -- holder, for which we're seeking for affecting it
        affectors

        Return value:
        Set with affectors, incluencing target_holder
        """
        affectors = set()
        # Add all affectors which directly affect it
        affectors.update(self.__active_direct_affectors.get(target_holder) or set())
        # Then all affectors which affect location of passed holder
        location = target_holder._location
        affectors.update(self.__affector_location.get(location) or set())
        # All affectors which affect location and group of passed holder
        group = target_holder.item.group_id
        affectors.update(self.__affector_location_group.get((location, group)) or set())
        # Same, but for location & skill requirement of passed holder
        for skill in target_holder.item.required_skills:
            affectors.update(self.__affector_location_skill.get((location, skill)) or set())
        return affectors

    # General-purpose auxiliary methods
    def __get_affectee_maps(self, target_holder):
        """
        Helper for affectee register/unregister methods.

        Positional arguments:
        target_holder -- holder, for which affectee maps are requested

        Return value:
        List of (key, affecteeMap) tuples, where key should be used to access
        data set (appropriate to passed target_holder) in affecteeMap
        """
        # Container which temporarily holds (key, map) tuples
        affectee_maps = []
        location = target_holder._location
        if location is not None:
            affectee_maps.append((location, self.__affectee_location))
            group = target_holder.item.group_id
            if group is not None:
                affectee_maps.append(((location, group), self.__affectee_location_group))
            for skill in target_holder.item.required_skills:
                affectee_maps.append(((location, skill), self.__affectee_location_skill))
        return affectee_maps

    def __get_affector_map(self, affector):
        """
        Helper for affector register/unregister methods.

        Positional arguments:
        affector -- affector, for which affector map are requested

        Return value:
        (key, affector_map) tuple, where key should be used to access
        data set (appropriate to passed affector) in affector_map

        Possible exceptions:
        FilteredSelfReferenceError -- raised if affector's modifier specifies
        filtered modification and target location refers self, but affector's
        holder isn't in position to be target for filtered modifications
        DirectLocationError -- raised when affector's modifier target
        location is not supported for direct modification
        FilteredLocationError -- raised when affector's modifier target
        location is not supported for filtered modification
        FilterTypeError -- raised when affector's modifier filter type is not
        supported
        """
        source_holder, modifier = affector
        # For each filter type, define affector map and key to use
        if modifier.filter_type is None:
            # For direct modifications, we need to properly pick
            # target holder (it's key) based on location
            if modifier.location == Location.self_:
                affector_map = self.__active_direct_affectors
                key = source_holder
            elif modifier.location == Location.character:
                char = self._fit.character
                if char is not None:
                    affector_map = self.__active_direct_affectors
                    key = char
                else:
                    affector_map = self.__disabled_direct_affectors
                    key = source_holder
            elif modifier.location == Location.ship:
                ship = self._fit.ship
                if ship is not None:
                    affector_map = self.__active_direct_affectors
                    key = ship
                else:
                    affector_map = self.__disabled_direct_affectors
                    key = source_holder
            # When other location is referenced, it means direct reference to module's charge
            # or to charge's module-container
            elif modifier.location == Location.other:
                other_holder = self.__get_other_linked_holder(source_holder)
                if other_holder is not None:
                    affector_map = self.__active_direct_affectors
                    key = other_holder
                # When no reference available, it means that e.g. charge may be
                # unavailable for now; use disabled affectors map for these
                else:
                    affector_map = self.__disabled_direct_affectors
                    key = source_holder
            else:
                raise DirectLocationError(modifier.location)
        # For filtered modifications, compose key, making sure reference to self
        # is converted into appropriate real location
        elif modifier.filter_type == FilterType.all_:
            affector_map = self.__affector_location
            location = self.__contextize_filter_location(affector)
            key = location
        elif modifier.filter_type == FilterType.group:
            affector_map = self.__affector_location_group
            location = self.__contextize_filter_location(affector)
            key = (location, modifier.filter_value)
        elif modifier.filter_type == FilterType.skill:
            affector_map = self.__affector_location_skill
            location = self.__contextize_filter_location(affector)
            skill = affector.modifier.filter_value
            key = (location, skill)
        elif modifier.filter_type == FilterType.skill_self:
            affector_map = self.__affector_location_skill
            location = self.__contextize_filter_location(affector)
            skill = affector.source_holder.item.id
            key = (location, skill)
        else:
            raise FilterTypeError(modifier.filter_type)
        return key, affector_map

    def __handle_affector_errors(self, error, affector):
        """
        Multiple register methods which get data based on passed affector
        raise similar exception classes. To handle them in consistent fashion,
        it is done from centralized place - this method. If error cannot be
        handled by method, it is re-raised.

        Positional arguments:
        error -- Exception instance which was caught and needs to be handled
        affector -- affector object, which was being processed when error occurred
        """
        if isinstance(error, DirectLocationError):
            msg = 'malformed modifier on item {}: unsupported target location {} for direct modification'.format(
                affector.source_holder.item.id, error.args[0])
            signature = (type(error), affector.source_holder.item.id, error.args[0])
            self._fit.eos._logger.warning(msg, child_name='attribute_calculator', signature=signature)
        elif isinstance(error, FilteredLocationError):
            msg = 'malformed modifier on item {}: unsupported target location {} for filtered modification'.format(
                affector.source_holder.item.id, error.args[0])
            signature = (type(error), affector.source_holder.item.id, error.args[0])
            self._fit.eos._logger.warning(msg, child_name='attribute_calculator', signature=signature)
        elif isinstance(error, FilteredSelfReferenceError):
            msg = 'malformed modifier on item {}: invalid reference to self for filtered modification'.format(
                affector.source_holder.item.id)
            signature = (type(error), affector.source_holder.item.id)
            self._fit.eos._logger.warning(msg, child_name='attribute_calculator', signature=signature)
        elif isinstance(error, FilterTypeError):
            msg = 'malformed modifier on item {}: invalid filter type {}'.format(
                affector.source_holder.item.id, error.args[0])
            signature = (type(error), affector.source_holder.item.id, error.args[0])
            self._fit.eos._logger.warning(msg, child_name='attribute_calculator', signature=signature)
        else:
            raise error

    # Methods which help to process filtered modifications
    def __contextize_filter_location(self, affector):
        """
        Convert location self-reference to real location, like
        character or ship. Used only in modifications of multiple
        filtered holders, direct modifications are processed out
        of the context of this method.

        Positional arguments:
        affector -- affector, whose modifier refers location in question

        Return value:
        Real contextized location

        Possible exceptions:
        FilteredSelfReferenceError -- raised if affector's modifier
        refers self, but affector's holder isn't in position to be
        target for filtered modifications
        FilteredLocationError -- raised when affector's modifier
        target location is not supported for filtered modification
        """
        source_holder = affector.source_holder
        target_location = affector.modifier.location
        # Reference to self is sparingly used in ship effects, so we must convert
        # it to real location
        if target_location == Location.self_:
            if source_holder is self._fit.ship:
                return Location.ship
            elif source_holder is self._fit.character:
                return Location.character
            else:
                raise FilteredSelfReferenceError
        # Just return untouched location for all other valid cases
        elif target_location in (Location.character, Location.ship, Location.space):
            return target_location
        # Raise error if location is invalid
        else:
            raise FilteredLocationError(target_location)

    # Methods which help to process direct modifications
    def __get_holder_direct_location(self, holder):
        """
        Get location which you need to target to apply
        direct modification to passed holder.

        Positional arguments:
        holder -- holder in question

        Return value:
        Location specification, if holder can be targeted directly
        from the outside, or None if it can't
        """
        # For ship and character it's easy, we're just picking
        # corresponding location
        if holder is self._fit.ship:
            location = Location.ship
        elif holder is self._fit.character:
            location = Location.character
        # For "other" location, we should've checked for presence
        # of other entity - charge's container or module's charge
        elif self.__get_other_linked_holder(holder) is not None:
            location = Location.other
        else:
            location = None
        return location

    def __enable_direct_spec(self, target_holder, target_location):
        """
        Enable temporarily disabled affectors, directly targeting holder in
        specific location.

        Positional arguments:
        target_holder -- holder which is being registered
        target_location -- location, to which holder is being registered
        """
        # Format: {source_holder: [affectors]}
        affectors_to_enable = {}
        # Cycle through all disabled direct affectors
        for source_holder, affector_set in self.__disabled_direct_affectors.items():
            for affector in affector_set:
                modifier = affector.modifier
                # Mark affector as to-be-enabled only when it
                # targets passed target location
                if modifier.location == target_location:
                    source_affectors = affectors_to_enable.setdefault(source_holder, [])
                    source_affectors.append(affector)
        # Bail if we have nothing to do
        if not affectors_to_enable:
            return
        # Move all of them to direct modification dictionary
        for source_holder, affectors in affectors_to_enable.items():
            self.__disabled_direct_affectors.rm_data_set(source_holder, affectors)
            self.__active_direct_affectors.add_data_set(target_holder, affectors)

    def __disable_direct_spec(self, target_holder):
        """
        Disable affectors, directly targeting holder in specific location.

        Positional arguments:
        target_holder -- holder which is being unregistered
        """
        # Format: {source_holder: [affectors]}
        affectors_to_disable = {}
        # Check all affectors, targeting passed holder
        for affector in self.__active_direct_affectors.get(target_holder) or ():
            # Mark them as to-be-disabled only if they originate from
            # other holder, else they should be removed with passed holder
            if affector.source_holder is not target_holder:
                source_affectors = affectors_to_disable.setdefault(affector.source_holder, [])
                source_affectors.append(affector)
        if not affectors_to_disable:
            return
        # Move data from map to map
        for source_holder, affectors in affectors_to_disable.items():
            self.__active_direct_affectors.rm_data_set(target_holder, affectors)
            self.__disabled_direct_affectors.add_data_set(source_holder, affectors)

    def __enable_direct_other(self, target_holder):
        """
        Enable temporarily disabled affectors, directly targeting passed holder,
        originating from holder in "other" location.

        Positional arguments:
        target_holder -- holder which is being registered
        """
        other_holder = self.__get_other_linked_holder(target_holder)
        # If passed holder doesn't have other location (charge's module
        # or module's charge), do nothing
        if other_holder is None:
            return
        # Get all disabled affectors which should influence our target_holder
        affectors_to_enable = set()
        for affector in self.__disabled_direct_affectors.get(other_holder) or ():
            modifier = affector.modifier
            if modifier.location == Location.other:
                affectors_to_enable.add(affector)
        # Bail if we have nothing to do
        if not affectors_to_enable:
            return
        # Move all of them to direct modification dictionary
        self.__active_direct_affectors.add_data_set(target_holder, affectors_to_enable)
        self.__disabled_direct_affectors.rm_data_set(other_holder, affectors_to_enable)

    def __disable_direct_other(self, target_holder):
        """
        Disable affectors, directly targeting passed holder, originating from
        holder in "other" location.

        Positional arguments:
        target_holder -- holder which is being unregistered
        """
        other_holder = self.__get_other_linked_holder(target_holder)
        if other_holder is None:
            return
        affectors_to_disable = set()
        # Go through all affectors influencing holder being unregistered
        for affector in self.__active_direct_affectors.get(target_holder) or ():
            # If affector originates from other_holder, mark it as
            # to-be-disabled
            if affector.source_holder is other_holder:
                affectors_to_disable.add(affector)
        # Do nothing if we have no such affectors
        if not affectors_to_disable:
            return
        # If we have, move them from map to map
        self.__disabled_direct_affectors.add_data_set(other_holder, affectors_to_disable)
        self.__active_direct_affectors.rm_data_set(target_holder, affectors_to_disable)

    def __get_other_linked_holder(self, holder):
        """
        Attempt to get holder linked via 'other' link,
        like charge's module or module's charge, return
        None if nothing is found.
        """
        if hasattr(holder, 'charge'):
            return holder.charge
        elif hasattr(holder, 'container'):
            return holder.container
        else:
            return None
