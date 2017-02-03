# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
# ===============================================================================


from logging import getLogger

from eos.const.eos import ModifierTargetFilter, ModifierDomain, EosEveTypes
from eos.util.keyed_set import KeyedSet
from .exception import DirectDomainError, FilteredDomainError, FilteredSelfReferenceError, TargetFilterError


logger = getLogger(__name__)


class AffectionRegister:
    """
    Keep track of connections between Affector objects and affectee
    items. Having this data is hard requirement for efficient partial
    attribute recalculation.

    Required arguments:
    fit -- fit, to which this register is bound to
    """

    def __init__(self, fit):
        self._fit = fit

        # Items belonging to certain domain
        # Format: {domain: set(target items)}
        self.__affectee_domain = KeyedSet()

        # Items belonging to certain domain and group
        # Format: {(domain, group): set(target items)}
        self.__affectee_domain_group = KeyedSet()

        # Items belonging to certain domain and having certain skill requirement
        # Format: {(domain, skill): set(target items)}
        self.__affectee_domain_skillrq = KeyedSet()

        # Owner-modifiable items which have certain skill requirement
        # Format: {skill: set(target items)}
        self.__affectee_owner_skillrq = KeyedSet()

        # Affectors influencing items directly
        # Format: {target item: set(affectors)}
        self.__affector_direct_active = KeyedSet()

        # Affectors which influence something directly, but their target is not available
        # Format: {carrier item: set(affectors)}
        self.__affector_direct_awaiting = KeyedSet()

        # Affectors influencing all items belonging to certain domain
        # Format: {domain: set(affectors)}
        self.__affector_domain = KeyedSet()

        # Affectors influencing items belonging to certain domain and group
        # Format: {(domain, group): set(affectors)}
        self.__affector_domain_group = KeyedSet()

        # Affectors influencing items belonging to certain domain and having certain skill requirement
        # Format: {(domain, skill): set(affectors)}
        self.__affector_domain_skillrq = KeyedSet()

        # Affectors influencing owner-modifiable items which have certain skill requirement
        # Format: {skill: set(affectors)}
        self.__affector_owner_skillrq = KeyedSet()

    # Affectee processing
    def get_affectees(self, affector):
        """
        Get all items influenced by passed affector.

        Required arguments:
        affector -- affector, for which we're seeking for affectees

        Return value:
        Set with items, being influenced by affector
        """
        modifier, carrier_item = affector
        affectees = set()
        try:
            # For direct modification, make set out of single target domain
            if modifier.tgt_filter == ModifierTargetFilter.item:
                if modifier.tgt_domain == ModifierDomain.self:
                    target = {carrier_item}
                elif modifier.tgt_domain == ModifierDomain.character:
                    char = self._fit.character
                    target = {char} if char is not None else None
                elif modifier.tgt_domain == ModifierDomain.ship:
                    ship = self._fit.ship
                    target = {ship} if ship is not None else None
                elif modifier.tgt_domain == ModifierDomain.other:
                    other_item = self.__get_other_linked_item(carrier_item)
                    target = {other_item} if other_item is not None else None
                else:
                    raise DirectDomainError(modifier.tgt_domain)
            # For filtered modifications, pick appropriate dictionary and get set
            # with target items
            elif modifier.tgt_filter == ModifierTargetFilter.domain:
                key = self.__contextize_filter_domain(affector)
                target = self.__affectee_domain.get(key) or set()
            elif modifier.tgt_filter == ModifierTargetFilter.domain_group:
                domain = self.__contextize_filter_domain(affector)
                group = modifier.tgt_filter_extra_arg
                key = (domain, group)
                target = self.__affectee_domain_group.get(key) or set()
            elif modifier.tgt_filter == ModifierTargetFilter.domain_skillrq:
                domain = self.__contextize_filter_domain(affector)
                skill = modifier.tgt_filter_extra_arg
                if skill == EosEveTypes.current_self:
                    skill = carrier_item._eve_type_id
                key = (domain, skill)
                target = self.__affectee_domain_skillrq.get(key) or set()
            elif modifier.tgt_filter == ModifierTargetFilter.owner_skillrq:
                skill = modifier.tgt_filter_extra_arg
                if skill == EosEveTypes.current_self:
                    skill = carrier_item._eve_type_id
                key = skill
                target = self.__affectee_owner_skillrq.get(key) or set()
            else:
                raise TargetFilterError(modifier.tgt_filter)
            # Add our set to affectees
            if target is not None:
                affectees.update(target)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
        return affectees

    def register_affectee(self, target_item):
        """
        Add passed target item to register's maps, so it can be affected by
        other items properly.

        Required arguments:
        target_item -- item to register
        """
        for key, affectee_map in self.__get_affectee_maps(target_item):
            # Add data to map
            affectee_map.add_data(key, target_item)
        # Check if we have affectors which should directly influence passed item,
        # but are disabled; enable them if there're any
        enable_direct = self.__get_item_direct_domain(target_item)
        if enable_direct is None:
            return
        if enable_direct == ModifierDomain.other:
            self.__enable_direct_other(target_item)
        elif enable_direct in (ModifierDomain.character, ModifierDomain.ship):
            self.__enable_direct_spec(target_item, enable_direct)

    def unregister_affectee(self, target_item):
        """
        Remove passed target item from register's maps, so items affecting
        it "know" that its modification is no longer needed.

        Required arguments:
        target_item -- item to unregister
        """
        for key, affectee_map in self.__get_affectee_maps(target_item):
            affectee_map.rm_data(key, target_item)
        # When removing item from register, make sure to move modifiers which
        # originate from 'other' items and directly affect it to disabled map
        disable_direct = self.__get_item_direct_domain(target_item)
        if disable_direct is None:
            return
        if disable_direct == ModifierDomain.other:
            self.__disable_direct_other(target_item)
        elif disable_direct in (ModifierDomain.character, ModifierDomain.ship):
            self.__disable_direct_spec(target_item)

    def __get_affectee_maps(self, target_item):
        """
        Helper for affectee register/unregister methods.

        Required arguments:
        target_item -- item, for which affectee maps are requested

        Return value:
        List of (key, affecteeMap) tuples, where key should be used to access
        data set (appropriate to passed target_item) in affecteeMap
        """
        # Container which temporarily holds (key, map) tuples
        affectee_maps = []
        domain = target_item._parent_modifier_domain
        if domain is not None:
            affectee_maps.append((domain, self.__affectee_domain))
            group = target_item._eve_type.group
            if group is not None:
                affectee_maps.append(((domain, group), self.__affectee_domain_group))
            for skill in target_item._eve_type.required_skills:
                affectee_maps.append(((domain, skill), self.__affectee_domain_skillrq))
        if target_item._owner_modifiable:
            for skill in target_item._eve_type.required_skills:
                affectee_maps.append((skill, self.__affectee_owner_skillrq))
        return affectee_maps

    def __enable_direct_spec(self, target_item, domain):
        """
        Enable temporarily disabled affectors, directly targeting item in
        specific domain.

        Required arguments:
        target_item -- item which is being registered
        domain -- domain, to which item is being registered
        """
        # Format: {carrier item: [affectors]}
        affectors_to_enable = {}
        # Cycle through all disabled direct affectors
        for carrier_item, affector_set in self.__affector_direct_awaiting.items():
            for affector in affector_set:
                modifier = affector.modifier
                # Mark affector as to-be-enabled only when it
                # targets passed target domain
                if modifier.tgt_domain == domain:
                    affectors = affectors_to_enable.setdefault(carrier_item, [])
                    affectors.append(affector)
        # Bail if we have nothing to do
        if not affectors_to_enable:
            return
        # Move all of them to direct modification dictionary
        for carrier_item, affectors in affectors_to_enable.items():
            self.__affector_direct_awaiting.rm_data_set(carrier_item, affectors)
            self.__affector_direct_active.add_data_set(target_item, affectors)

    def __disable_direct_spec(self, target_item):
        """
        Disable affectors, directly targeting item in specific domain.

        Required arguments:
        target_item -- item which is being unregistered
        """
        # Format: {carrier item: [affectors]}
        affectors_to_disable = {}
        # Check all affectors, targeting passed item
        for affector in self.__affector_direct_active.get(target_item) or ():
            # Mark them as to-be-disabled only if they originate from
            # other item, else they should be removed with passed item
            if affector.carrier_item is not target_item:
                affectors = affectors_to_disable.setdefault(affector.carrier_item, [])
                affectors.append(affector)
        if not affectors_to_disable:
            return
        # Move data from map to map
        for carrier_item, affectors in affectors_to_disable.items():
            self.__affector_direct_active.rm_data_set(target_item, affectors)
            self.__affector_direct_awaiting.add_data_set(carrier_item, affectors)

    def __get_item_direct_domain(self, item):
        """
        Get domain which you need to target to apply
        direct modification to passed item.

        Required arguments:
        item -- item in question

        Return value:
        Domain specification, if item can be targeted directly
        from the outside, or None if it can't
        """
        # For ship and character it's easy, we're just picking
        # corresponding domain
        if item is self._fit.ship:
            domain = ModifierDomain.ship
        elif item is self._fit.character:
            domain = ModifierDomain.character
        # For "other" domain, we should've checked for presence
        # of other entity - charge's container or module's charge
        elif self.__get_other_linked_item(item) is not None:
            domain = ModifierDomain.other
        else:
            domain = None
        return domain

    def __enable_direct_other(self, target_item):
        """
        Enable temporarily disabled affectors, directly targeting passed item,
        originating from item in "other" domain.

        Required arguments:
        target_item -- item which is being registered
        """
        other_item = self.__get_other_linked_item(target_item)
        # If passed item doesn't have other domain (charge's module
        # or module's charge), do nothing
        if other_item is None:
            return
        # Get all disabled affectors which should influence our target_item
        affectors_to_enable = set()
        for affector in self.__affector_direct_awaiting.get(other_item) or ():
            modifier = affector.modifier
            if modifier.tgt_domain == ModifierDomain.other:
                affectors_to_enable.add(affector)
        # Bail if we have nothing to do
        if not affectors_to_enable:
            return
        # Move all of them to direct modification dictionary
        self.__affector_direct_active.add_data_set(target_item, affectors_to_enable)
        self.__affector_direct_awaiting.rm_data_set(other_item, affectors_to_enable)

    def __disable_direct_other(self, target_item):
        """
        Disable affectors, directly targeting passed item, originating from
        item in "other" domain.

        Required arguments:
        target_item -- item which is being unregistered
        """
        other_item = self.__get_other_linked_item(target_item)
        if other_item is None:
            return
        affectors_to_disable = set()
        # Go through all affectors influencing item being unregistered
        for affector in self.__affector_direct_active.get(target_item) or ():
            # If affector originates from other_item, mark it as
            # to-be-disabled
            if affector.carrier_item is other_item:
                affectors_to_disable.add(affector)
        # Do nothing if we have no such affectors
        if not affectors_to_disable:
            return
        # If we have, move them from map to map
        self.__affector_direct_awaiting.add_data_set(other_item, affectors_to_disable)
        self.__affector_direct_active.rm_data_set(target_item, affectors_to_disable)

    # Affector processing
    def get_affectors(self, target_item):
        """Get all affectors, which influence passed item"""
        affectors = set()
        # Item
        affectors.update(self.__affector_direct_active.get(target_item, ()))
        # Domain
        domain = target_item._parent_modifier_domain
        affectors.update(self.__affector_domain.get(domain, ()))
        # Domain and group
        affectors.update(self.__affector_domain_group.get((domain, target_item._eve_type.group), ()))
        for skill in target_item._eve_type.required_skills:
            # Domain and skill requirement
            affectors.update(self.__affector_domain_skillrq.get((domain, skill), ()))
            # Owner-modifiable and skill requirement
            if target_item._owner_modifiable is True:
                affectors.update(self.__affector_owner_skillrq.get(skill, ()))
        return affectors

    def register_affector(self, affector):
        """
        Make register aware of the affector, thus making it
        possible for the affector to modify other items.
        """
        try:
            key, affector_map = self._get_affector_map(affector)
            affector_map.add_data(key, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)

    def unregister_affector(self, affector):
        """
        Remove the affector from register, thus making it
        impossible for the affector to modify any other items.
        """
        try:
            key, affector_map = self._get_affector_map(affector)
            affector_map.rm_data(key, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)

    # Methods which select proper affector map and key to it
    def _affector_map_getter_item_self(self, affector):
        return affector.carrier_item, self.__affector_direct_active

    def _affector_map_getter_item_character(self, affector):
        character = self._fit.character
        if character is not None:
            return character, self.__affector_direct_active
        else:
            return affector.carrier_item, self.__affector_direct_awaiting

    def _affector_map_getter_item_ship(self, affector):
        ship = self._fit.ship
        if ship is not None:
            return ship, self.__affector_direct_active
        else:
            return affector.carrier_item, self.__affector_direct_awaiting

    def _affector_map_getter_item_other(self, affector):
        other_item = self.__get_other_linked_item(affector.carrier_item)
        if other_item is not None:
            return other_item, self.__affector_direct_active
        else:
            return affector.carrier_item, self.__affector_direct_awaiting

    _affector_map_getters_item = {
        ModifierDomain.self: _affector_map_getter_item_self,
        ModifierDomain.character: _affector_map_getter_item_character,
        ModifierDomain.ship: _affector_map_getter_item_ship,
        ModifierDomain.other: _affector_map_getter_item_other
    }

    def _affector_map_getter_item(self, affector):
        try:
            getter = self._affector_map_getters_item[affector.modifier.tgt_domain]
        except KeyError as e:
            raise DirectDomainError(affector.modifier.tgt_domain) from e
        else:
            return getter(self, affector)

    def _affector_map_getter_domain(self, affector):
        domain = self.__contextize_filter_domain(affector)
        return domain, self.__affector_domain

    def _affector_map_getter_domain_group(self, affector):
        domain = self.__contextize_filter_domain(affector)
        group = affector.modifier.tgt_filter_extra_arg
        return (domain, group), self.__affector_domain_group

    def _affector_map_getter_domain_skillrq(self, affector):
        domain = self.__contextize_filter_domain(affector)
        skill = affector.modifier.tgt_filter_extra_arg
        if skill == EosEveTypes.current_self:
            skill = affector.carrier_item._eve_type_id
        return (domain, skill), self.__affector_domain_skillrq

    def _affector_map_getter_owner_skillrq(self, affector):
        skill = affector.modifier.tgt_filter_extra_arg
        if skill == EosEveTypes.current_self:
            skill = affector.carrier_item._eve_type_id
        return skill, self.__affector_owner_skillrq

    _affector_map_getters = {
        ModifierTargetFilter.item: _affector_map_getter_item,
        ModifierTargetFilter.domain: _affector_map_getter_domain,
        ModifierTargetFilter.domain_group: _affector_map_getter_domain_group,
        ModifierTargetFilter.domain_skillrq: _affector_map_getter_domain_skillrq,
        ModifierTargetFilter.owner_skillrq: _affector_map_getter_owner_skillrq
    }

    def _get_affector_map(self, affector):
        """
        Helper for affector register/unregister methods.

        Required arguments:
        affector -- affector, for which affector map are requested

        Return value:
        (key, affector_map) tuple, where key should be used to access
        data set (appropriate to passed affector) in affector_map

        Possible exceptions:
        FilteredSelfReferenceError -- raised if affector's modifier specifies
        filtered modification and target domain refers self, but affector's
        item isn't in position to be target for filtered modifications
        DirectDomainError -- raised when affector's modifier target
        domain is not supported for direct modification
        FilteredDomainError -- raised when affector's modifier target
        domain is not supported for filtered modification
        TargetFilterError -- raised when affector's modifier filter type is not
        supported
        """
        try:
            getter = self._affector_map_getters[affector.modifier.tgt_filter]
        except KeyError as e:
            raise TargetFilterError(affector.modifier.tgt_filter) from e
        else:
            return getter(self, affector)

    # Shared helpers
    def __contextize_filter_domain(self, affector):
        """
        Convert domain self-reference to real domain, like
        character or ship. Used only in modifications of multiple
        filtered items, direct modifications are processed out
        of the context of this method.

        Required arguments:
        affector -- affector, whose modifier refers domain in question

        Return value:
        Real contextized domain

        Possible exceptions:
        FilteredSelfReferenceError -- raised if affector's modifier
        refers self, but affector's item isn't in position to be
        target for filtered modifications
        FilteredDomainError -- raised when affector's modifier
        target domain is not supported for filtered modification
        """
        carrier_item = affector.carrier_item
        domain = affector.modifier.tgt_domain
        # Reference to self is sparingly used in ship effects, so we must convert
        # it to real domain
        if domain == ModifierDomain.self:
            if carrier_item is self._fit.ship:
                return ModifierDomain.ship
            elif carrier_item is self._fit.character:
                return ModifierDomain.character
            else:
                raise FilteredSelfReferenceError
        # Just return untouched domain for all other valid cases
        elif domain in (ModifierDomain.character, ModifierDomain.ship):
            return domain
        # Raise error if domain is invalid
        else:
            raise FilteredDomainError(domain)

    def __get_other_linked_item(self, item):
        """
        Attempt to get item linked via 'other' link,
        like charge's module or module's charge, return
        None if nothing is found.
        """
        if hasattr(item, 'charge'):
            return item.charge
        elif hasattr(item, 'container'):
            return item.container
        else:
            return None

    def __handle_affector_errors(self, error, affector):
        """
        Multiple register methods which get data based on passed affector
        raise similar exception classes. To handle them in consistent fashion,
        it is done from centralized place - this method. If error cannot be
        handled by method, it is re-raised.

        Required arguments:
        error -- Exception instance which was caught and needs to be handled
        affector -- affector object, which was being processed when error occurred
        """
        if isinstance(error, DirectDomainError):
            msg = 'malformed modifier on eve type {}: unsupported target domain {} for direct modification'.format(
                affector.carrier_item._eve_type_id, error.args[0])
            logger.warning(msg)
        elif isinstance(error, FilteredDomainError):
            msg = 'malformed modifier on eve type {}: unsupported target domain {} for filtered modification'.format(
                affector.carrier_item._eve_type_id, error.args[0])
            logger.warning(msg)
        elif isinstance(error, FilteredSelfReferenceError):
            msg = 'malformed modifier on eve type {}: invalid reference to self for filtered modification'.format(
                affector.carrier_item._eve_type_id)
            logger.warning(msg)
        elif isinstance(error, TargetFilterError):
            msg = 'malformed modifier on eve type {}: invalid target filter {}'.format(
                affector.carrier_item._eve_type_id, error.args[0])
            logger.warning(msg)
        else:
            raise error
