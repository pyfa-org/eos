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


from eos.const.eos import ModDomain
from eos.eve_obj.modifier import BasePythonModifier
from eos.eve_obj.modifier import DogmaModifier
from eos.eve_obj.modifier import ModificationCalculationError
from eos.pubsub.message import AttrValueChanged
from eos.pubsub.message import EffectsStarted
from eos.pubsub.message import EffectsStopped
from eos.pubsub.message import ItemLoaded
from eos.pubsub.message import ItemUnloaded
from eos.pubsub.subscriber import BaseSubscriber
from eos.util.keyed_storage import KeyedStorage
from .affection import AffectionRegister
from .misc import Affector
from .projection import ProjectionRegister


class CalculationService(BaseSubscriber):
    """Service which supports attribute calculation.

    This class collects data about various items and relations between them, and
    via exposed methods which provice data about these connections helps
    attribute map to calculate modified attribute values.
    """

    def __init__(self):
        self.__affections = AffectionRegister()
        self.__projections = ProjectionRegister()
        # Container with affectors which will receive messages
        # Format: {message type: set(affectors)}
        self.__subscribed_affectors = KeyedStorage()

    def get_modifications(self, tgt_item, tgt_attr_id):
        """Get modifications of target attribute on target item.

        Args:
            tgt_item: Item, for which we're getting modifications.
            tgt_attr_id: Target attribute ID; only modifications which influence
                attribute with this ID will be returned.

        Returns:
            Set with tuples in (operator, modification value, carrier item)
            format.
        """
        # Use list because we can have multiple tuples with the same values
        # as valid configuration
        modifications = []
        for carrier_item, modifier in self.__affections.get_affectors(
            tgt_item._fit, tgt_item
        ):
            if modifier.tgt_attr_id == tgt_attr_id:
                try:
                    mod_op, mod_value = modifier.get_modification(carrier_item)
                # Do nothing here - errors should be logged in modification
                # getter or even earlier
                except ModificationCalculationError:
                    continue
                modifications.append((mod_op, mod_value, carrier_item))
        return modifications

    def _handle_fit_added(self, fit):
        fit._subscribe(self, self._handler_map.keys())

    def _handle_fit_removed(self, fit):
        fit._unsubscribe(self, self._handler_map.keys())

    # Handle item changes which are significant for calculator
    def _handle_item_loaded(self, msg):
        self.__affections.register_affectee(msg.fit, msg.item)

    def _handle_item_unloaded(self, msg):
        self.__affections.unregister_affectee(msg.fit, msg.item)

    def _handle_effects_started(self, msg):
        fit = msg.fit
        affectors = self.__generate_affectors(msg.item, msg.effect_ids)
        for affector in affectors:
            if isinstance(affector.modifier, BasePythonModifier):
                self.__subscribe_python_affector(fit, affector)
            self.__affections.register_affector(fit, affector)
            for tgt_item in self.__affections.get_affectees(fit, affector):
                del tgt_item.attrs[affector.modifier.tgt_attr_id]

    def _handle_effects_stopped(self, msg):
        fit = msg.fit
        affectors = self.__generate_affectors(msg.item, msg.effect_ids)
        for affector in affectors:
            for tgt_item in self.__affections.get_affectees(fit, affector):
                del tgt_item.attrs[affector.modifier.tgt_attr_id]
            self.__affections.unregister_affector(fit, affector)
            if isinstance(affector.modifier, BasePythonModifier):
                self.__unsubscribe_python_affector(fit, affector)

    # Methods to clear calculated child nodes when parent nodes change
    def _revise_regular_attr_dependents(self, msg):
        """Remove calculated attribute values which rely on passed attribute.

        Removing them allows to recalculate updated value. Here we process all
        regular dependents, which include dependencies specified via capped
        attribute map and via affectors with dogma modifiers. Affectors with
        python modifiers are processed separately.
        """
        # Remove values of target attributes capped by changing attribute
        item = msg.item
        attr_id = msg.attr_id
        for capped_attr_id in item.attrs._cap_map.get(attr_id, ()):
            del item.attrs[capped_attr_id]
        # Remove values of target attributes which are using changing attribute
        # as modification source
        for affector in self.__generate_affectors(
                item, item._running_effect_ids):
            modifier = affector.modifier
            # Only dogma modifiers have source attribute specified, python
            # modifiers are processed separately
            if (
                not isinstance(modifier, DogmaModifier) or
                modifier.src_attr_id != attr_id
            ):
                continue
            for tgt_item in self.__affections.get_affectees(msg.fit, affector):
                del tgt_item.attrs[modifier.tgt_attr_id]

    def _revise_python_attr_dependents(self, msg):
        """Remove calculated attribute values when necessary.

        Here we go through python modifiers, deliver to them message, and if,
        based on contents of the message, they decide that calculated values
        should be removed, we remove values which depend on such modifiers.
        """
        # If there's no affector-subscribers for received message type, do
        # nothing
        msg_type = type(msg)
        if msg_type not in self.__subscribed_affectors:
            return
        # Otherwise, ask affector if target value should change, and remove it
        # if it should
        for affector in self.__subscribed_affectors[msg_type]:
            if not affector.modifier.revise_modification(
                msg, affector.carrier_item
            ):
                continue
            for tgt_item in self.__affections.get_affectees(msg.fit, affector):
                del tgt_item.attrs[affector.modifier.tgt_attr_id]

    # Message routing
    _handler_map = {
        ItemLoaded: _handle_item_loaded,
        ItemUnloaded: _handle_item_unloaded,
        EffectsStarted: _handle_effects_started,
        EffectsStopped: _handle_effects_stopped,
        AttrValueChanged: _revise_regular_attr_dependents}

    def _notify(self, msg):
        BaseSubscriber._notify(self, msg)
        # Relay all messages to python modifiers, as in case of python modifiers
        # any message may result in deleting dependent attributes
        self._revise_python_attr_dependents(msg)

    # Do not process here just target domain
    _supported_domains = set(
        domain for domain in ModDomain if domain != ModDomain.target)

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
        for effect_id, effect in item._type_effects.items():
            if effect_id not in effect_ids:
                continue
            for modifier in effect.modifiers:
                if modifier.tgt_domain not in self._supported_domains:
                    continue
                affector = Affector(item, modifier)
                affectors.add(affector)
        return affectors

    # Python affector subscription/unsubscription
    def __subscribe_python_affector(self, fit, affector):
        """Subscribe python affector to message types it wants."""
        to_subscribe = set()
        for msg_type in affector.modifier.revise_msg_types:
            # Subscribe service to new message type only if there's no such
            # subscription yet
            if (
                msg_type not in self._handler_map and
                msg_type not in self.__subscribed_affectors
            ):
                to_subscribe.add(msg_type)
            # Add affector to subscriber map to let it receive messages
            self.__subscribed_affectors.add_data_entry(msg_type, affector)
        if to_subscribe:
            fit._subscribe(self, to_subscribe)

    def __unsubscribe_python_affector(self, fit, affector):
        """Unsubscribe python affector."""
        to_ubsubscribe = set()
        for msg_type in affector.modifier.revise_msg_types:
            # Make sure affector will not receive messages anymore
            self.__subscribed_affectors.rm_data_entry(msg_type, affector)
            # Unsubscribe service from message type if there're no recipients
            # anymore
            if (
                msg_type not in self._handler_map and
                msg_type not in self.__subscribed_affectors
            ):
                to_ubsubscribe.add(msg_type)
        if to_ubsubscribe:
            fit._unsubscribe(self, to_ubsubscribe)
