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


from eos.const.eos import ModifierDomain
from eos.eve_object.modifier import DogmaModifier, ModificationCalculationError
from eos.eve_object.modifier.python import BasePythonModifier
from eos.fit.item import Character, Ship
from eos.fit.pubsub.message import (
    InstrAttrValueChanged, InstrEffectsStart, InstrEffectsStop, InstrItemAdd,
    InstrItemRemove
)
from eos.fit.pubsub.subscriber import BaseSubscriber
from eos.util.keyed_set import KeyedSet
from .affector import Affector
from .register import AffectionRegister


class CalculationService(BaseSubscriber):
    """Service which supports attribute calculation.

    This class collects data about fit items and relations between them, and via
    exposed methods which provice data about these connections helps attribute
    map to calculate modified attribute values.
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
        """Get modifications of target attr on target item.

        Args:
            target_item: Item, for which we're getting modifications.
            target_attr: Target attribute ID; only modifications which influence
                attribute with this ID will be returned.

        Returns:
            Set with tuples in (operator, modification value, carrier item)
            format.
        """
        modifications = set()
        for affector in self.__affections.get_affectors(target_item):
            modifier, carrier_item = affector
            if modifier.tgt_attr == target_attr:
                try:
                    mod_oper, mod_value = modifier.get_modification(
                        carrier_item, self._current_ship)
                # Do nothing here - errors should be logged in modification
                # getter or even earlier
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
        """Remove calculated attribute values which rely on passed attribute.

        Removing them allows to recalculate updated value. Here we process all
        regular dependents, which include dependencies specified via capped
        attribute map and via affectors with dogma modifiers. Affectors with
        python modifiers are processed separately.
        """
        # Remove values of target attributes capped by changing attribute
        item = message.item
        attr = message.attr
        for capped_attr in item.attributes._cap_map.get(attr, ()):
            del item.attributes[capped_attr]
        # Remove values of target attributes which are using changing attribute
        # as modification source
        for affector in self.__generate_affectors(item, item._running_effects):
            modifier = affector.modifier
            # Only dogma modifiers have source attribute specified, python
            # modifiers are processed separately
            if (
                not isinstance(modifier, DogmaModifier) or
                modifier.src_attr != attr
            ):
                continue
            for target_item in self.__affections.get_affectees(affector):
                del target_item.attributes[modifier.tgt_attr]

    def _revise_python_attrib_dependents(self, message):
        """Remove calculated attribute values when necessary.

        Here we go through python modifiers, deliver to them message, and if,
        based on contents of the message, they decide that calculated values
        should be removed, we remove values which depend on such modifiers.
        """
        # If there's no affector-subscribers for received message type, do
        # nothing
        msg_type = type(message)
        if msg_type not in self.__subscribed_affectors:
            return
        # Otherwise, ask affector if target value should change, and remove it
        # if it should
        for affector in self.__subscribed_affectors[msg_type]:
            if not affector.modifier.revise_modification(
                message, affector.carrier_item, self._current_ship
            ):
                continue
            for target_item in self.__affections.get_affectees(affector):
                del target_item.attributes[affector.modifier.tgt_attr]

    # Message routing
    _handler_map = {
        InstrItemAdd: _handle_item_addition,
        InstrItemRemove: _handle_item_removal,
        InstrEffectsStart: _handle_item_effects_activation,
        InstrEffectsStop: _handle_item_effects_deactivation,
        InstrAttrValueChanged: _revise_regular_attrib_dependents
    }

    def _notify(self, message):
        BaseSubscriber._notify(self, message)
        # Relay all messages to python modifiers, as in case of python modifiers
        # any message may result in deleting dependent attrs
        self._revise_python_attrib_dependents(message)

    # Do not process here just target domain
    _supported_domains = set(
        d for d in ModifierDomain if d != ModifierDomain.target
    )

    # Affector generation and manipulation
    def __generate_affectors(self, item, effect_ids):
        """Get all affectors spawned by the item.

        Args:
            item: Item, for which affectors are generated.
            effect_ids: Iterable with effect IDs which should serve as filter
                for affectors. If affector's modifier is not part of effect from
                this iterable, it's filtered out.

        Return value:
            Set with Affector objects.
        """
        affectors = set()
        for effect_id, effect in item._eve_type.effects.items():
            if effect_id not in effect_ids:
                continue
            for modifier in effect.modifiers:
                if modifier.tgt_domain not in self._supported_domains:
                    continue
                affector = Affector(modifier, item)
                affectors.add(affector)
        return affectors

    # Python affector subscription/unsubscription
    def __subscribe_affector(self, affector):
        """Subscribe python affector to message types it wants."""
        if not isinstance(affector.modifier, BasePythonModifier):
            return
        to_subscribe = set()
        for msg_type in affector.modifier.revise_message_types:
            # Subscribe service to new message type only if there's no such
            # subscription yet
            if (
                msg_type not in self._handler_map and
                msg_type not in self.__subscribed_affectors
            ):
                to_subscribe.add(msg_type)
            # Add affector to subscriber map to let it receive messages
            self.__subscribed_affectors.add_data(msg_type, affector)
        self.__msg_broker._subscribe(self, to_subscribe)

    def __unsubscribe_affector(self, affector):
        """Unsubscribe python affector."""
        if not isinstance(affector.modifier, BasePythonModifier):
            return
        to_ubsubscribe = set()
        for msg_type in affector.modifier.revise_message_types:
            # Make sure affector will not receive messages anymore
            self.__subscribed_affectors.rm_data(msg_type, affector)
            # Unsubscribe service from message type if there're no recipients
            # anymore
            if (
                msg_type not in self._handler_map and
                msg_type not in self.__subscribed_affectors
            ):
                to_ubsubscribe.add(msg_type)
        self.__msg_broker._unsubscribe(self, to_ubsubscribe)
