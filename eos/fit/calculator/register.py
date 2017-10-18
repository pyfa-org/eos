# ==============================================================================
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
# ==============================================================================


from itertools import chain
from logging import getLogger

from eos.const.eos import EosTypeId, ModifierDomain, ModifierTargetFilter
from eos.util.keyed_storage import KeyedStorage
from .exception import UnexpectedDomainError, UnknownTargetFilterError


logger = getLogger(__name__)


class AffectionRegister:
    """Keeps track of connections between affectors and affectees.

    Deals only with affectors which have dogma modifiers. Having information
    about connections is hard requirement for efficient partial attribute
    recalculation.
    """

    def __init__(self, calc_svc):
        self.__calc_svc = calc_svc

        # All known items
        # Format: {items}
        self.__affectee = set()

        # Items belonging to certain domain
        # Format: {domain: set(target items)}
        self.__affectee_domain = KeyedStorage()

        # Items belonging to certain domain and group
        # Format: {(domain, group): set(target items)}
        self.__affectee_domain_group = KeyedStorage()

        # Items belonging to certain domain and having certain skill requirement
        # Format: {(domain, skill): set(target items)}
        self.__affectee_domain_skillrq = KeyedStorage()

        # Owner-modifiable items which have certain skill requirement
        # Format: {skill: set(target items)}
        self.__affectee_owner_skillrq = KeyedStorage()

        # Affectors influencing items directly
        # Format: {target item: set(affectors)}
        self.__affector_item_active = KeyedStorage()

        # Affectors which influence something directly, but their target is not
        # available
        # Format: {carrier item: set(affectors)}
        self.__affector_item_awaiting = KeyedStorage()

        # Affectors influencing all items belonging to certain domain
        # Format: {domain: set(affectors)}
        self.__affector_domain = KeyedStorage()

        # Affectors influencing items belonging to certain domain and group
        # Format: {(domain, group): set(affectors)}
        self.__affector_domain_group = KeyedStorage()

        # Affectors influencing items belonging to certain domain and having
        # certain skill requirement
        # Format: {(domain, skill): set(affectors)}
        self.__affector_domain_skillrq = KeyedStorage()

        # Affectors influencing owner-modifiable items which have certain skill
        # requirement
        # Format: {skill: set(affectors)}
        self.__affector_owner_skillrq = KeyedStorage()

    # Helpers for affectee getter - they find map and get data from it according
    # to passed affector
    def __affectee_getter_item_self(self, affector):
        return (affector.carrier_item,)

    def __affectee_getter_item_character(self, _):
        character = self.__calc_svc._current_char
        if character is not None:
            return (character,)
        else:
            return ()

    def __affectee_getter_item_ship(self, _):
        ship = self.__calc_svc._current_ship
        if ship is not None:
            return (ship,)
        else:
            return ()

    def __affectee_getter_item_other(self, affector):
        other_item = affector.carrier_item._other
        if other_item is not None:
            return (other_item,)
        else:
            return ()

    __affectee_getters_item = {
        ModifierDomain.self: __affectee_getter_item_self,
        ModifierDomain.character: __affectee_getter_item_character,
        ModifierDomain.ship: __affectee_getter_item_ship,
        ModifierDomain.other: __affectee_getter_item_other}

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
        if skill == EosTypeId.current_self:
            skill = affector.carrier_item._eve_type_id
        return self.__affectee_domain_skillrq.get((domain, skill), ())

    def __affectee_getter_owner_skillrq(self, affector):
        skill = affector.modifier.tgt_filter_extra_arg
        if skill == EosTypeId.current_self:
            skill = affector.carrier_item._eve_type_id
        return self.__affectee_owner_skillrq.get(skill, ())

    __affectee_getters = {
        ModifierTargetFilter.item: __affectee_getter_item,
        ModifierTargetFilter.domain: __affectee_getter_domain,
        ModifierTargetFilter.domain_group: __affectee_getter_domain_group,
        ModifierTargetFilter.domain_skillrq: __affectee_getter_domain_skillrq,
        ModifierTargetFilter.owner_skillrq: __affectee_getter_owner_skillrq}

    # Affectee processing
    def get_affectees(self, affector):
        """Get iterable with items influenced by passed affector."""
        try:
            mod_tgt_filter = affector.modifier.tgt_filter
            try:
                getter = self.__affectee_getters[mod_tgt_filter]
            except KeyError as e:
                raise UnknownTargetFilterError(mod_tgt_filter) from e
            else:
                return getter(self, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
            return ()

    def register_affectee(self, target_item):
        """Add passed target item to register's affectee containers.

        We track affectees to efficiently update attributes when set of items
        influencing them changes.
        """
        self.__affectee.add(target_item)
        for key, affectee_map in self.__get_affectee_maps(target_item):
            affectee_map.add_data_entry(key, target_item)
        # Special handling for awaitable direct item affectors. Affector is
        # awaitable only when it directly affects single target item, and only
        # when this target item is not affector's carrier item. All affectors
        # which target their own carrier are always enabled, because when they
        # are turned on - their target is always available
        self.__find_and_enable_awaitable_affectors(target_item)

    def unregister_affectee(self, target_item):
        """Remove passed target item from register's affectee containers."""
        self.__affectee.discard(target_item)
        for key, affectee_map in self.__get_affectee_maps(target_item):
            affectee_map.rm_data_entry(key, target_item)
        # Special handling for awaitable direct item affectors
        self.__disable_awaitable_affectors(target_item)

    def __get_affectee_maps(self, target_item):
        """Return all places where passed affectee should be stored.

        Returns:
            Iterable with multiple elements, where each element is tuple in
            (key, affectee map) format.
        """
        affectee_maps = []
        domain = target_item._parent_modifier_domain
        if domain is not None:
            # Domain
            affectee_maps.append((domain, self.__affectee_domain))
            group = target_item._eve_type.group
            if group is not None:
                # Domain and group
                affectee_maps.append(
                    ((domain, group), self.__affectee_domain_group))
            for skill in target_item._eve_type.required_skills:
                # Domain and skill requirement
                affectee_maps.append(
                    ((domain, skill), self.__affectee_domain_skillrq))
        if target_item._owner_modifiable is True:
            for skill in target_item._eve_type.required_skills:
                # Owner-modifiable and skill requirement
                affectee_maps.append((skill, self.__affectee_owner_skillrq))
        return affectee_maps

    def __find_and_enable_awaitable_affectors(self, target_item):
        """Enable affectors which wait for passed item."""
        # Search for affectors
        other_item = target_item._other
        if other_item is not None:
            affectors_to_enable = self.__find_affectors_for_tgt_other(
                chain(*self.__affector_item_awaiting.values()), other_item)
        elif target_item is self.__calc_svc._current_ship:
            affectors_to_enable = self.__find_affectors_for_tgt_domain(
                chain(*self.__affector_item_awaiting.values()),
                ModifierDomain.ship)
        elif target_item is self.__calc_svc._current_char:
            affectors_to_enable = self.__find_affectors_for_tgt_domain(
                chain(*self.__affector_item_awaiting.values()),
                ModifierDomain.character)
        else:
            return
        # Enable them - move from awaiting map to enabled map
        self.__affector_item_active.add_data_set(
            target_item, affectors_to_enable)
        for affector in affectors_to_enable:
            self.__affector_item_awaiting.rm_data_entry(
                affector.carrier_item, affector)

    def __disable_awaitable_affectors(self, target_item):
        """Disable awaitable affectors which influence passed item."""
        affectors_to_disable = set()
        for affector in self.__affector_item_active.get(target_item, ()):
            # Mark them as to-be-disabled only if they are awaitable. We
            # consider all affectors which target this item and which are not
            # originating from it as awaitable
            if affector.carrier_item is not target_item:
                affectors_to_disable.add(affector)
        # Move active affectors to awaiting list
        self.__affector_item_active.rm_data_set(
            target_item, affectors_to_disable)
        for affector in affectors_to_disable:
            self.__affector_item_awaiting.add_data_entry(
                affector.carrier_item, affector)

    def __find_affectors_for_tgt_domain(self, affectors, tgt_domain):
        """Find affectors with specified domain.

        Args:
            affectors: Iterable with affectors to filter from.
            tgt_domain: Domain as filter criterion for affectors.

        Returns:
            Set with affectors which have passed domain.
        """
        results = set()
        for affector in affectors:
            if affector.modifier.tgt_domain == tgt_domain:
                results.add(affector)
        return results

    def __find_affectors_for_tgt_other(self, affectors, other_item):
        """Find 'other' affectors in valid configuration.

        Proper 'other' affector for passed 'other' item means that affector
        should target 'other' domain, and affector's carrier should be
        'other' item which is passed in as argument. This item is called 'other'
        because it's 'other' to item being looked at, which happens outside of
        scope of this method.

        Args:
            affectors: Iterable with affectors to filter from..
            other_item: Domain as filter criterion for affectors.

        Returns:
            Set with valid 'other' affectors.
        """
        results = set()
        for affector in affectors:
            if (
                affector.modifier.tgt_domain == ModifierDomain.other and
                affector.carrier_item is other_item
            ):
                results.add(affector)
        return results

    # Affector processing
    def get_affectors(self, target_item):
        """Get all affectors, which influence passed item."""
        affectors = set()
        # Item
        affectors.update(self.__affector_item_active.get(target_item, ()))
        domain = target_item._parent_modifier_domain
        if domain is not None:
            # Domain
            affectors.update(self.__affector_domain.get(domain, ()))
            # Domain and group
            affectors.update(self.__affector_domain_group.get(
                (domain, target_item._eve_type.group), ()))
            for skill in target_item._eve_type.required_skills:
                # Domain and skill requirement
                affectors.update(self.__affector_domain_skillrq.get(
                    (domain, skill), ()))
        if target_item._owner_modifiable is True:
            for skill in target_item._eve_type.required_skills:
                # Owner-modifiable and skill requirement
                affectors.update(self.__affector_owner_skillrq.get(skill, ()))
        return affectors

    def register_affector(self, affector):
        """Make register aware of the affector.

        It makes it possible for the affector to modify other items.
        """
        try:
            key, affector_map = self.__get_affector_map(affector)
            affector_map.add_data_entry(key, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)

    def unregister_affector(self, affector):
        """Remove the affector from register.

        It makes it impossible for the affector to modify any other items.
        """
        try:
            key, affector_map = self.__get_affector_map(affector)
            affector_map.rm_data_entry(key, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)

    # Helpers for affector registering/unregistering, they find affector map and
    # key to it
    def __affector_map_getter_item_self(self, affector):
        return affector.carrier_item, self.__affector_item_active

    def __affector_map_getter_item_character(self, affector):
        character = self.__calc_svc._current_char
        if character is not None:
            return character, self.__affector_item_active
        else:
            return affector.carrier_item, self.__affector_item_awaiting

    def __affector_map_getter_item_ship(self, affector):
        ship = self.__calc_svc._current_ship
        if ship is not None:
            return ship, self.__affector_item_active
        else:
            return affector.carrier_item, self.__affector_item_awaiting

    def __affector_map_getter_item_other(self, affector):
        other_item = affector.carrier_item._other
        if other_item is not None and other_item in self.__affectee:
            return other_item, self.__affector_item_active
        else:
            return affector.carrier_item, self.__affector_item_awaiting

    __affector_map_getters_item = {
        ModifierDomain.self: __affector_map_getter_item_self,
        ModifierDomain.character: __affector_map_getter_item_character,
        ModifierDomain.ship: __affector_map_getter_item_ship,
        ModifierDomain.other: __affector_map_getter_item_other}

    def __affector_map_getter_item(self, affector):
        tgt_domain = affector.modifier.tgt_domain
        try:
            getter = self.__affector_map_getters_item[tgt_domain]
        except KeyError as e:
            raise UnexpectedDomainError(tgt_domain) from e
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
        if skill == EosTypeId.current_self:
            skill = affector.carrier_item._eve_type_id
        return (domain, skill), self.__affector_domain_skillrq

    def __affector_map_getter_owner_skillrq(self, affector):
        skill = affector.modifier.tgt_filter_extra_arg
        if skill == EosTypeId.current_self:
            skill = affector.carrier_item._eve_type_id
        return skill, self.__affector_owner_skillrq

    __affector_map_getters = {
        ModifierTargetFilter.item:
            __affector_map_getter_item,
        ModifierTargetFilter.domain:
            __affector_map_getter_domain,
        ModifierTargetFilter.domain_group:
            __affector_map_getter_domain_group,
        ModifierTargetFilter.domain_skillrq:
            __affector_map_getter_domain_skillrq,
        ModifierTargetFilter.owner_skillrq:
            __affector_map_getter_owner_skillrq}

    def __get_affector_map(self, affector):
        """Get place where passed affector should be stored.

        Args:
            affector: Affector, for which map is looked up.

        Returns:
            Tuple in (key, affector map) format, which defines where affector
            should be located.

        Raises:
            UnexpectedDomainError: If affector's modifier target domain is not
                supported for context of passed affector.
            UnknownTargetFilterError: If affector's modifier filter type is not
                supported.
        """
        try:
            getter = self.__affector_map_getters[affector.modifier.tgt_filter]
        except KeyError as e:
            raise UnknownTargetFilterError(affector.modifier.tgt_filter) from e
        else:
            return getter(self, affector)

    # Shared helpers
    def __contextize_tgt_filter_domain(self, affector):
        """Convert relative domain into absolute.

        Applicable only to en-masse modifications. That is, when modification
        targets multiple items in target domain. If modification targets single
        item, it should not be handled via this method.

        Raises:
            UnexpectedDomainError: If affector's modifier target domain is not
                supported.
        """
        carrier_item = affector.carrier_item
        domain = affector.modifier.tgt_domain
        if domain == ModifierDomain.self:
            if carrier_item is self.__calc_svc._current_ship:
                return ModifierDomain.ship
            elif carrier_item is self.__calc_svc._current_char:
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

    def __handle_affector_errors(self, error, affector):
        """Handles affector-related exceptions.

        Multiple register methods which get data based on passed affector raise
        similar exceptions. To handle them in consistent fashion, it is done
        from centralized place - this method. If error cannot be handled by the
        method, it is re-raised.
        """
        if isinstance(error, UnexpectedDomainError):
            msg = (
                'malformed modifier on eve type {}: '
                'unsupported target domain {}'
            ).format(affector.carrier_item._eve_type_id, error.args[0])
            logger.warning(msg)
        elif isinstance(error, UnknownTargetFilterError):
            msg = (
                'malformed modifier on eve type {}: invalid target filter {}'
            ).format(affector.carrier_item._eve_type_id, error.args[0])
            logger.warning(msg)
        else:
            raise error
