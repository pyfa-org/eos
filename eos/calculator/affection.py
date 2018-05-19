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
from eos.const.eos import ModAffecteeFilter
from eos.const.eos import ModDomain
from eos.item import Character
from eos.item import Ship
from eos.util.keyed_storage import KeyedStorage
from .exception import UnexpectedDomainError
from .exception import UnknownAffecteeFilterError


logger = getLogger(__name__)


class AffectionRegister:
    """Keeps track of connections between affector specs and affectee items.

    Having information about such connections is a hard requirement for
    efficient partial attribute recalculation.
    """

    def __init__(self):
        # All known affectee items
        # Format: {affectee items}
        self.__affectees = set()

        # Items belonging to certain fit and domain
        # Format: {(affectee fit, affectee domain): {affectee items}}
        self.__affectees_domain = KeyedStorage()

        # Items belonging to certain fit, domain and group
        # Format: {(affectee fit, affectee domain, affectee group ID): {affectee
        # items}}
        self.__affectees_domain_group = KeyedStorage()

        # Items belonging to certain fit and domain, and having certain skill
        # requirement
        # Format: {(affectee fit, affectee domain, affectee skill requirement
        # type ID): {affectee items}}
        self.__affectees_domain_skillrq = KeyedStorage()

        # Owner-modifiable items which belong to certain fit and have certain
        # skill requirement
        # Format: {(affectee fit, affectee skill requirement type ID): {affectee
        # items}}
        self.__affectees_owner_skillrq = KeyedStorage()

        # Affector specs with modifiers which affect 'other' location are always
        # stored here, regardless if they actually affect something or not
        # Format: {affector item: {affector specs}}
        self.__affectors_item_other = KeyedStorage()

        # Affector specs which should affect only one item (ship, character or
        # self), when this item is not registered as affectee
        # Format: {affectee fit: {affector specs}}
        self.__affectors_item_awaiting = KeyedStorage()

        # All active affector specs which affect one specific item (via ship,
        # character, other reference or self) are kept here
        # Format: {affectee item: {affector specs}}
        self.__affectors_item_active = KeyedStorage()

        # Affector specs influencing all items belonging to certain fit and
        # domain
        # Format: {(affectee fit, affectee domain): {affector specs}}
        self.__affectors_domain = KeyedStorage()

        # Affector specs influencing items belonging to certain fit, domain and
        # group
        # Format: {(affectee fit, affectee domain, affectee group ID): {affector
        # specs}}
        self.__affectors_domain_group = KeyedStorage()

        # Affector specs influencing items belonging to certain fit and domain,
        # and having certain skill requirement
        # Format: {(affectee fit, affectee domain, affectee skill requirement
        # type ID): {affector specs}}
        self.__affectors_domain_skillrq = KeyedStorage()

        # Affector specs influencing owner-modifiable items belonging to certain
        # fit and having certain skill requirement
        # Format: {(affectee fit, affectee skill requirement type ID): {affector
        # specs}}
        self.__affectors_owner_skillrq = KeyedStorage()

    # Query methods
    def get_local_affectee_items(self, affector_spec):
        """Get iterable with items influenced by passed local affector spec."""
        try:
            affectee_filter = affector_spec.modifier.affectee_filter
            # Direct item modification needs to use local-specific getters
            if affectee_filter == ModAffecteeFilter.item:
                affectee_domain = affector_spec.modifier.affectee_domain
                try:
                    getter = self.__local_affectees_getters[affectee_domain]
                except KeyError as e:
                    raise UnexpectedDomainError(affectee_domain) from e
                return getter(self, affector_spec)
            # En-masse filtered modification can use shared affectee item
            # getters
            else:
                try:
                    getter = self.__affectees_getters[affectee_filter]
                except KeyError as e:
                    raise UnknownAffecteeFilterError(affectee_filter) from e
                affectee_domain = self.__resolve_local_domain(affector_spec)
                affectee_fits = affector_spec.item._fit,
                return getter(
                    self, affector_spec, affectee_domain, affectee_fits)
        except Exception as e:
            self.__handle_affector_spec_errors(e, affector_spec)
            return ()

    def get_projected_affectee_items(self, affector_spec, tgt_items):
        """Get iterable with items influenced by projected affector spec."""
        affectee_filter = affector_spec.modifier.affectee_filter
        # Return targeted items when modification affects just them directly
        if affectee_filter == ModAffecteeFilter.item:
            return {i for i in tgt_items if i in self.__affectees}
        # En-masse modifications of items located on targeted items use shared
        # affectee item getters
        else:
            try:
                getter = self.__affectees_getters[affectee_filter]
            except KeyError as e:
                raise UnknownAffecteeFilterError(affectee_filter) from e
            affectee_fits = {i._fit for i in tgt_items if isinstance(i, Ship)}
            return getter(self, affector_spec, ModDomain.ship, affectee_fits)

    def get_affector_specs(self, affectee_item):
        """Get all affector specs, which influence passed item."""
        affectee_fit = affectee_item._fit
        affector_specs = set()
        # Item
        affector_storage = self.__affectors_item_active
        key = affectee_item
        affector_specs.update(affector_storage.get(key, ()))
        affectee_domain = affectee_item._modifier_domain
        if affectee_domain is not None:
            # Domain
            affector_storage = self.__affectors_domain
            key = (affectee_fit, affectee_domain)
            affector_specs.update(affector_storage.get(key, ()))
            # Domain and group
            affector_storage = self.__affectors_domain_group
            key = (affectee_fit, affectee_domain, affectee_item._type.group_id)
            affector_specs.update(affector_storage.get(key, ()))
            # Domain and skill requirement
            affector_storage = self.__affectors_domain_skillrq
            for affectee_srq_type_id in affectee_item._type.required_skills:
                key = (affectee_fit, affectee_domain, affectee_srq_type_id)
                affector_specs.update(affector_storage.get(key, ()))
        # Owner-modifiable and skill requirement
        if affectee_item._owner_modifiable:
            affector_storage = self.__affectors_owner_skillrq
            for affectee_srq_type_id in affectee_item._type.required_skills:
                key = (affectee_fit, affectee_srq_type_id)
                affector_specs.update(affector_storage.get(key, ()))
        return affector_specs

    # Maintenance methods
    def register_affectee_item(self, affectee_item):
        """Add passed affectee item to the register.

        We track affectee items to efficiently update attributes when set of
        items influencing them changes.
        """
        self.__affectees.add(affectee_item)
        affectee_fit = affectee_item._fit
        for key, storage in self.__get_affectee_storages(
            affectee_fit, affectee_item
        ):
            storage.add_data_entry(key, affectee_item)
        # Process special affector specs separately. E.g., when item like ship
        # is added, there might already be affector specs which should affect
        # it, and in this method we activate such affector specs
        self.__activate_special_affector_specs(affectee_fit, affectee_item)

    def unregister_affectee_item(self, affectee_item):
        """Remove passed affectee item from the register."""
        self.__affectees.remove(affectee_item)
        affectee_fit = affectee_item._fit
        for key, storage in self.__get_affectee_storages(
            affectee_fit, affectee_item
        ):
            storage.rm_data_entry(key, affectee_item)
        # Deactivate all special affector specs for item being unregistered
        self.__deactivate_special_affector_specs(affectee_fit, affectee_item)

    def register_local_affector_spec(self, affector_spec):
        """Make the register aware of the local affector spec.

        It makes it possible for the affector spec to modify other items within
        its fit.
        """
        try:
            storages = self.__get_local_affector_storages(affector_spec)
        except Exception as e:
            self.__handle_affector_spec_errors(e, affector_spec)
        else:
            for key, storage in storages:
                storage.add_data_entry(key, affector_spec)

    def unregister_local_affector_spec(self, affector_spec):
        """Remove local affector spec from the register.

        It makes it impossible for the affector spec to modify any items.
        """
        try:
            storages = self.__get_local_affector_storages(affector_spec)
        except Exception as e:
            self.__handle_affector_spec_errors(e, affector_spec)
        else:
            for key, storage in storages:
                storage.rm_data_entry(key, affector_spec)

    def register_projected_affector_spec(self, affector_spec, tgt_items):
        """Make register aware that projected affector spec affects items.

        Should be called every time projected effect with modifiers is applied
        onto any items.
        """
        try:
            storages = self.__get_projected_affector_storages(
                affector_spec, tgt_items)
        except Exception as e:
            self.__handle_affector_spec_errors(e, affector_spec)
        else:
            for key, storage in storages:
                storage.add_data_entry(key, affector_spec)

    def unregister_projected_affector(self, affector_spec, tgt_items):
        """Remove effect of affector spec from items.

        Should be called every time projected effect with modifiers stops
        affecting any object.
        """
        try:
            storages = self.__get_projected_affector_storages(
                affector_spec, tgt_items)
        except Exception as e:
            self.__handle_affector_spec_errors(e, affector_spec)
        else:
            for key, storage in storages:
                storage.rm_data_entry(key, affector_spec)

    # Helpers for affectee getter
    def __get_local_affectees_self(self, affector_spec):
        return affector_spec.item,

    def __get_local_affectees_character(self, affector_spec):
        affectee_fit = affector_spec.item._fit
        affectee_character = affectee_fit.character
        if affectee_character in self.__affectees:
            return affectee_character,
        else:
            return ()

    def __get_local_affectees_ship(self, affector_spec):
        affectee_fit = affector_spec.item._fit
        affectee_ship = affectee_fit.ship
        if affectee_ship in self.__affectees:
            return affectee_ship,
        else:
            return ()

    def __get_local_affectees_other(self, affector_spec):
        return [i for i in affector_spec.item._others if i in self.__affectees]

    __local_affectees_getters = {
        ModDomain.self: __get_local_affectees_self,
        ModDomain.character: __get_local_affectees_character,
        ModDomain.ship: __get_local_affectees_ship,
        ModDomain.other: __get_local_affectees_other}

    def __get_affectees_domain(self, _, affectee_domain, affectee_fits):
        affectee_items = set()
        storage = self.__affectees_domain
        for affectee_fit in affectee_fits:
            key = (affectee_fit, affectee_domain)
            affectee_items.update(storage.get(key, ()))
        return affectee_items

    def __get_affectees_domain_group(
        self, affector_spec, affectee_domain, affectee_fits
    ):
        affectee_group_id = affector_spec.modifier.affectee_filter_extra_arg
        affectee_items = set()
        storage = self.__affectees_domain_group
        for affectee_fit in affectee_fits:
            key = (affectee_fit, affectee_domain, affectee_group_id)
            affectee_items.update(storage.get(key, ()))
        return affectee_items

    def __get_affectees_domain_skillrq(
        self, affector_spec, affectee_domain, affectee_fits
    ):
        affectee_srq_type_id = affector_spec.modifier.affectee_filter_extra_arg
        if affectee_srq_type_id == EosTypeId.current_self:
            affectee_srq_type_id = affector_spec.item._type_id
        affectee_items = set()
        storage = self.__affectees_domain_skillrq
        for affectee_fit in affectee_fits:
            key = (affectee_fit, affectee_domain, affectee_srq_type_id)
            affectee_items.update(storage.get(key, ()))
        return affectee_items

    def __get_affectees_owner_skillrq(self, affector_spec, _, affectee_fits):
        affectee_srq_type_id = affector_spec.modifier.affectee_filter_extra_arg
        if affectee_srq_type_id == EosTypeId.current_self:
            affectee_srq_type_id = affector_spec.item._type_id
        affectee_items = set()
        storage = self.__affectees_owner_skillrq
        for affectee_fit in affectee_fits:
            key = (affectee_fit, affectee_srq_type_id)
            affectee_items.update(storage.get(key, ()))
        return affectee_items

    __affectees_getters = {
        ModAffecteeFilter.domain: __get_affectees_domain,
        ModAffecteeFilter.domain_group: __get_affectees_domain_group,
        ModAffecteeFilter.domain_skillrq: __get_affectees_domain_skillrq,
        ModAffecteeFilter.owner_skillrq: __get_affectees_owner_skillrq}

    # Helpers for affectee registering/unregistering
    def __get_affectee_storages(self, affectee_fit, affectee_item):
        """Return all places where passed affectee item should be stored.

        Returns:
            Iterable with multiple elements, where each element is tuple in
            (key, affectee map) format.
        """
        storages = []
        affectee_domain = affectee_item._modifier_domain
        if affectee_domain is not None:
            # Domain
            key = (affectee_fit, affectee_domain)
            storage = self.__affectees_domain
            storages.append((key, storage))
            # Domain and group
            affectee_group_id = affectee_item._type.group_id
            if affectee_group_id is not None:
                key = (affectee_fit, affectee_domain, affectee_group_id)
                storage = self.__affectees_domain_group
                storages.append((key, storage))
            # Domain and skill requirement
            storage = self.__affectees_domain_skillrq
            for affectee_srq_type_id in affectee_item._type.required_skills:
                key = (affectee_fit, affectee_domain, affectee_srq_type_id)
                storages.append((key, storage))
        # Owner-modifiable and skill requirement
        if affectee_item._owner_modifiable:
            storage = self.__affectees_owner_skillrq
            for affectee_srq_type_id in affectee_item._type.required_skills:
                key = (affectee_fit, affectee_srq_type_id)
                storages.append((key, storage))
        return storages

    def __activate_special_affector_specs(self, affectee_fit, affectee_item):
        """Activate special affector specs which should affect passed item."""
        awaiting_to_activate = set()
        for affector_spec in self.__affectors_item_awaiting.get(
            affectee_fit, ()
        ):
            affectee_domain = affector_spec.modifier.affectee_domain
            # Ship
            if (
                affectee_domain == ModDomain.ship and
                isinstance(affectee_item, Ship)
            ):
                awaiting_to_activate.add(affector_spec)
            # Character
            elif (
                affectee_domain == ModDomain.character and
                isinstance(affectee_item, Character)
            ):
                awaiting_to_activate.add(affector_spec)
            # Self
            elif (
                affectee_domain == ModDomain.self and
                affectee_item is affector_spec.item
            ):
                awaiting_to_activate.add(affector_spec)
        # Move awaiting affector specs from awaiting storage to active storage
        if awaiting_to_activate:
            self.__affectors_item_awaiting.rm_data_set(
                affectee_fit, awaiting_to_activate)
            self.__affectors_item_active.add_data_set(
                affectee_item, awaiting_to_activate)
        # Other
        other_to_activate = set()
        for affector_item, affector_specs in (
            self.__affectors_item_other.items()
        ):
            if affectee_item in affector_item._others:
                other_to_activate.update(affector_specs)
        # Just add affector specs to active storage, 'other' affector specs
        # should never be removed from 'other'-specific storage
        if other_to_activate:
            self.__affectors_item_active.add_data_set(
                affectee_item, other_to_activate)

    def __deactivate_special_affector_specs(self, affectee_fit, affectee_item):
        """Deactivate special affector specs which affect passed item."""
        if affectee_item not in self.__affectors_item_active:
            return
        awaitable_to_deactivate = set()
        for affector_spec in (
            self.__affectors_item_active.get(affectee_item, ())
        ):
            if affector_spec.modifier.affectee_domain in (
                ModDomain.ship, ModDomain.character, ModDomain.self
            ):
                awaitable_to_deactivate.add(affector_spec)
        # Remove all affector specs influencing this item directly, including
        # 'other' affectors
        del self.__affectors_item_active[affectee_item]
        # And make sure awaitable affectors become awaiting - moved to
        # appropriate container for future use
        if awaitable_to_deactivate:
            self.__affectors_item_awaiting.add_data_set(
                affectee_fit, awaitable_to_deactivate)

    # Helpers for affector spec registering/unregistering
    def __get_local_affector_storages(self, affector_spec):
        """Get places where passed local affector spec should be stored.

        Raises:
            UnexpectedDomainError: If modifier affectee domain is not supported
                for context of passed affector spec.
            UnknownAffecteeFilterError: If modifier affectee filter type is not
                supported.
        """
        affectee_filter = affector_spec.modifier.affectee_filter
        if affectee_filter == ModAffecteeFilter.item:
            affectee_domain = affector_spec.modifier.affectee_domain
            try:
                getter = self.__local_affector_storages_getters[affectee_domain]
            except KeyError as e:
                raise UnexpectedDomainError(affectee_domain) from e
            return getter(self, affector_spec)
        else:
            try:
                getter = self.__affector_storages_getters[affectee_filter]
            except KeyError as e:
                raise UnknownAffecteeFilterError(affectee_filter) from e
            affectee_domain = self.__resolve_local_domain(affector_spec)
            affectee_fits = affector_spec.item._fit,
            return getter(self, affector_spec, affectee_domain, affectee_fits)

    def __get_projected_affector_storages(self, affector_spec, tgt_items):
        """Get places where passed projected affector spec should be stored.

        Raises:
            UnknownAffecteeFilterError: If modifier affectee filter type is not
                supported.
        """
        affectee_filter = affector_spec.modifier.affectee_filter
        # Modifier affects just targeted items directly
        if affectee_filter == ModAffecteeFilter.item:
            storages = []
            storage = self.__affectors_item_active
            for tgt_item in tgt_items:
                if tgt_item in self.__affectees:
                    key = tgt_item
                    storages.append((key, storage))
            return storages
        # Modifier affects multiple items via affectee filter
        else:
            try:
                getter = self.__affector_storages_getters[affectee_filter]
            except KeyError as e:
                raise UnknownAffecteeFilterError(affectee_filter) from e
            affectee_domain = ModDomain.ship
            affectee_fits = {i._fit for i in tgt_items if isinstance(i, Ship)}
            return getter(self, affector_spec, affectee_domain, affectee_fits)

    def __get_local_affector_storages_self(self, affector_spec):
        affectee_item = affector_spec.item
        if affectee_item in self.__affectees:
            key = affectee_item
            storage = self.__affectors_item_active
        else:
            key = affectee_item._fit
            storage = self.__affectors_item_awaiting
        return (key, storage),

    def __get_local_affector_storages_character(self, affector_spec):
        affectee_fit = affector_spec.item._fit
        affectee_character = affectee_fit.character
        if affectee_character in self.__affectees:
            key = affectee_character
            storage = self.__affectors_item_active
        else:
            key = affectee_fit
            storage = self.__affectors_item_awaiting
        return (key, storage),

    def __get_local_affector_storages_ship(self, affector_spec):
        affectee_fit = affector_spec.item._fit
        affectee_ship = affectee_fit.ship
        if affectee_ship in self.__affectees:
            key = affectee_ship
            storage = self.__affectors_item_active
        else:
            key = affectee_fit
            storage = self.__affectors_item_awaiting
        return (key, storage),

    def __get_local_affector_storages_other(self, affector_spec):
        # Affectors with 'other' modifiers are always stored in their special
        # place
        storages = [(affector_spec.item, self.__affectors_item_other)]
        # And all those which have valid affectee item are also stored in
        # storage for active direct affectors
        storage = self.__affectors_item_active
        for other_item in affector_spec.item._others:
            if other_item in self.__affectees:
                key = other_item
                storages.append((key, storage))
        return storages

    __local_affector_storages_getters = {
        ModDomain.self: __get_local_affector_storages_self,
        ModDomain.character: __get_local_affector_storages_character,
        ModDomain.ship: __get_local_affector_storages_ship,
        ModDomain.other: __get_local_affector_storages_other}

    def __get_affector_storages_domain(self, _, affectee_domain, affectee_fits):
        storages = []
        storage = self.__affectors_domain
        for affectee_fit in affectee_fits:
            key = (affectee_fit, affectee_domain)
            storages.append((key, storage))
        return storages

    def __get_affector_storages_domain_group(
        self, affector_spec, affectee_domain, affectee_fits
    ):
        affectee_group_id = affector_spec.modifier.affectee_filter_extra_arg
        storages = []
        storage = self.__affectors_domain_group
        for affectee_fit in affectee_fits:
            key = (affectee_fit, affectee_domain, affectee_group_id)
            storages.append((key, storage))
        return storages

    def __get_affector_storages_domain_skillrq(
        self, affector_spec, affectee_domain, affectee_fits
    ):
        affectee_srq_type_id = affector_spec.modifier.affectee_filter_extra_arg
        if affectee_srq_type_id == EosTypeId.current_self:
            affectee_srq_type_id = affector_spec.item._type_id
        storages = []
        storage = self.__affectors_domain_skillrq
        for affectee_fit in affectee_fits:
            key = (affectee_fit, affectee_domain, affectee_srq_type_id)
            storages.append((key, storage))
        return storages

    def __get_affector_storages_owner_skillrq(
        self, affector_spec, _, affectee_fits
    ):
        affectee_srq_type_id = affector_spec.modifier.affectee_filter_extra_arg
        if affectee_srq_type_id == EosTypeId.current_self:
            affectee_srq_type_id = affector_spec.item._type_id
        storages = []
        storage = self.__affectors_owner_skillrq
        for affectee_fit in affectee_fits:
            key = (affectee_fit, affectee_srq_type_id)
            storages.append((key, storage))
        return storages

    __affector_storages_getters = {
        ModAffecteeFilter.domain:
            __get_affector_storages_domain,
        ModAffecteeFilter.domain_group:
            __get_affector_storages_domain_group,
        ModAffecteeFilter.domain_skillrq:
            __get_affector_storages_domain_skillrq,
        ModAffecteeFilter.owner_skillrq:
            __get_affector_storages_owner_skillrq}

    # Shared helpers
    def __resolve_local_domain(self, affector_spec):
        """Convert relative domain into absolute for local affector spec.

        Applicable only to en-masse modifications - that is, when modification
        affects multiple items in affectee domain.

        Raises:
            UnexpectedDomainError: If modifier affectee domain is not supported.
        """
        affector_item = affector_spec.item
        affectee_domain = affector_spec.modifier.affectee_domain
        if affectee_domain == ModDomain.self:
            if isinstance(affector_item, Ship):
                return ModDomain.ship
            elif isinstance(affector_item, Character):
                return ModDomain.character
            else:
                raise UnexpectedDomainError(affectee_domain)
        # Just return untouched domain for all other valid cases. Valid cases
        # include 'globally' visible (within the fit scope) domains only. I.e.
        # if item on fit refers this affectee domain, it should always refer the
        # same affectee item regardless of position of source item.
        elif affectee_domain in (ModDomain.character, ModDomain.ship):
            return affectee_domain
        # Raise error if domain is invalid
        else:
            raise UnexpectedDomainError(affectee_domain)

    def __handle_affector_spec_errors(self, error, affector_spec):
        """Handles exceptions related to affector spec.

        Multiple register methods which get data based on passed affector spec
        raise similar exceptions. To handle them in consistent fashion, it is
        done from this method. If error cannot be handled by the method, it is
        re-raised.
        """
        if isinstance(error, UnexpectedDomainError):
            msg = (
                'malformed modifier on item type {}: '
                'unsupported affectee domain {}'
            ).format(affector_spec.item._type_id, error.args[0])
            logger.warning(msg)
        elif isinstance(error, UnknownAffecteeFilterError):
            msg = (
                'malformed modifier on item type {}: invalid affectee filter {}'
            ).format(affector_spec.item._type_id, error.args[0])
            logger.warning(msg)
        else:
            raise error
