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
from eos.item import Character
from eos.item import Ship
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
        # All known affectee items
        # Format: {affectee items}
        self.__affectees = set()

        # Items belonging to certain domain
        # Format: {(affectee fit, domain): {affectee items}}
        self.__affectee_domain = KeyedStorage()

        # Items belonging to certain domain and group
        # Format: {(affectee fit, domain, group ID): {affectee items}}
        self.__affectee_domain_group = KeyedStorage()

        # Items belonging to certain domain and having certain skill requirement
        # Format: {(affectee fit, domain, skill type ID): {affectee items}}
        self.__affectee_domain_skillrq = KeyedStorage()

        # Owner-modifiable items which have certain skill requirement
        # Format: {(affectee fit, skill type ID): {affectee items}}
        self.__affectee_owner_skillrq = KeyedStorage()

        # Affectors which target 'other' location are always stored here,
        # regardless if they actually affect something or not
        # Format: {affector item: {affectors}}
        self.__affector_item_other = KeyedStorage()

        # Affectors which should affect only one item (ship, character or self),
        # when this item is not registered as affectee
        # Format: {affectee fit: {affectors}}
        self.__affector_item_awaitable = KeyedStorage()

        # All active affectors which target specific item (via ship, character,
        # other reference or self) are kept here
        # Format: {affectee item: {affectors}}
        self.__affector_item_active = KeyedStorage()

        # Affectors influencing all items belonging to certain domain
        # Format: {(affectee fit, domain): {affectors}}
        self.__affector_domain = KeyedStorage()

        # Affectors influencing items belonging to certain domain and group
        # Format: {(affectee fit, domain, group ID): {affectors}}
        self.__affector_domain_group = KeyedStorage()

        # Affectors influencing items belonging to certain domain and having
        # certain skill requirement
        # Format: {(affectee fit, domain, skill type ID): {affectors}}
        self.__affector_domain_skillrq = KeyedStorage()

        # Affectors influencing owner-modifiable items which have certain skill
        # requirement
        # Format: {(affectee fit, skill type ID): {affectors}}
        self.__affector_owner_skillrq = KeyedStorage()

    # Query methods
    def get_affectees(self, affectee_fits, affector):
        """Get iterable with items influenced by passed affector."""
        try:
            mod_tgt_filter = affector.modifier.tgt_filter
            try:
                getter = self.__affectees_getters[mod_tgt_filter]
            except KeyError as e:
                raise UnknownTgtFilterError(mod_tgt_filter) from e
            else:
                return getter(self, affectee_fits, affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
            return ()

    def get_affectors(self, affectee_item):
        """Get all affectors, which influence passed item."""
        affectee_fit = affectee_item._fit
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

    # Maintenance methods
    def register_affectee(self, affectee_item):
        """Add passed affectee item to register.

        We track affectees to efficiently update attributes when set of items
        influencing them changes.
        """
        self.__affectees.add(affectee_item)
        affectee_fit = affectee_item._fit
        for key, affectee_map in self.__get_affectee_storages(
            affectee_fit, affectee_item
        ):
            affectee_map.add_data_entry(key, affectee_item)
        # Process special affectors separately. E.g., when item like ship is
        # added, there might already be affectors which should affect it, and
        # in this method we activate such affectors
        self.__activate_special_affectors(affectee_fit, affectee_item)

    def unregister_affectee(self, affectee_item):
        """Remove passed affectee item from register."""
        self.__affectees.remove(affectee_item)
        affectee_fit = affectee_item._fit
        for key, affectee_map in self.__get_affectee_storages(
            affectee_fit, affectee_item
        ):
            affectee_map.rm_data_entry(key, affectee_item)
        # Deactivate all special affectors for item being unregistered
        self.__deactivate_special_affectors(affectee_fit, affectee_item)

    def register_local_affector(self, affector):
        """Make the register aware of the local affector.

        It makes it possible for the affector to modify other items within its
        fit.
        """
        try:
            affector_storages = self.__get_local_affector_storages(affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
        else:
            for key, affector_map in affector_storages:
                affector_map.add_data_entry(key, affector)

    def unregister_local_affector(self, affector):
        """Remove local affector from the register.

        It makes it impossible for the affector to modify any other items.
        """
        try:
            affector_storages = self.__get_local_affector_storages(affector)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
        else:
            for key, affector_map in affector_storages:
                affector_map.rm_data_entry(key, affector)

    def register_projected_affector(self, affector, tgt_items):
        """Make register aware that projected affector affects items.

        Should be called every time affector is applied onto any object.
        """
        try:
            affector_storages = self.__get_projected_affector_storages(
                affector, tgt_items)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
        else:
            for key, affector_map in affector_storages:
                affector_map.add_data_entry(key, affector)

    def unregister_projected_affector(self, affector, tgt_items):
        """Remove effect of affector from items.

        Should be called every time affector stops affecting any object.
        """
        try:
            affector_storages = self.__get_projected_affector_storages(
                affector, tgt_items)
        except Exception as e:
            self.__handle_affector_errors(e, affector)
        else:
            for key, affector_map in affector_storages:
                affector_map.rm_data_entry(key, affector)

    # Helpers for affectee getter
    def __get_affectees_item_self(self, _, affector):
        return affector.item,

    def __get_affectees_item_character(self, affectee_fits, _):
        affectee_items = []
        for affectee_fit in affectee_fits:
            character = affectee_fit.character
            if character in self.__affectees:
                affectee_items.append(character)
        return affectee_items

    def __get_affectees_item_ship(self, affectee_fits, _):
        affectee_items = []
        for affectee_fit in affectee_fits:
            ship = affectee_fit.ship
            if ship in self.__affectees:
                affectee_items.append(ship)
        return affectee_items

    def __get_affectees_item_other(self, _, affector):
        return [i for i in affector.item._others if i in self.__affectees]

    __affectees_getters_item = {
        ModDomain.self: __get_affectees_item_self,
        ModDomain.character: __get_affectees_item_character,
        ModDomain.ship: __get_affectees_item_ship,
        ModDomain.other: __get_affectees_item_other}

    def __get_affectees_item(self, affectee_fits, affector):
        try:
            getter = self.__affectees_getters_item[affector.modifier.tgt_domain]
        except KeyError as e:
            raise UnexpectedDomainError(affector.modifier.tgt_domain) from e
        else:
            return getter(self, affectee_fits, affector)

    def __get_affectees_domain(self, affectee_fits, affector):
        domain = self.__contextize_local_affector_domain(affector)
        affectee_items = set()
        for affectee_fit in affectee_fits:
            key = (affectee_fit, domain)
            affectee_items.update(self.__affectee_domain.get(key, ()))
        return affectee_items

    def __get_affectees_domain_group(self, affectee_fits, affector):
        domain = self.__contextize_local_affector_domain(affector)
        group_id = affector.modifier.tgt_filter_extra_arg
        affectee_items = set()
        for affectee_fit in affectee_fits:
            key = (affectee_fit, domain, group_id)
            affectee_items.update(self.__affectee_domain_group.get(key, ()))
        return affectee_items

    def __get_affectees_domain_skillrq(self, affectee_fits, affector):
        domain = self.__contextize_local_affector_domain(affector)
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.item._type_id
        affectee_items = set()
        for affectee_fit in affectee_fits:
            key = (affectee_fit, domain, skill_type_id)
            affectee_items.update(self.__affectee_domain_skillrq.get(key, ()))
        return affectee_items

    def __get_affectees_owner_skillrq(self, affectee_fits, affector):
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.item._type_id
        affectee_items = set()
        for affectee_fit in affectee_fits:
            key = (affectee_fit, skill_type_id)
            affectee_items.update(self.__affectee_owner_skillrq.get(key, ()))
        return affectee_items

    __affectees_getters = {
        ModTgtFilter.item: __get_affectees_item,
        ModTgtFilter.domain: __get_affectees_domain,
        ModTgtFilter.domain_group: __get_affectees_domain_group,
        ModTgtFilter.domain_skillrq: __get_affectees_domain_skillrq,
        ModTgtFilter.owner_skillrq: __get_affectees_owner_skillrq}

    # Helpers for affectee registering/unregistering
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
            # Domain and group
            if group_id is not None:
                affectee_storages.append((
                    (affectee_fit, domain, group_id),
                    self.__affectee_domain_group))
            # Domain and skill requirement
            for skill_type_id in affectee_item._type.required_skills:
                affectee_storages.append((
                    (affectee_fit, domain, skill_type_id),
                    self.__affectee_domain_skillrq))
        # Owner-modifiable and skill requirement
        if affectee_item._owner_modifiable is True:
            for skill_type_id in affectee_item._type.required_skills:
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
            if domain == ModDomain.ship and isinstance(affectee_item, Ship):
                awaitable_to_activate.add(affector)
            # Character
            elif (
                domain == ModDomain.character and
                isinstance(affectee_item, Character)
            ):
                awaitable_to_activate.add(affector)
            # Self
            elif domain == ModDomain.self and affectee_item is affector.item:
                awaitable_to_activate.add(affector)
        # Move awaitable affectors from awaitable storage to active storage
        if awaitable_to_activate:
            self.__affector_item_awaitable.rm_data_set(
                affectee_fit, awaitable_to_activate)
            self.__affector_item_active.add_data_set(
                affectee_item, awaitable_to_activate)
        # Other
        other_to_activate = set()
        for affector_item, affectors in self.__affector_item_other.items():
            if affectee_item in affector_item._others:
                other_to_activate.update(affectors)
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
                ModDomain.ship, ModDomain.character, ModDomain.self
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

    # Helpers for affector registering/unregistering
    def __get_local_affector_storages(self, affector):
        """Get places where passed local affector should be stored.

        Raises:
            UnexpectedDomainError: If affector's modifier target domain is not
                supported for context of passed affector.
            UnknownTgtFilterError: If affector's modifier filter type is not
                supported.
        """
        tgt_filter = affector.modifier.tgt_filter
        if tgt_filter == ModTgtFilter.item:
            domain = affector.modifier.tgt_domain
            try:
                getter = self.__local_affector_storages_getters_item[domain]
            except KeyError as e:
                raise UnexpectedDomainError(domain) from e
            return getter(self, affector)
        else:
            try:
                getter = self.__affector_storages_getters[tgt_filter]
            except KeyError as e:
                raise UnknownTgtFilterError(tgt_filter) from e
            domain = self.__contextize_local_affector_domain(affector)
            affectee_fits = affector.item._fit,
            return getter(self, affector, domain, affectee_fits)

    def __get_projected_affector_storages(self, affector, tgt_items):
        tgt_filter = affector.modifier.tgt_filter
        if tgt_filter == ModTgtFilter.item:
            storages = []
            for tgt_item in tgt_items:
                if tgt_item in self.__affectees:
                    storages.append((tgt_item, self.__affector_item_active))
            return storages
        else:
            try:
                getter = self.__affector_storages_getters[tgt_filter]
            except KeyError as e:
                raise UnknownTgtFilterError(tgt_filter) from e
            affectee_fits = set()
            for tgt_item in tgt_items:
                if isinstance(tgt_item, Ship):
                    affectee_fits.add(tgt_item._fit)
            return getter(self, affector, ModDomain.ship, affectee_fits)

    def __get_affector_storages_domain(self, _, domain, fits):
        storages = []
        for affectee_fit in fits:
            key = (affectee_fit, domain)
            storages.append((key, self.__affector_domain))
        return storages

    def __get_affector_storages_domain_group(self, affector, domain, fits):
        group_id = affector.modifier.tgt_filter_extra_arg
        storages = []
        for affectee_fit in fits:
            key = (affectee_fit, domain, group_id)
            storages.append((key, self.__affector_domain_group))
        return storages

    def __get_affector_storages_domain_skillrq(self, affector, domain, fits):
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.item._type_id
        storages = []
        for affectee_fit in fits:
            key = (affectee_fit, domain, skill_type_id)
            storages.append((key, self.__affector_domain_skillrq))
        return storages

    def __get_affector_storages_owner_skillrq(self, affector, _, fits):
        skill_type_id = affector.modifier.tgt_filter_extra_arg
        if skill_type_id == EosTypeId.current_self:
            skill_type_id = affector.item._type_id
        storages = []
        for affectee_fit in fits:
            key = (affectee_fit, skill_type_id)
            storages.append((key, self.__affector_owner_skillrq))
        return storages

    __affector_storages_getters = {
        ModTgtFilter.domain: __get_affector_storages_domain,
        ModTgtFilter.domain_group: __get_affector_storages_domain_group,
        ModTgtFilter.domain_skillrq: __get_affector_storages_domain_skillrq,
        ModTgtFilter.owner_skillrq: __get_affector_storages_owner_skillrq}

    def __get_local_affector_storages_item_self(self, affector):
        if affector.item in self.__affectees:
            return [(affector.item, self.__affector_item_active)]
        else:
            affectee_fit = affector.item._fit
            return (affectee_fit, self.__affector_item_awaitable),

    def __get_local_affector_storages_item_character(self, affector):
        affectee_fit = affector.item._fit
        character = affectee_fit.character
        if character in self.__affectees:
            return (character, self.__affector_item_active),
        else:
            return (affectee_fit, self.__affector_item_awaitable),

    def __get_local_affector_storages_item_ship(self, affector):
        affectee_fit = affector.item._fit
        ship = affectee_fit.ship
        if ship in self.__affectees:
            return (ship, self.__affector_item_active),
        else:
            return (affectee_fit, self.__affector_item_awaitable),

    def __get_local_affector_storages_item_other(self, affector):
        # Affectors with 'other' modifiers are always stored in their special
        # place
        storages = [(affector.item, self.__affector_item_other)]
        # And all those which have valid target are also stored in storage for
        # active direct affectors
        for other_item in affector.item._others:
            if other_item in self.__affectees:
                storages.append((other_item, self.__affector_item_active))
        return storages

    __local_affector_storages_getters_item = {
        ModDomain.self: __get_local_affector_storages_item_self,
        ModDomain.character: __get_local_affector_storages_item_character,
        ModDomain.ship: __get_local_affector_storages_item_ship,
        ModDomain.other: __get_local_affector_storages_item_other}

    # Shared helpers
    def __contextize_local_affector_domain(self, affector):
        """Convert relative domain into absolute for local affector.

        Applicable only to en-masse modifications. That is, when modification
        affects multiple items in target domain. If modification targets single
        item, it should not be handled via this method.

        Raises:
            UnexpectedDomainError: If affector's modifier target domain is not
                supported.
        """
        item = affector.item
        domain = affector.modifier.tgt_domain
        if domain == ModDomain.self:
            if isinstance(item, Ship):
                return ModDomain.ship
            elif isinstance(item, Character):
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
            ).format(affector.item._type_id, error.args[0])
            logger.warning(msg)
        elif isinstance(error, UnknownTgtFilterError):
            msg = (
                'malformed modifier on item type {}: invalid target filter {}'
            ).format(affector.item._type_id, error.args[0])
            logger.warning(msg)
        else:
            raise error
