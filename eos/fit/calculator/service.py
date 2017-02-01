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
from eos.data.cache_object.modifier import DogmaModifier, ModificationCalculationError
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
    Class which collects data about fit item and with
    its help assists modified attribute map with attribute
    value calculation.

    Required arguments:
    fit -- Fit object to which service is assigned
    """

    def __init__(self, fit):
        self.__enabled = False
        self.__fit = fit
        self.__affections = AffectionRegister(fit)
        # Container with affectors which will receive messages
        # Format: {message type: set(affectors)}
        self.__subscribed_affectors = KeyedSet()
        fit._subscribe(self, self._handler_map.keys())

    def get_modifications(self, target_item, target_attr):
        """
        Get modifications of target attr on target item.

        Required arguments:
        target_item -- item, for which we're getting modifications
        target_attr -- target attribute ID; only modifications which
            influence attribute with this ID will be returned.

        Return value:
        set((operator, modification value, source item))
        """
        modifications = set()
        for source_item, modifier in self.__affections.get_affectors(target_item):
            if modifier.tgt_attr == target_attr:
                try:
                    mod_oper, mod_value = modifier.get_modification(source_item, self.__fit)
                # Do nothing here - errors should be logged in modification getter
                except ModificationCalculationError:
                    continue
                modifications.add((mod_oper, mod_value, source_item))
        return modifications

    # Handle item addition/removal
    def _handle_item_addition(self, message):
        self.__add_item(message.item)

    def _handle_item_removal(self, message):
        self.__remove_item(message.item)

    def __add_item(self, item):
        """Make service aware of fit item"""
        self.__affections.register_affectee(item)
        self.__enable_affectors(self.__generate_affectors(
            item, effect_filter=item._enabled_effects,
            state_filter=set(filter(lambda s: s <= item.state, State))
        ))

    def __remove_item(self, item):
        """Make service to forget about fit item"""
        self.__disable_affectors(self.__generate_affectors(
            item, effect_filter=item._enabled_effects,
            state_filter=set(filter(lambda s: s <= item.state, State))
        ))
        self.__affections.unregister_affectee(item)

    # Handle item changes which are significant for calculator
    def _handle_item_state_change(self, message):
        """
        Enable/disable affectors based on state change direction.
        """
        item, old_state, new_state = message
        if new_state > old_state:
            self.__enable_affectors(self.__generate_affectors(
                item, effect_filter=item._enabled_effects,
                state_filter=set(filter(lambda s: old_state < s <= new_state, State))
            ))
        elif new_state < old_state:
            self.__disable_affectors(self.__generate_affectors(
                item, effect_filter=item._enabled_effects,
                state_filter=set(filter(lambda s: new_state < s <= old_state, State))
            ))

    def _handle_item_effects_enabling(self, message):
        """
        Enable effects carried by the item.
        """
        affectors = self.__generate_affectors(
            message.item, effect_filter=message.effects,
            state_filter=set(filter(lambda s: s <= message.item.state, State))
        )
        self.__enable_affectors(affectors)

    def _handle_item_effects_disabling(self, message):
        """
        Disable effects carried by the item.
        """
        affectors = self.__generate_affectors(
            message.item, effect_filter=message.effects,
            state_filter=set(filter(lambda s: s <= message.item.state, State))
        )
        self.__disable_affectors(affectors)

    # Methods to clear calculated child nodes when parent nodes change
    def _revise_regular_attrib_dependents(self, message):
        """
        Remove all calculated attribute values which rely on passed
        attribute of passed item - it allows these values to be
        recalculated. Here we process all regular dependents, which
        include dependencies specified via capped attribute map and
        via affectors with dogma modifiers. Affectors with python
        modifiers are processed separately.
        """
        item, attr = message
        # Remove values of target attributes capped by changing attribute
        for capped_attr in (item.attributes._cap_map.get(attr) or ()):
            del item.attributes[capped_attr]
        # Remove values of target attributes which are using changing attribute
        # as modification source
        for affector in self.__generate_affectors(
            item, effect_filter=item._enabled_effects,
            state_filter=set(filter(lambda s: s <= item.state, State))
        ):
            modifier = affector.modifier
            # Only dogma modifiers have source attribute specified,
            # python modifiers are processed separately
            if not isinstance(modifier, DogmaModifier) or modifier.src_attr != attr:
                continue
            for target_item in self.__affections.get_affectees(affector):
                del target_item.attributes[modifier.tgt_attr]

    def _revise_python_attrib_dependents(self, message):
        """
        Remove all calculated attribute values which depend on affectors
        with python modifier, in case modifier positively decides on it.
        """
        # If there's no affector-subscribers for received
        # message type, do nothing
        msg_type = type(message)
        if msg_type not in self.__subscribed_affectors:
            return
        # Otherwise, ask affector if target value should
        # change, and remove it if it should
        for affector in self.__subscribed_affectors[msg_type]:
            if affector.modifier.revise_modification(message, affector.source_item, self.__fit) is not True:
                continue
            for target_item in self.__affections.get_affectees(affector):
                del target_item.attributes[affector.modifier.tgt_attr]

    # Service state management
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

    # Message routing
    _handler_map = {
        ItemAdded: _handle_item_addition,
        ItemRemoved: _handle_item_removal,
        ItemStateChanged: _handle_item_state_change,
        EffectsEnabled: _handle_item_effects_enabling,
        EffectsDisabled: _handle_item_effects_disabling,
        AttrValueChanged: _revise_regular_attrib_dependents,
        AttrValueChangedOverride: _revise_regular_attrib_dependents,
        EnableServices: _handle_enable_services,
        DisableServices: _handle_disable_services
    }

    def _notify(self, message):
        # When service is disabled, we are processing
        # only message which enables it
        if not self.__enabled and type(message) is not EnableServices:
            return
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            pass
        else:
            handler(self, message)
        # Relay all messages to python modifiers, as in case of python
        # modifiers any message may result in deleting dependent attrs
        self._revise_python_attrib_dependents(message)

    # Do not process here just target domain
    _supported_domains = set(filter(lambda d: d != ModifierDomain.target, ModifierDomain))

    # Affector generation and manipulation
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

    def __enable_affectors(self, affectors):
        """
        Enable effect of affectors on their target items.

        Required arguments:
        affectors -- iterable with affectors to enable
        """
        # Clear attributes only after registration jobs
        for affector in affectors:
            self.__affections.register_affector(affector)
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
            self.__affections.unregister_affector(affector)

    def __clear_affectors_dependents(self, affectors):
        """
        Clear calculated attributes which are relying on
        passed affectors.

        Required arguments:
        affectors -- iterable with affectors in question
        src_attr -- clear dependents which rely on this attribute only
        """
        for affector in affectors:
            # Go through all items targeted by modifier
            for target_item in self.__affections.get_affectees(affector):
                # And remove target attribute
                del target_item.attributes[affector.modifier.tgt_attr]

    # Python affector subscription/unsubscription
    def __subscribe_affector(self, affector):
        """Subscribe python affector to message types it wants"""
        if not isinstance(affector.modifier, BasePythonModifier):
            return
        to_subscribe = set()
        for msg_type in affector.modifier.revise_message_types:
            # Subscribe service to new message type only if there's
            # no such subscription yet
            if msg_type not in self._handler_map and msg_type not in self.__subscribed_affectors:
                to_subscribe.add(msg_type)
            # Add affector to subscriber map to let it receive messages
            self.__subscribed_affectors.add_data(msg_type, affector)
        self.__fit._subscribe(self, to_subscribe)

    def __unsubscribe_affector(self, affector):
        """Unsubscribe python affector"""
        if not isinstance(affector.modifier, BasePythonModifier):
            return
        to_ubsubscribe = set()
        for msg_type in affector.modifier.revise_message_types:
            # Make sure affector will not receive messages anymore
            self.__subscribed_affectors.rm_data(msg_type, affector)
            # Unsubscribe service from message type if there're no
            # recipients anymore
            if msg_type not in self._handler_map and msg_type not in self.__subscribed_affectors:
                to_ubsubscribe.add(msg_type)
        self.__fit._unsubscribe(self, to_ubsubscribe)
