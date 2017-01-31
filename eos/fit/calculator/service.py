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


from eos.const.eos import State, ModifierDomain
from eos.data.cache_object.modifier import ModificationCalculationError
from eos.data.cache_object.modifier.python import BasePythonModifier
from eos.fit.messages import (
    ItemAdded, ItemRemoved, ItemStateChanged, EffectsEnabled, EffectsDisabled,
    AttrValueChanged, AttrValueChangedOverride, EnableServices, DisableServices
)
from eos.util.keyed_set import KeyedSet
from eos.util.pubsub import BaseSubscriber
from .affector import Affector
from .register import AffectionRegister


class CalculationService(BaseSubscriber):
    """
    Serve as intermediate layer between fit and item link register.
    Implements methods which make it easier for fit to add, modify and
    remove items (by implementing higher-level logic which deals with
    state, scope and attribute filters), and exposes two main register
    getters for external use.

    Required arguments:
    fit -- Fit object to which service is assigned
    """

    def __init__(self, fit):
        self.__enabled = False
        self.__fit = fit
        self.__register = AffectionRegister(fit)
        # Container with affectors which are supposed to receive messages
        # Format: {message type: set(affectors)}
        self.__affector_subs = KeyedSet()
        fit._subscribe(self, self._handler_map.keys())

    # Do not process here just target domain
    _supported_domains = set(filter(lambda d: d != ModifierDomain.target, ModifierDomain))

    def get_modifications(self, target_item, target_attr):
        """
        Get modifications of attr on item.

        Required arguments:
        target_item -- item, for which we're getting modifications
        target_attr -- target attribute ID, only modifications which
            influence attribute with this ID will be returned.

        Return value:
        set((operator, modification value, source item))
        """
        modifications = set()
        for source_item, modifier in self.__register.get_affectors(target_item):
            if modifier.tgt_attr == target_attr:
                try:
                    mod_oper, mod_value = modifier.get_modification(source_item, self.__fit)
                # Do nothing here - errors should be logged in modification getter
                except ModificationCalculationError:
                    continue
                modifications.add((mod_oper, mod_value, source_item))
        return modifications

    def get_affectees(self, affector):
        """
        Get affectees being influenced by the affector.

        Required arguments:
        affector -- affector, for which we're getting affectees

        Return value:
        Set with items
        """
        return self.__register.get_affectees(affector)

    # Message handling
    def _handle_item_addition(self, message):
        """
        Put the item under influence of registered affectors
        and enable its affectors according to its state.
        """
        if not self.__enabled:
            return
        self.__add_item(message.item)

    def _handle_item_removal(self, message):
        """
        Disable item affectors and remove it from influence
        of of registered affectors.
        """
        if not self.__enabled:
            return
        self.__remove_item(message.item)

    def _handle_item_state_change(self, message):
        """
        Enable/disable affectors based on state change direction.
        """
        if not self.__enabled:
            return
        item, old_state, new_state = message
        if new_state > old_state:
            states = set(filter(lambda s: old_state < s <= new_state, State))
            self.__enable_states(item, states)
        elif new_state < old_state:
            states = set(filter(lambda s: new_state < s <= old_state, State))
            self.__disable_states(item, states)

    def _handle_item_effects_enabling(self, message):
        """
        Enable effects carried by the item.
        """
        if not self.__enabled:
            return
        affectors = self.__generate_affectors(
            message.item, effect_filter=message.effects,
            state_filter=set(filter(lambda s: s <= message.item.state, State))
        )
        self.__enable_affectors(affectors)

    def _handle_item_effects_disabling(self, message):
        """
        Disable effects carried by the item.
        """
        if not self.__enabled:
            return
        affectors = self.__generate_affectors(
            message.item, effect_filter=message.effects,
            state_filter=set(filter(lambda s: s <= message.item.state, State))
        )
        self.__disable_affectors(affectors)

    def _clear_item_attribute_dependents(self, message):
        """
        Clear calculated attributes relying on the attribute of a item.
        """
        item, attr = message
        # Clear attributes capped by this attribute
        for capped_attr in (item.attributes._cap_map.get(attr) or ()):
            del item.attributes[capped_attr]
        # Clear attributes which are using this attribute as modification source
        affectors = self.__generate_affectors(
            item, effect_filter=item._enabled_effects,
            state_filter=set(filter(lambda s: s <= message.item.state, State))
        )
        self.__clear_affectors_dependents(affectors, src_attr=attr)

    def _handle_enable_services(self, message):
        """
        Enable service and register passed items.
        """
        self.__enabled = True
        for item in message.items:
            self.__add_item(item)

    def _handle_disable_services(self, message):
        """
        Unregister passed items from this service and
        disable it.
        """
        for item in message.items:
            self.__remove_item(item)
        self.__enabled = False

    _handler_map = {
        ItemAdded: _handle_item_addition,
        ItemRemoved: _handle_item_removal,
        ItemStateChanged: _handle_item_state_change,
        EffectsEnabled: _handle_item_effects_enabling,
        EffectsDisabled: _handle_item_effects_disabling,
        AttrValueChanged: _clear_item_attribute_dependents,
        AttrValueChangedOverride: _clear_item_attribute_dependents,
        EnableServices: _handle_enable_services,
        DisableServices: _handle_disable_services
    }

    def _notify(self, message):
        try:
            recipient_affectors = self.__affector_subs[type(message)]
        except KeyError:
            pass
        else:
            for affector in recipient_affectors:
                if affector.modifier.is_triggered(message, affector.source_item, self.__fit) is True:
                    for target_item in self.get_affectees(affector):
                        del target_item.attributes[affector.modifier.tgt_attr]
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            pass
        else:
            handler(self, message)

    # Private methods for message handlers
    def __add_item(self, item):
        self.__register.register_affectee(item)
        states = set(filter(lambda s: s <= item.state, State))
        self.__enable_states(item, states)

    def __remove_item(self, item):
        states = set(filter(lambda s: s <= item.state, State))
        self.__disable_states(item, states)
        self.__register.unregister_affectee(item)

    def __enable_states(self, item, states):
        """
        Handle state switch upwards.

        Required arguments:
        item -- item, for which states are switched
        states -- iterable with states, which are passed
            during state switch, except for initial state
        """
        affectors = self.__generate_affectors(
            item, effect_filter=item._enabled_effects, state_filter=states
        )
        self.__enable_affectors(affectors)

    def __disable_states(self, item, states):
        """
        Handle state switch downwards.

        Required arguments:
        item -- item, for which states are switched
        states -- iterable with states, which are passed
            during state switch, except for final state
        """
        affectors = self.__generate_affectors(
            item, effect_filter=item._enabled_effects, state_filter=states
        )
        self.__disable_affectors(affectors)

    def __enable_affectors(self, affectors):
        """
        Enable effect of affectors on their target items.

        Required arguments:
        affectors -- iterable with affectors to enable
        """
        # Clear attributes only after registration jobs
        for affector in affectors:
            self.__register.register_affector(affector)
            self.__subscribe_affector(affector)
        self.__clear_affectors_dependents(affectors)

    def __disable_affectors(self, affectors):
        """
        Remove effect of affectors from their target items.

        Required arguments:
        affectors -- iterable with affectors to disable
        """
        # Clear attributes before unregistering, otherwise
        # we won't clean them up properly
        self.__clear_affectors_dependents(affectors)
        for affector in affectors:
            self.__unsubscribe_affector(affector)
            self.__register.unregister_affector(affector)

    def __clear_affectors_dependents(self, affectors, src_attr=None):
        """
        Clear calculated attributes which are relying on
        passed affectors.

        Required arguments:
        affectors -- iterable with affectors in question
        src_attr -- clear dependents which rely on this attribute only
        """
        for affector in affectors:
            modifier = affector.modifier
            if src_attr is not None and (isinstance(modifier, BasePythonModifier) or modifier.src_attr != src_attr):
                continue
            # Go through all items targeted by modifier
            for target_item in self.get_affectees(affector):
                # And remove target attribute
                del target_item.attributes[affector.modifier.tgt_attr]

    def __generate_affectors(self, item, effect_filter, state_filter):
        """
        Get all affectors spawned by the item.

        Required arguments:
        item -- item, for which affectors are generated

        Optional arguments:
        effect filter -- filter results to include affectors, which carry
            modifiers generated from effects with IDs on this list
        state_filter -- filter results by state required by affector's
            modifier, which should be in this iterable

        Return value:
        Set with Affector objects, satisfying passed filters
        """
        affectors = set()
        for effect in item._eve_type.effects:
            if effect.id not in effect_filter:
                continue
            for modifier in effect.modifiers:
                if modifier.state not in state_filter:
                    continue
                if modifier.tgt_domain not in self._supported_domains:
                    continue
                affector = Affector(item, modifier)
                affectors.add(affector)
        return affectors

    def __subscribe_affector(self, affector):
        if not isinstance(affector.modifier, BasePythonModifier):
            return
        to_subscribe = set()
        for msg_type in affector.modifier.trigger_message_types:
            if msg_type not in self._handler_map and msg_type not in self.__affector_subs:
                to_subscribe.add(msg_type)
            self.__affector_subs.add_data(msg_type, affector)
        self.__fit._subscribe(self, to_subscribe)

    def __unsubscribe_affector(self, affector):
        if not isinstance(affector.modifier, BasePythonModifier):
            return
        to_ubsubscribe = set()
        for msg_type in affector.modifier.trigger_message_types:
            self.__affector_subs.rm_data(msg_type, affector)
            if msg_type not in self._handler_map and msg_type not in self.__affector_subs:
                to_ubsubscribe.add(msg_type)
        self.__fit._unsubscribe(self, to_ubsubscribe)
