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


from itertools import chain
from logging import getLogger

from eos.const.eos import ModifierTargetFilter, ModifierDomain, EosType
from eos.util.keyed_set import KeyedSet
from .exception import UnexpectedDomainError, UnknownTargetFilterError


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
        self.__fit = fit

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
        self.__affector_item_active = KeyedSet()

        # Affectors which influence something directly, but their target is not available
        # Format: {carrier item: set(affectors)}
        self.__affector_item_awaiting = KeyedSet()

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

    # Helpers for affectee getter - they find map and get data
    # from it according to passed affector
    def __affectee_getter_item_self(self, affector):
        return (affector.carrier_item,)

    def __affectee_getter_item_character(self, _):
        character = self.__fit.character
        if character is not None:
            return (character,)
        else:
            return ()

    def __affectee_getter_item_ship(self, _):
        ship = self.__fit.ship
        if ship is not None:
            return (ship,)
        else:
            return ()

    def __affectee_getter_item_other(self, affector):
        other_item = self.__get_other_linked_item(affector.carrier_item)
        if other_item is not None:
            return (other_item,)
        else:
            return ()

    __affectee_getters_item = {
        ModifierDomain.self: __affectee_getter_item_self,
        ModifierDomain.character: __affectee_getter_item_character,
        ModifierDomain.ship: __affectee_getter_item_ship,
        ModifierDomain.other: __affectee_getter_item_other
    }

    def __affectee_getter_item(self, affector):
        try:
            getter = self.__affectee_getters_item[affector.modifier.tgt_domain]
        except KeyError as e:
            raise UnexpectedDomainError(affector.modifier.tgt_domain) from e
        else:
            return getter(self, affector)

    def __affectee_getter_domain(self, affector):
        domain = self.__contextize_tgt_filter_domain(affector)
        return self.__affectee_domain.get(domain, ())

    def __affectee_getter_domain_group(self, affector):
        domain = self.__contextize_tgt_filter_domain(affector)
        group = affector.modifier.tgt_filter_extra_arg
        return self.__affectee_domain_group.get((domain, group), ())

    def __affectee_getter_domain_skillrq(self, affector):
        domain = self.__contextize_tgt_filter_domain(affector)
        skill = affector.modifier.tgt_filter_extra_arg
        if skill == EosType.current_self:
            skill = affector.carrier_item._eve_type_id
        return self.__affectee_domain_skillrq.get((domain, skill), ())

    def __affectee_getter_owner_skillrq(self, affector):
        skill = affector.modifier.tgt_filter_extra_arg
        if skill == EosType.current_self:
            skill = affector.carrier_item._eve_type_id
        return self.__affectee_owner_skillrq.get(skill, ())

    __affectee_getters = {
        ModifierTargetFilter.item: __affectee_getter_item,
        ModifierTargetFilter.domain: __affectee_getter_domain,
        ModifierTargetFilter.domain_group: __affectee_getter_domain_group,
        ModifierTargetFilter.domain_skillrq: __affectee_getter_domain_skillrq,
        ModifierTargetFilter.owner_skillrq: __affectee_getter_owner_skillrq
    }

    # Affectee processing
    def get_affectees(self, affector):
        """Get iterable with items influenced by passed affector"""
        try:
            try:
                getter = self.__affectee_getters[affector.modifier.tgt_filter]
            except KeyError as e:
                raise UnknownTargetFilterError(affector.modifier.tgt_filter) from e
            else:
                return getter(self, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
            return ()

    def register_affectee(self, target_item):
        """
        Add passed target item to register's affectee maps. We track
        affectees to efficiently update attributes when set of items
        influencing them changes.
        """
        # Add item to all affectee maps
        for key, affectee_map in self.__get_affectee_maps(target_item):
            affectee_map.add_data(key, target_item)
        # Special handling for awaitable direct item affectors. Affector
        # is awaitable only when it directly affects single target item,
        # and only when this target item is not affector's carrier item.
        # All affectors which target their own carrier are always enabled,
        # because when they're turned on - their target is always available
        self.__find_and_enable_awaitable_affectors(target_item)

    def unregister_affectee(self, target_item):
        """
        Remove passed target item from register's affectee maps,
        """
        # Remove item from all affectee maps
        for key, affectee_map in self.__get_affectee_maps(target_item):
            affectee_map.rm_data(key, target_item)
        # Special handling for awaitable direct item affectors
        self.__disable_awaitable_affectors(target_item)

    def __get_affectee_maps(self, target_item):
        """
        Return all places where passed affectee should be stored,
        in [(key, affectee map), ...] form.
        """
        affectee_maps = []
        domain = target_item._parent_modifier_domain
        if domain is not None:
            # Domain
            affectee_maps.append((domain, self.__affectee_domain))
            group = target_item._eve_type.group
            if group is not None:
                # Domain and group
                affectee_maps.append(((domain, group), self.__affectee_domain_group))
            for skill in target_item._eve_type.required_skills:
                # Domain and skill requirement
                affectee_maps.append(((domain, skill), self.__affectee_domain_skillrq))
        if target_item._owner_modifiable is True:
            for skill in target_item._eve_type.required_skills:
                # Owner-modifiable and skill requirement
                affectee_maps.append((skill, self.__affectee_owner_skillrq))
        return affectee_maps

    def __find_and_enable_awaitable_affectors(self, target_item):
        """Enable affectors which wait for passed item"""
        # Search for affectors
        other_item = self.__get_other_linked_item(target_item)
        if other_item is not None:
            affectors_to_enable = self.__find_affectors_for_tgt_other(
                chain(*self.__affector_item_awaiting.values()), other_item)
        elif target_item is self.__fit.ship:
            affectors_to_enable = self.__find_affectors_for_tgt_domain(
                chain(*self.__affector_item_awaiting.values()), ModifierDomain.ship)
        elif target_item is self.__fit.character:
            affectors_to_enable = self.__find_affectors_for_tgt_domain(
                chain(*self.__affector_item_awaiting.values()), ModifierDomain.character)
        else:
            return
        # Enable them - move from awaiting map to enabled map
        self.__affector_item_active.add_data_set(target_item, affectors_to_enable)
        for affector in affectors_to_enable:
            self.__affector_item_awaiting.rm_data(affector.carrier_item, affector)

    def __disable_awaitable_affectors(self, target_item):
        """Disable awaitable affectors which influence passed item"""
        affectors_to_disable = set()
        for affector in self.__affector_item_active.get(target_item, ()):
            # Mark them as to-be-disabled only if they are awaitable,
            # We consider all affectors which target this item and which
            # are not originating from it as awaitable
            if affector.carrier_item is not target_item:
                affectors_to_disable.add(affector)
        # Move active affectors to awaiting list
        self.__affector_item_active.rm_data_set(target_item, affectors_to_disable)
        for affector in affectors_to_disable:
            self.__affector_item_awaiting.add_data(affector.carrier_item, affector)

    def __find_affectors_for_tgt_domain(self, affectors, tgt_domain):
        """
        Take list of awaiting affectors and return only
        those which target specific domain
        """
        results = set()
        for affector in affectors:
            if affector.modifier.tgt_domain == tgt_domain:
                results.add(affector)
        return results

    def __find_affectors_for_tgt_other(self, affectors, other_item):
        """
        Take list of awaiting affectors and item which is "other"
        to the target item, and find out which affectors originate
        from "other" item and aim for target item (via "other"
        domain)
        """
        results = set()
        for affector in affectors:
            if affector.modifier.tgt_domain == ModifierDomain.other and affector.carrier_item is other_item:
                results.add(affector)
        return results

    # Affector processing
    def get_affectors(self, target_item):
        """Get all affectors, which influence passed item"""
        affectors = set()
        # Item
        affectors.update(self.__affector_item_active.get(target_item, ()))
        domain = target_item._parent_modifier_domain
        if domain is not None:
            # Domain
            affectors.update(self.__affector_domain.get(domain, ()))
            # Domain and group
            affectors.update(self.__affector_domain_group.get((domain, target_item._eve_type.group), ()))
            for skill in target_item._eve_type.required_skills:
                # Domain and skill requirement
                affectors.update(self.__affector_domain_skillrq.get((domain, skill), ()))
        if target_item._owner_modifiable is True:
            for skill in target_item._eve_type.required_skills:
                # Owner-modifiable and skill requirement
                affectors.update(self.__affector_owner_skillrq.get(skill, ()))
        return affectors

    def register_affector(self, affector):
        """
        Make register aware of the affector, thus making it
        possible for the affector to modify other items.
        """
        try:
            key, affector_map = self.__get_affector_map(affector)
            affector_map.add_data(key, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)

    def unregister_affector(self, affector):
        """
        Remove the affector from register, thus making it
        impossible for the affector to modify any other items.
        """
        try:
            key, affector_map = self.__get_affector_map(affector)
            affector_map.rm_data(key, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)

    # Helpers for affector registering/unregistering, they find
    # affector map and key to it
    def __affector_map_getter_item_self(self, affector):
        return affector.carrier_item, self.__affector_item_active

    def __affector_map_getter_item_character(self, affector):
        character = self.__fit.character
        if character is not None:
            return character, self.__affector_item_active
        else:
            return affector.carrier_item, self.__affector_item_awaiting

    def __affector_map_getter_item_ship(self, affector):
        ship = self.__fit.ship
        if ship is not None:
            return ship, self.__affector_item_active
        else:
            return affector.carrier_item, self.__affector_item_awaiting

    def __affector_map_getter_item_other(self, affector):
        other_item = self.__get_other_linked_item(affector.carrier_item)
        if other_item is not None:
            return other_item, self.__affector_item_active
        else:
            return affector.carrier_item, self.__affector_item_awaiting

    __affector_map_getters_item = {
        ModifierDomain.self: __affector_map_getter_item_self,
        ModifierDomain.character: __affector_map_getter_item_character,
        ModifierDomain.ship: __affector_map_getter_item_ship,
        ModifierDomain.other: __affector_map_getter_item_other
    }

    def __affector_map_getter_item(self, affector):
        try:
            getter = self.__affector_map_getters_item[affector.modifier.tgt_domain]
        except KeyError as e:
            raise UnexpectedDomainError(affector.modifier.tgt_domain) from e
        else:
            return getter(self, affector)

    def __affector_map_getter_domain(self, affector):
        domain = self.__contextize_tgt_filter_domain(affector)
        return domain, self.__affector_domain

    def __affector_map_getter_domain_group(self, affector):
        domain = self.__contextize_tgt_filter_domain(affector)
        group = affector.modifier.tgt_filter_extra_arg
        return (domain, group), self.__affector_domain_group

    def __affector_map_getter_domain_skillrq(self, affector):
        domain = self.__contextize_tgt_filter_domain(affector)
        skill = affector.modifier.tgt_filter_extra_arg
        if skill == EosType.current_self:
            skill = affector.carrier_item._eve_type_id
        return (domain, skill), self.__affector_domain_skillrq

    def __affector_map_getter_owner_skillrq(self, affector):
        skill = affector.modifier.tgt_filter_extra_arg
        if skill == EosType.current_self:
            skill = affector.carrier_item._eve_type_id
        return skill, self.__affector_owner_skillrq

    __affector_map_getters = {
        ModifierTargetFilter.item: __affector_map_getter_item,
        ModifierTargetFilter.domain: __affector_map_getter_domain,
        ModifierTargetFilter.domain_group: __affector_map_getter_domain_group,
        ModifierTargetFilter.domain_skillrq: __affector_map_getter_domain_skillrq,
        ModifierTargetFilter.owner_skillrq: __affector_map_getter_owner_skillrq
    }

    def __get_affector_map(self, affector):
        """
        Return place where passed affector should be stored, in
        (key, affector map) form.

        Possible exceptions:
        UnexpectedDomainError -- raised when affector's modifier target
            domain is not supported for context of passed affector
        UnknownTargetFilterError -- raised when affector's modifier filter
            type is not supported
        """
        try:
            getter = self.__affector_map_getters[affector.modifier.tgt_filter]
        except KeyError as e:
            raise UnknownTargetFilterError(affector.modifier.tgt_filter) from e
        else:
            return getter(self, affector)

    # Shared helpers
    def __contextize_tgt_filter_domain(self, affector):
        """
        Cnvert domain.self to absolute domain (such as char or ship).
        This method should be used for modifiers which have domain
        as one of the arguments for their target filter, except for
        direct item modifications, these are handled separately.

        Possible exceptions:
        UnexpectedDomainError -- raised when affector's modifier
            target domain is not supported
        """
        carrier_item = affector.carrier_item
        domain = affector.modifier.tgt_domain
        if domain == ModifierDomain.self:
            if carrier_item is self.__fit.ship:
                return ModifierDomain.ship
            elif carrier_item is self.__fit.character:
                return ModifierDomain.character
            else:
                raise UnexpectedDomainError(domain)
        # Just return untouched domain for all other valid cases. Valid cases
        # include 'globally' visible (within the fit scope) domains only.
        # I.e. if item on fit refers this target domain, it should always
        # refer the same target item regardless of source item.
        elif domain in (ModifierDomain.character, ModifierDomain.ship):
            return domain
        # Raise error if domain is invalid
        else:
            raise UnexpectedDomainError(domain)

    def __get_other_linked_item(self, item):
        """
        Attempt to get item linked via 'other' link, like charge's
        module or module's charge, return None if nothing is found.
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
        """
        if isinstance(error, UnexpectedDomainError):
            msg = 'malformed modifier on eve type {}: unsupported target domain {}'.format(
                affector.carrier_item._eve_type_id, error.args[0])
            logger.warning(msg)
        elif isinstance(error, UnknownTargetFilterError):
            msg = 'malformed modifier on eve type {}: invalid target filter {}'.format(
                affector.carrier_item._eve_type_id, error.args[0])
            logger.warning(msg)
        else:
            raise error
