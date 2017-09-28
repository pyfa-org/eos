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


from eos.const.eos import ModifierDomain
from eos.eve_object.modifier import DogmaModifier, ModificationCalculationError
from eos.eve_object.modifier.python import BasePythonModifier
from eos.fit.item import Character, Ship
from eos.fit.pubsub.message import (
    InstrItemAdd, InstrItemRemove, InstrEffectsActivate, InstrEffectsDeactivate,
    InstrAttrValueChanged
)
from eos.fit.pubsub.subscriber import BaseSubscriber
from eos.util.keyed_set import KeyedSet

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

    def __init__(self, msg_broker):
        self._current_char = None
        self._current_ship = None
        self.__affections = AffectionRegister(self)
        # Container with affectors which will receive messages
        # Format: {message type: set(affectors)}
        self.__subscribed_affectors = KeyedSet()
        self.__msg_broker = msg_broker
        msg_broker._subscribe(self, self._handler_map.keys())

    def get_modifications(self, target_item, target_attr):
        """
        Get modifications of target attr on target item.

        Required arguments:
        target_item -- item, for which we're getting modifications
        target_attr -- target attribute ID; only modifications which
            influence attribute with this ID will be returned.

        Return value:
        set((operator, modification value, carrier item))
        """
        modifications = set()
        for modifier, carrier_item in self.__affections.get_affectors(target_item):
            if modifier.tgt_attr == target_attr:
                try:
                    mod_oper, mod_value = modifier.get_modification(carrier_item, self._current_ship)
                # Do nothing here - errors should be logged in modification getter
                # or even earlier
                except ModificationCalculationError:
                    continue
                modifications.add((mod_oper, mod_value, carrier_item))
        return modifications

    # Handle item changes which are significant for calculator
    def _handle_item_addition(self, message):
        if isinstance(message.item, Character):
            self._current_char = message.item
        elif isinstance(message.item, Ship):
            self._current_ship = message.item
        self.__affections.register_affectee(message.item)

    def _handle_item_removal(self, message):
        if message.item is self._current_char:
            self._current_char = None
        elif message.item is self._current_ship:
            self._current_ship = None
        self.__affections.unregister_affectee(message.item)

    def _handle_item_effects_activation(self, message):
        affectors = self.__generate_affectors(message.item, message.effects)
        for affector in affectors:
            self.__subscribe_affector(affector)
            self.__affections.register_affector(affector)
            for target_item in self.__affections.get_affectees(affector):
                del target_item.attributes[affector.modifier.tgt_attr]

    def _handle_item_effects_deactivation(self, message):
        affectors = self.__generate_affectors(message.item, message.effects)
        for affector in affectors:
            for target_item in self.__affections.get_affectees(affector):
                del target_item.attributes[affector.modifier.tgt_attr]
            self.__affections.unregister_affector(affector)
            self.__unsubscribe_affector(affector)

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
        # Remove values of target attributes capped by changing attribute
        for capped_attr in (message.item.attributes._cap_map.get(message.attr, ())):
            del message.item.attributes[capped_attr]
        # Remove values of target attributes which are using changing attribute
        # as modification source
        for affector in self.__generate_affectors(message.item, message.item._active_effects.keys()):
            modifier = affector.modifier
            # Only dogma modifiers have source attribute specified,
            # python modifiers are processed separately
            if not isinstance(modifier, DogmaModifier) or modifier.src_attr != message.attr:
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
            if affector.modifier.revise_modification(
                message, affector.carrier_item, self._current_ship
            ) is not True:
                continue
            for target_item in self.__affections.get_affectees(affector):
                del target_item.attributes[affector.modifier.tgt_attr]

    # Message routing
    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal,
        InstrEffectsActivate: _handle_item_effects_activation,
        InstrEffectsDeactivate: _handle_item_effects_deactivation,
        InstrAttrValueChanged: _revise_regular_attrib_dependents
    }

    def _notify(self, message):
        BaseSubscriber._notify(self, message)
        # Relay all messages to python modifiers, as in case of python
        # modifiers any message may result in deleting dependent attrs
        self._revise_python_attrib_dependents(message)

    # Do not process here just target domain
    _supported_domains = set(filter(lambda d: d != ModifierDomain.target, ModifierDomain))

    # Affector generation and manipulation
    def __generate_affectors(self, item, effect_ids):
        """
        Get all affectors spawned by the item.

        Required arguments:
        item -- item, for which affectors are generated
        effect_ids -- iterable with effect IDs, for which
            affectors should be generated

        Return value:
        Set with Affector objects
        """
        affectors = set()
        for effect_id, effect in item._eve_type.effects.items():
            if effect_id not in effect_ids:
                continue
            for modifier in effect.modifiers:
                if modifier.tgt_domain not in CalculationService._supported_domains:
                    continue
                affector = Affector(modifier, item)
                affectors.add(affector)
        return affectors

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
        self.__msg_broker._subscribe(self, to_subscribe)

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
        self.__msg_broker._unsubscribe(self, to_ubsubscribe)
