# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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

    def __init__(self):
        # Items belonging to certain domain
        # Format: {(fit, domain): {affectee items}}
        self.__affectee_domain = KeyedStorage()

        # Items belonging to certain domain and group
        # Format: {(fit, domain, group ID): {affectee items}}
        self.__affectee_domain_group = KeyedStorage()

        # Items belonging to certain domain and having certain skill requirement
        # Format: {(fit, domain, skill type ID): {affectee items}}
        self.__affectee_domain_skillrq = KeyedStorage()

        # Owner-modifiable items which have certain skill requirement
        # Format: {(fit, skill type ID): {affectee items}}
        self.__affectee_owner_skillrq = KeyedStorage()

        # Affectors which target 'other' location are always stored here,
        # regardless if they actually affect something or not
        # Format: {carrier item: {affectors}}
        self.__affector_item_other = KeyedStorage()

        # Affectors which should affect only one item (ship, character or self),
        # when this item is not registered as affectee
        # Format: {fit: {affectors}}
        self.__affector_item_awaitable = KeyedStorage()

        # All active affectors which target specific item (via ship, character,
        # other reference or self) are kept here
        # Format: {affectee item: {affectors}}
        self.__affector_item_active = KeyedStorage()

        # Affectors influencing all items belonging to certain domain
        # Format: {(fit, domain): {affectors}}
        self.__affector_domain = KeyedStorage()

        # Affectors influencing items belonging to certain domain and group
        # Format: {(fit, domain, group ID): {affectors}}
        self.__affector_domain_group = KeyedStorage()

        # Affectors influencing items belonging to certain domain and having
        # certain skill requirement
        # Format: {(fit, domain, skill type ID): {affectors}}
        self.__affector_domain_skillrq = KeyedStorage()

        # Affectors influencing owner-modifiable items which have certain skill
        # requirement
        # Format: {(fit, skill type ID): {affectors}}
        self.__affector_owner_skillrq = KeyedStorage()

    # Helpers for affectee getter - they find map and get data from it according
    # to passed affector
    def __get_affectees_item_self(self, _, affector):
        return affector.carrier_item,

    def __get_affectees_item_character(self, affector_fit, _):
        character = affector_fit.character
        if character is not None and character._is_loaded:
            return character,
        else:
            return ()

    def __get_affectees_item_ship(self, affector_fit, _):
        ship = affector_fit.ship
        if ship is not None and ship._is_loaded:
            return ship,
        else:
            return ()

    def __get_affectees_item_other(self, _, affector):
        return [
            i for i in affector.carrier_item._others
            if i._is_loaded]

    __affectees_getters_item = {
        ModDomain.self: __get_affectees_item_self,
        ModDomain.character: __get_affectees_item_character,
        ModDomain.ship: __get_affectees_item_ship,
        ModDomain.other: __get_affectees_item_other}

    def __get_affectees_item(self, affector_fit, affector):
        try:
            getter = self.__affectees_getters_item[affector.modifier.tgt_domain]
        except KeyError as e:
            raise UnexpectedDomainError(affector.modifier.tgt_domain) from e
        else:
            return getter(self, affector_fit, affector)

    def __get_affectees_domain(self, affector_fit, affector):
        domain = self.__contextize_tgt_filter_domain(affector_fit, affector)
        key = (affector_fit, domain)
        return self.__affectee_domain.get(key, ())

    def __get_affectees_domain_group(self, affector_fit, affector):
        domain = self.__contextize_tgt_filter_domain(affector_fit, affector)
        group_id = affector.modifier.tgt_filter_extra_arg
        key = (affector_fit, domain, group_id)
        return self.__affectee_domain_group.get(key, ())

    def __get_affectees_domain_skillrq(self, affector_fit, affector):
        domain = self.__contextize_tgt_filter_domain(affector_fit, affector)
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.carrier_item._type_id
        key = (affector_fit, domain, skill_type_id)
        return self.__affectee_domain_skillrq.get(key, ())

    def __get_affectees_owner_skillrq(self, affector_fit, affector):
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.carrier_item._type_id
        key = (affector_fit, skill_type_id)
        return self.__affectee_owner_skillrq.get(key, ())

    __affectees_getters = {
        ModTgtFilter.item: __get_affectees_item,
        ModTgtFilter.domain: __get_affectees_domain,
        ModTgtFilter.domain_group: __get_affectees_domain_group,
        ModTgtFilter.domain_skillrq: __get_affectees_domain_skillrq,
        ModTgtFilter.owner_skillrq: __get_affectees_owner_skillrq}

    # Affectee processing
    def get_affectees(self, affector_fit, affector):
        """Get iterable with items influenced by passed affector."""
        try:
            mod_tgt_filter = affector.modifier.tgt_filter
            try:
                getter = self.__affectees_getters[mod_tgt_filter]
            except KeyError as e:
                raise UnknownTgtFilterError(mod_tgt_filter) from e
            else:
                return getter(self, affector_fit, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
            return ()

    def register_affectee(self, affectee_fit, affectee_item):
        """Add passed affectee item to register.

        We track affectees to efficiently update attributes when set of items
        influencing them changes.
        """
        for key, affectee_map in self.__get_affectee_storages(
            affectee_fit, affectee_item
        ):
            affectee_map.add_data_entry(key, affectee_item)
        # Process special affectors separately. E.g., when item like ship is
        # added, there might already be affectors which should affect it, and
        # in this method we activate such affectors
        self.__activate_special_affectors(affectee_fit, affectee_item)

    def unregister_affectee(self, affectee_fit, affectee_item):
        """Remove passed affectee item from register."""
        for key, affectee_map in self.__get_affectee_storages(
            affectee_fit, affectee_item
        ):
            affectee_map.rm_data_entry(key, affectee_item)
        # Deactivate all special affectors for item being unregistered
        self.__deactivate_special_affectors(affectee_fit, affectee_item)

    def __get_affectee_storages(self, affectee_fit, affectee_item):
        """Return all places where passed affectee should be stored.

        Returns:
            Iterable with multiple elements, where each element is tuple in
            (key, affectee map) format.
        """
        affectee_storages = []
        domain = affectee_item._modifier_domain
        if domain is not None:
            # Domain
            affectee_storages.append((
                (affectee_fit, domain),
                self.__affectee_domain))
            group_id = affectee_item._type.group_id
            if group_id is not None:
                # Domain and group
                affectee_storages.append((
                    (affectee_fit, domain, group_id),
                    self.__affectee_domain_group))
            for skill_type_id in affectee_item._type.required_skills:
                # Domain and skill requirement
                affectee_storages.append((
                    (affectee_fit, domain, skill_type_id),
                    self.__affectee_domain_skillrq))
        if affectee_item._owner_modifiable is True:
            for skill_type_id in affectee_item._type.required_skills:
                # Owner-modifiable and skill requirement
                affectee_storages.append((
                    (affectee_fit, skill_type_id),
                    self.__affectee_owner_skillrq))
        return affectee_storages

    def __activate_special_affectors(self, affectee_fit, affectee_item):
        """Activate special affectors which should affect passed item."""
        awaitable_to_activate = set()
        for affector in self.__affector_item_awaitable.get(affectee_fit, ()):
            domain = affector.modifier.tgt_domain
            # Ship
            if domain == ModDomain.ship:
                if affectee_item is affectee_fit.ship:
                    awaitable_to_activate.add(affector)
            # Character
            elif domain == ModDomain.character:
                if affectee_item is affectee_fit.character:
                    awaitable_to_activate.add(affector)
        # Move awaitable affectors from awaitable storage to active storage
        if awaitable_to_activate:
            self.__affector_item_awaitable.rm_data_set(
                affectee_fit, awaitable_to_activate)
            self.__affector_item_active.add_data_set(
                affectee_item, awaitable_to_activate)
        # Other
        other_to_activate = set()
        for carrier_item, affectors in self.__affector_item_other.items():
            carrier_others = carrier_item._others
            for affector in affectors:
                if affectee_item in carrier_others:
                    other_to_activate.add(affector)
        # Just add affectors to active storage, 'other' affectors should never
        # be removed from 'other'-specific storage
        if other_to_activate:
            self.__affector_item_active.add_data_set(
                affectee_item, other_to_activate)

    def __deactivate_special_affectors(self, affectee_fit, affectee_item):
        """Deactivate special affectors which affect passed item."""
        if affectee_item not in self.__affector_item_active:
            return
        awaitable_to_deactivate = set()
        for affector in self.__affector_item_active.get(affectee_item, ()):
            if affector.modifier.tgt_domain in (
                ModDomain.ship, ModDomain.character
            ):
                awaitable_to_deactivate.add(affector)
        # Remove all affectors influencing this item directly, including 'other'
        # affectors
        del self.__affector_item_active[affectee_item]
        # And make sure awaitable affectors are moved to appropriate container
        # for future use
        if awaitable_to_deactivate:
            self.__affector_item_awaitable.add_data_set(
                affectee_fit, awaitable_to_deactivate)

    # Affector processing
    def get_affectors(self, affectee_fit, affectee_item):
        """Get all affectors, which influence passed item."""
        affectors = set()
        # Item
        affectors.update(self.__affector_item_active.get(
            affectee_item, ()))
        domain = affectee_item._modifier_domain
        if domain is not None:
            # Domain
            affectors.update(self.__affector_domain.get(
                (affectee_fit, domain), ()))
            # Domain and group
            group_id = affectee_item._type.group_id
            affectors.update(self.__affector_domain_group.get(
                (affectee_fit, domain, group_id), ()))
            for skill_type_id in affectee_item._type.required_skills:
                # Domain and skill requirement
                affectors.update(self.__affector_domain_skillrq.get(
                    (affectee_fit, domain, skill_type_id), ()))
        if affectee_item._owner_modifiable is True:
            for skill_type_id in affectee_item._type.required_skills:
                # Owner-modifiable and skill requirement
                affectors.update(self.__affector_owner_skillrq.get(
                    (affectee_fit, skill_type_id), ()))
        return affectors

    def register_affector(self, affector_fit, affector):
        """Make register aware of the affector.

        It makes it possible for the affector to modify other items.
        """
        try:
            affector_storages = self.__get_affector_storages(
                affector_fit, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
        else:
            for key, affector_map in affector_storages:
                affector_map.add_data_entry(key, affector)

    def unregister_affector(self, affector_fit, affector):
        """Remove the affector from register.

        It makes it impossible for the affector to modify any other items.
        """
        try:
            affector_storages = self.__get_affector_storages(
                affector_fit, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
        else:
            for key, affector_map in affector_storages:
                affector_map.rm_data_entry(key, affector)

    # Helpers for affector registering/unregistering, they find affector maps
    # and keys to them
    def __get_affector_storages_item_self(self, _, affector):
        return (affector.carrier_item, self.__affector_item_active),

    def __get_affector_storages_item_character(self, affector_fit, _):
        character = affector_fit.character
        if character is not None and character._is_loaded:
            return (character, self.__affector_item_active),
        else:
            return (affector_fit, self.__affector_item_awaitable),

    def __get_affector_storages_item_ship(self, affector_fit, _):
        ship = affector_fit.ship
        if ship is not None and ship._is_loaded:
            return (ship, self.__affector_item_active),
        else:
            return (affector_fit, self.__affector_item_awaitable),

    def __get_affector_storages_item_other(self, _, affector):
        # Affectors with 'other' modifiers are always stored in their special
        # place
        storages = [(affector.carrier_item, self.__affector_item_other)]
        # And all those which have valid target are also stored in storage for
        # active direct affectors
        for other_item in affector.carrier_item._others:
            if not other_item._is_loaded:
                continue
            storages.append((other_item, self.__affector_item_active))
        return storages

    __affector_storages_getters_item = {
        ModDomain.self: __get_affector_storages_item_self,
        ModDomain.character: __get_affector_storages_item_character,
        ModDomain.ship: __get_affector_storages_item_ship,
        ModDomain.other: __get_affector_storages_item_other}

    def __get_affector_storages_item(self, affector_fit, affector):
        tgt_domain = affector.modifier.tgt_domain
        try:
            getter = self.__affector_storages_getters_item[tgt_domain]
        except KeyError as e:
            raise UnexpectedDomainError(tgt_domain) from e
        else:
            return getter(self, affector_fit, affector)

    def __get_affector_storages_domain(self, affector_fit, affector):
        domain = self.__contextize_tgt_filter_domain(affector_fit, affector)
        key = (affector_fit, domain)
        storage = self.__affector_domain
        return (key, storage),

    def __get_affector_storages_domain_group(self, affector_fit, affector):
        domain = self.__contextize_tgt_filter_domain(affector_fit, affector)
        group_id = affector.modifier.tgt_filter_extra_arg
        key = (affector_fit, domain, group_id)
        storage = self.__affector_domain_group
        return (key, storage),

    def __get_affector_storages_domain_skillrq(self, affector_fit, affector):
        domain = self.__contextize_tgt_filter_domain(affector_fit, affector)
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.carrier_item._type_id
        key = (affector_fit, domain, skill_type_id)
        storage = self.__affector_domain_skillrq
        return (key, storage),

    def __get_affector_storages_owner_skillrq(self, affector_fit, affector):
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.carrier_item._type_id
        key = (affector_fit, skill_type_id)
        storage = self.__affector_owner_skillrq
        return (key, storage),

    __affector_storages_getters = {
        ModTgtFilter.item: __get_affector_storages_item,
        ModTgtFilter.domain: __get_affector_storages_domain,
        ModTgtFilter.domain_group: __get_affector_storages_domain_group,
        ModTgtFilter.domain_skillrq: __get_affector_storages_domain_skillrq,
        ModTgtFilter.owner_skillrq: __get_affector_storages_owner_skillrq}

    def __get_affector_storages(self, affector_fit, affector):
        """Get places where passed affector should be stored.

        Raises:
            UnexpectedDomainError: If affector's modifier target domain is not
                supported for context of passed affector.
            UnknownTgtFilterError: If affector's modifier filter type is not
                supported.
        """
        tgt_filter = affector.modifier.tgt_filter
        try:
            getter = self.__affector_storages_getters[tgt_filter]
        except KeyError as e:
            raise UnknownTgtFilterError(affector.modifier.tgt_filter) from e
        else:
            return getter(self, affector_fit, affector)

    # Shared helpers
    def __contextize_tgt_filter_domain(self, affector_fit, affector):
        """Convert relative domain into absolute.

        Applicable only to en-masse modifications. That is, when modification
        affects multiple items in target domain. If modification targets single
        item, it should not be handled via this method.

        Raises:
            UnexpectedDomainError: If affector's modifier target domain is not
                supported.
        """
        carrier_item = affector.carrier_item
        domain = affector.modifier.tgt_domain
        if domain == ModDomain.self:
            if carrier_item is affector_fit.ship:
                return ModDomain.ship
            elif carrier_item is affector_fit.character:
                return ModDomain.character
            else:
                raise UnexpectedDomainError(domain)
        # Just return untouched domain for all other valid cases. Valid cases
        # include 'globally' visible (within the fit scope) domains only. I.e.
        # if item on fit refers this target domain, it should always refer the
        # same target item regardless of source item.
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
