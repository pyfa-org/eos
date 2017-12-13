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

from eos.const.eos import EosTypeId
from eos.const.eos import ModDomain
from eos.const.eos import ModTgtFilter
from eos.util.keyed_storage import KeyedStorage
from .exception import UnexpectedDomainError
from .exception import UnknownTgtFilterError


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
        # Format: {(domain, group ID): set(target items)}
        self.__affectee_domain_group = KeyedStorage()

        # Items belonging to certain domain and having certain skill requirement
        # Format: {(domain, skill type ID): set(target items)}
        self.__affectee_domain_skillrq = KeyedStorage()

        # Owner-modifiable items which have certain skill requirement
        # Format: {skill type ID: set(target items)}
        self.__affectee_owner_skillrq = KeyedStorage()

        # Affectors influencing items directly
        # Format: {carrier item: set(affectors)}
        self.__affector_item = KeyedStorage()

        # Affectors influencing items directly on a per-target basis
        # Format: {target item: set(affectors)}
        self.__affector_item_active = KeyedStorage()

        # Affectors influencing all items belonging to certain domain
        # Format: {domain: set(affectors)}
        self.__affector_domain = KeyedStorage()

        # Affectors influencing items belonging to certain domain and group
        # Format: {(domain, group ID): set(affectors)}
        self.__affector_domain_group = KeyedStorage()

        # Affectors influencing items belonging to certain domain and having
        # certain skill requirement
        # Format: {(domain, skill type ID): set(affectors)}
        self.__affector_domain_skillrq = KeyedStorage()

        # Affectors influencing owner-modifiable items which have certain skill
        # requirement
        # Format: {skill type ID: set(affectors)}
        self.__affector_owner_skillrq = KeyedStorage()

    # Helpers for affectee getter - they find map and get data from it according
    # to passed affector
    def __affectee_getter_item_self(self, affector):
        return affector.carrier_item,

    def __affectee_getter_item_character(self, _):
        character = self.__calc_svc._current_char
        if character is not None:
            return character,
        else:
            return ()

    def __affectee_getter_item_ship(self, _):
        ship = self.__calc_svc._current_ship
        if ship is not None:
            return ship,
        else:
            return ()

    def __affectee_getter_item_other(self, affector):
        return affector.carrier_item._other

    __affectee_getters_item = {
        ModDomain.self: __affectee_getter_item_self,
        ModDomain.character: __affectee_getter_item_character,
        ModDomain.ship: __affectee_getter_item_ship,
        ModDomain.other: __affectee_getter_item_other}

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
        group_id = affector.modifier.tgt_filter_extra_arg
        return self.__affectee_domain_group.get((domain, group_id), ())

    def __affectee_getter_domain_skillrq(self, affector):
        domain = self.__contextize_tgt_filter_domain(affector)
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.carrier_item._type_id
        return self.__affectee_domain_skillrq.get((domain, skill_type_id), ())

    def __affectee_getter_owner_skillrq(self, affector):
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.carrier_item._type_id
        return self.__affectee_owner_skillrq.get(skill_type_id, ())

    __affectee_getters = {
        ModTgtFilter.item: __affectee_getter_item,
        ModTgtFilter.domain: __affectee_getter_domain,
        ModTgtFilter.domain_group: __affectee_getter_domain_group,
        ModTgtFilter.domain_skillrq: __affectee_getter_domain_skillrq,
        ModTgtFilter.owner_skillrq: __affectee_getter_owner_skillrq}

    # Affectee processing
    def get_affectees(self, affector):
        """Get iterable with items influenced by passed affector."""
        try:
            mod_tgt_filter = affector.modifier.tgt_filter
            try:
                getter = self.__affectee_getters[mod_tgt_filter]
            except KeyError as e:
                raise UnknownTgtFilterError(mod_tgt_filter) from e
            else:
                return getter(self, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
            return ()

    def register_affectee(self, tgt_item):
        """Add passed target item to register's affectee containers.

        We track affectees to efficiently update attributes when set of items
        influencing them changes.
        """
        self.__affectee.add(tgt_item)
        for key, affectee_map in self.__get_affectee_maps(tgt_item):
            affectee_map.add_data_entry(key, tgt_item)
        # When item like ship is added, there might already be affectors which
        # target it. Make sure that they are activated by calling this method
        self.__activate_direct_affectors(tgt_item)

    def unregister_affectee(self, tgt_item):
        """Remove passed target item from register's affectee containers."""
        self.__affectee.discard(tgt_item)
        for key, affectee_map in self.__get_affectee_maps(tgt_item):
            affectee_map.rm_data_entry(key, tgt_item)
        # Deactivate all affectors for item being unregistered
        self.__deactivate_direct_affectors(tgt_item)

    def __get_affectee_maps(self, tgt_item):
        """Return all places where passed affectee should be stored.

        Returns:
            Iterable with multiple elements, where each element is tuple in
            (key, affectee map) format.
        """
        affectee_maps = []
        domain = tgt_item._modifier_domain
        if domain is not None:
            # Domain
            affectee_maps.append((domain, self.__affectee_domain))
            group_id = tgt_item._type.group_id
            if group_id is not None:
                # Domain and group
                affectee_maps.append(
                    ((domain, group_id), self.__affectee_domain_group))
            for skill_type_id in tgt_item._type.required_skills:
                # Domain and skill requirement
                affectee_maps.append(
                    ((domain, skill_type_id), self.__affectee_domain_skillrq))
        if tgt_item._owner_modifiable is True:
            for skill_type_id in tgt_item._type.required_skills:
                # Owner-modifiable and skill requirement
                affectee_maps.append(
                    (skill_type_id, self.__affectee_owner_skillrq))
        return affectee_maps

    def __activate_direct_affectors(self, tgt_item):
        """Activate affectors which target passed item."""
        # Search for affectors
        other_items = tgt_item._other
        if other_items:
            affectors = self.__find_affectors_for_tgt_other(
                chain(*self.__affector_item.values()), other_items)
        elif tgt_item is self.__calc_svc._current_ship:
            affectors = self.__find_affectors_for_tgt_domain(
                chain(*self.__affector_item.values()), ModDomain.ship)
        elif tgt_item is self.__calc_svc._current_char:
            affectors = self.__find_affectors_for_tgt_domain(
                chain(*self.__affector_item.values()), ModDomain.character)
        else:
            return
        # Activate affectors
        self.__affector_item_active.add_data_set(tgt_item, affectors)

    def __deactivate_direct_affectors(self, tgt_item):
        """Deactivate direct affectors for passed item."""
        if tgt_item in self.__affector_item_active:
            del self.__affector_item_active[tgt_item]

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

    def __find_affectors_for_tgt_other(self, affectors, other_items):
        """Find 'other' affectors in valid configuration.

        Proper 'other' affector for passed 'other' item means that affector
        should target 'other' domain, and affector's carrier should be 'other'
        item which is passed in as argument. This item is called 'other' because
        it's 'other' to item being looked at, which happens outside of scope of
        this method.

        Args:
            affectors: Iterable with affectors to filter from..
            other_items: Iterable with items which belong to 'other' location.

        Returns:
            Set with valid 'other' affectors.
        """
        results = set()
        for affector in affectors:
            if (
                affector.modifier.tgt_domain == ModDomain.other and
                affector.carrier_item is other_items
            ):
                results.add(affector)
        return results

    # Affector processing
    def get_affectors(self, tgt_item):
        """Get all affectors, which influence passed item."""
        affectors = set()
        # Item
        affectors.update(self.__affector_item_active.get(tgt_item, ()))
        domain = tgt_item._modifier_domain
        if domain is not None:
            # Domain
            affectors.update(self.__affector_domain.get(domain, ()))
            # Domain and group
            affectors.update(self.__affector_domain_group.get(
                (domain, tgt_item._type.group_id), ()))
            for skill_type_id in tgt_item._type.required_skills:
                # Domain and skill requirement
                affectors.update(self.__affector_domain_skillrq.get(
                    (domain, skill_type_id), ()))
        if tgt_item._owner_modifiable is True:
            for skill_type_id in tgt_item._type.required_skills:
                # Owner-modifiable and skill requirement
                affectors.update(self.__affector_owner_skillrq.get(
                    skill_type_id, ()))
        return affectors

    def register_affector(self, affector):
        """Make register aware of the affector.

        It makes it possible for the affector to modify other items.
        """
        try:
            affector_storages = self.__get_affector_storages(affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
        else:
            for key, affector_map in affector_storages:
                affector_map.add_data_entry(key, affector)

    def unregister_affector(self, affector):
        """Remove the affector from register.

        It makes it impossible for the affector to modify any other items.
        """
        try:
            affector_storages = self.__get_affector_storages(affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
        else:
            for key, affector_map in affector_storages:
                affector_map.rm_data_entry(key, affector)

    # Helpers for affector registering/unregistering, they find affector maps
    # and keys to them
    def __affector_storages_getter_item_self(self, affector):
        return (
            (affector.carrier_item, self.__affector_item),
            (affector.carrier_item, self.__affector_item_active))

    def __affector_storages_getter_item_character(self, affector):
        character = self.__calc_svc._current_char
        if character is not None:
            return (
                (affector.carrier_item, self.__affector_item),
                (character, self.__affector_item_active))
        else:
            return (affector.carrier_item, self.__affector_item),

    def __affector_storages_getter_item_ship(self, affector):
        ship = self.__calc_svc._current_ship
        if ship is not None:
            return (
                (affector.carrier_item, self.__affector_item),
                (ship, self.__affector_item_active))
        else:
            return (affector.carrier_item, self.__affector_item),

    def __affector_storages_getter_item_other(self, affector):
        affector_storages = [(affector.carrier_item, self.__affector_item)]
        for other_item in affector.carrier_item._other:
            affector_storages.append((other_item, self.__affector_item_active))
        return affector_storages

    __affector_storages_getters_item = {
        ModDomain.self: __affector_storages_getter_item_self,
        ModDomain.character: __affector_storages_getter_item_character,
        ModDomain.ship: __affector_storages_getter_item_ship,
        ModDomain.other: __affector_storages_getter_item_other}

    def __affector_storages_getter_item(self, affector):
        tgt_domain = affector.modifier.tgt_domain
        try:
            getter = self.__affector_storages_getters_item[tgt_domain]
        except KeyError as e:
            raise UnexpectedDomainError(tgt_domain) from e
        else:
            return getter(self, affector)

    def __affector_storages_getter_domain(self, affector):
        domain = self.__contextize_tgt_filter_domain(affector)
        return (domain, self.__affector_domain),

    def __affector_storages_getter_domain_group(self, affector):
        domain = self.__contextize_tgt_filter_domain(affector)
        group_id = affector.modifier.tgt_filter_extra_arg
        return ((domain, group_id), self.__affector_domain_group),

    def __affector_storages_getter_domain_skillrq(self, affector):
        domain = self.__contextize_tgt_filter_domain(affector)
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.carrier_item._type_id
        return ((domain, skill_type_id), self.__affector_domain_skillrq),

    def __affector_storages_getter_owner_skillrq(self, affector):
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.carrier_item._type_id
        return (skill_type_id, self.__affector_owner_skillrq),

    __affector_storages_getters = {
        ModTgtFilter.item: __affector_storages_getter_item,
        ModTgtFilter.domain: __affector_storages_getter_domain,
        ModTgtFilter.domain_group: __affector_storages_getter_domain_group,
        ModTgtFilter.domain_skillrq: __affector_storages_getter_domain_skillrq,
        ModTgtFilter.owner_skillrq: __affector_storages_getter_owner_skillrq}

    def __get_affector_storages(self, affector):
        """Get places where passed affector should be stored.

        Args:
            affector: Affector, for which storage is looked up.

        Returns:
            Iterable with tuples in (key, affector map) format, which defines
            where affector should be stored.

        Raises:
            UnexpectedDomainError: If affector's modifier target domain is not
                supported for context of passed affector.
            UnknownTargetFilterError: If affector's modifier filter type is not
                supported.
        """
        tgt_filter = affector.modifier.tgt_filter
        try:
            getter = self.__affector_storages_getters[tgt_filter]
        except KeyError as e:
            raise UnknownTgtFilterError(affector.modifier.tgt_filter) from e
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
        if domain == ModDomain.self:
            if carrier_item is self.__calc_svc._current_ship:
                return ModDomain.ship
            elif carrier_item is self.__calc_svc._current_char:
                return ModDomain.character
            else:
                raise UnexpectedDomainError(domain)
        # Just return untouched domain for all other valid cases. Valid cases
        # include 'globally' visible (within the fit scope) domains only.
        # I.e. if item on fit refers this target domain, it should always
        # refer the same target item regardless of source item.
        elif domain in (ModDomain.character, ModDomain.ship):
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
                'malformed modifier on item type {}: '
                'unsupported target domain {}'
            ).format(affector.carrier_item._type_id, error.args[0])
            logger.warning(msg)
        elif isinstance(error, UnknownTgtFilterError):
            msg = (
                'malformed modifier on item type {}: invalid target filter {}'
            ).format(affector.carrier_item._type_id, error.args[0])
            logger.warning(msg)
        else:
            raise error
