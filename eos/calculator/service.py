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


from eos.const.eve import EffectCategoryId
from eos.eve_obj.modifier import BasePythonModifier
from eos.eve_obj.modifier import DogmaModifier
from eos.eve_obj.modifier import ModificationCalculationError
from eos.item.mixin.solar_system import SolarSystemItemMixin
from eos.pubsub.message import AttrsValueChanged
from eos.pubsub.message import EffectApplied
from eos.pubsub.message import EffectUnapplied
from eos.pubsub.message import EffectsStarted
from eos.pubsub.message import EffectsStopped
from eos.pubsub.message import ItemLoaded
from eos.pubsub.message import ItemUnloaded
from eos.pubsub.subscriber import BaseSubscriber
from eos.util.keyed_storage import KeyedStorage
from .affection import AffectionRegister
from .misc import AffectorSpec
from .misc import Projector
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
        # Container with affector specs which will receive messages
        # Format: {message type: set(affector specs)}
        self.__subscribed_affectors = KeyedStorage()

    def get_modifications(self, affectee_item, affectee_attr_id):
        """Get modifications of affectee attribute on affectee item.

        Args:
            affectee_item: Item, for which we're getting modifications.
            affectee_attr_id: Affectee attribute ID; only modifications which
                influence attribute with this ID will be returned.

        Returns:
            Set with tuples in (modification operator, modification value,
            resistance value, affector item) format.
        """
        # Use list because we can have multiple tuples with the same values
        # as valid configuration
        mods = []
        for affector_spec in self.__affections.get_affector_specs(
            affectee_item
        ):
            affector_modifier = affector_spec.modifier
            affector_item = affector_spec.item
            if affector_modifier.affectee_attr_id != affectee_attr_id:
                continue
            try:
                mod_op, mod_value = affector_modifier.get_modification(
                    affector_item)
            # Do nothing here - errors should be logged in modification
            # getter or even earlier
            except ModificationCalculationError:
                continue
            # Get resistance value
            resist_attr_id = affector_spec.effect.resist_attr_id
            carrier_item = affectee_item._solsys_carrier
            if resist_attr_id and carrier_item is not None:
                try:
                    resist_value = carrier_item.attrs[resist_attr_id]
                except KeyError:
                    resist_value = 1
            else:
                resist_value = 1
            mods.append((mod_op, mod_value, resist_value, affector_item))
        return mods

    # Handle fits
    def _handle_fit_added(self, fit):
        fit._subscribe(self, self._handler_map.keys())

    def _handle_fit_removed(self, fit):
        fit._unsubscribe(self, self._handler_map.keys())

    # Handle item changes which are significant for calculator
    def _handle_item_loaded(self, msg):
        item = msg.item
        self.__affections.register_affectee_item(item)
        if isinstance(item, SolarSystemItemMixin):
            self.__projections.register_solsys_item(item)

    def _handle_item_unloaded(self, msg):
        item = msg.item
        self.__affections.unregister_affectee_item(item)
        if isinstance(item, SolarSystemItemMixin):
            self.__projections.unregister_solsys_item(item)

    def _handle_effects_started(self, msg):
        for affector_spec in self.__generate_local_affector_specs(
            msg.item, msg.effect_ids
        ):
            # Register the affector spec
            if isinstance(affector_spec.modifier, BasePythonModifier):
                self.__subscribe_python_affector_spec(msg.fit, affector_spec)
            self.__affections.register_local_affector_spec(affector_spec)
            # Clear values of attributes dependent on the affector spec
            for affectee_item in self.__affections.get_local_affectee_items(
                affector_spec
            ):
                del affectee_item.attrs[affector_spec.modifier.affectee_attr_id]
        # Register projectors
        for projector in self.__generate_projectors(msg.item, msg.effect_ids):
            self.__projections.register_projector(projector)

    def _handle_effects_stopped(self, msg):
        for affector_spec in self.__generate_local_affector_specs(
            msg.item, msg.effect_ids
        ):
            # Clear values of attributes dependent on the affector spec
            for affectee_item in self.__affections.get_local_affectee_items(
                affector_spec
            ):
                del affectee_item.attrs[affector_spec.modifier.affectee_attr_id]
            # Unregister the affector spec
            self.__affections.unregister_local_affector_spec(affector_spec)
            if isinstance(affector_spec.modifier, BasePythonModifier):
                self.__unsubscribe_python_affector_spec(msg.fit, affector_spec)
        # Unregister projectors
        for projector in self.__generate_projectors(msg.item, msg.effect_ids):
            self.__projections.unregister_projector(projector)

    def _handle_effect_applied(self, msg):
        for affector_spec in self.__generate_projected_affectors(
            msg.item, (msg.effect_id,)
        ):
            # Register the affector spec
            self.__affections.register_projected_affector_spec(
                affector_spec, msg.tgt_items)
            # Clear values of attributes dependent on the affector spec
            for affectee_item in self.__affections.get_projected_affectee_items(
                affector_spec, msg.tgt_items
            ):
                del affectee_item.attrs[affector_spec.modifier.affectee_attr_id]
        # Apply projector
        for projector in self.__generate_projectors(msg.item, (msg.effect_id,)):
            self.__projections.apply_projector(projector, msg.tgt_items)

    def _handle_effect_unapplied(self, msg):
        for affector_spec in self.__generate_projected_affectors(
            msg.item, (msg.effect_id,)
        ):
            # Clear values of attributes dependent on the affector spec
            for affectee_item in self.__affections.get_projected_affectee_items(
                affector_spec, msg.tgt_items
            ):
                del affectee_item.attrs[affector_spec.modifier.affectee_attr_id]
            # Unregister the affector spec
            self.__affections.unregister_projected_affector(
                affector_spec, msg.tgt_items)
        # Un-apply projector
        for projector in self.__generate_projectors(msg.item, (msg.effect_id,)):
            self.__projections.unapply_projector(projector, msg.tgt_items)

    # Methods to clear calculated child attributes when parent attributes change
    def _revise_regular_attr_dependents(self, msg):
        """Remove calculated attribute values which rely on passed attribute.

        Removing them allows to recalculate updated value. Here we process all
        regular dependents, which include dependencies specified via capped
        attribute map and via affector specs with dogma modifiers. Affector
        specs with python modifiers are processed separately.
        """
        for item, attr_ids in msg.attr_changes.items():
            # Remove values of affectee attributes capped by the changing
            # attribute
            for attr_id in attr_ids:
                for capped_attr_id in item.attrs._cap_map.get(attr_id, ()):
                    del item.attrs[capped_attr_id]
            # Force attribute recalculation when local affector spec
            # modification changes
            affections = self.__affections
            for affector_spec in self.__generate_local_affector_specs(
                item, item._running_effect_ids
            ):
                affector_modifier = affector_spec.modifier
                # Only dogma modifiers have source attribute specified, python
                # modifiers are processed separately
                if (
                    not isinstance(affector_modifier, DogmaModifier) or
                    affector_modifier.affector_attr_id not in attr_ids
                ):
                    continue
                # Remove values
                for affectee_item in affections.get_local_affectee_items(
                    affector_spec
                ):
                    del affectee_item.attrs[affector_modifier.affectee_attr_id]
            # Force attribute recalculation when projected affector spec
            # modification changes
            projections = self.__projections
            for projector in self.__generate_projectors(
                item, item._running_effect_ids
            ):
                tgt_items = projections.get_projector_tgts(projector)
                # When projector doesn't target any items, then we do not need
                # to clean anything
                if not tgt_items:
                    continue
                for affector_spec in self.__generate_projected_affectors(
                    item, (projector.effect.id,)
                ):
                    affector_modifier = affector_spec.modifier
                    # Only dogma modifiers have source attribute specified,
                    # python modifiers are processed separately
                    if (
                        not isinstance(affector_modifier, DogmaModifier) or
                        affector_modifier.affector_attr_id not in attr_ids
                    ):
                        continue
                    for affectee_item in (
                        affections.get_projected_affectee_items(
                            affector_spec, tgt_items)
                    ):
                        del affectee_item.attrs[
                            affector_modifier.affectee_attr_id]
            # Force attribute recalculation if changed attribute defines
            # resistance to some effect
            for projector in projections.get_tgt_projectors(item):
                effect = projector.effect
                if effect.resist_attr_id not in attr_ids:
                    continue
                tgt_items = projections.get_projector_tgts(projector)
                for affector_spec in self.__generate_projected_affectors(
                    projector.item, (effect.id,)
                ):
                    for affectee_item in (
                        affections.get_projected_affectee_items(
                            affector_spec, tgt_items)
                    ):
                        del affectee_item.attrs[
                            affector_spec.modifier.affectee_attr_id]

    def _revise_python_attr_dependents(self, msg):
        """Remove calculated attribute values when necessary.

        Here we go through python modifiers, deliver to them message, and if,
        based on contents of the message, they decide that calculated values
        should be removed, we remove values which depend on such modifiers.
        """
        # If there's no subscribed affector specs for received message type, do
        # nothing
        msg_type = type(msg)
        if msg_type not in self.__subscribed_affectors:
            return
        # Otherwise, ask modifier if value of attribute it calculates may
        # change, and force recalculation if answer is yes
        for affector_spec in self.__subscribed_affectors[msg_type]:
            if not affector_spec.modifier.revise_modification(
                msg, affector_spec.item
            ):
                continue
            for affectee_item in self.__affections.get_local_affectee_items(
                affector_spec
            ):
                del affectee_item.attrs[affector_spec.modifier.affectee_attr_id]

    # Message routing
    _handler_map = {
        ItemLoaded: _handle_item_loaded,
        ItemUnloaded: _handle_item_unloaded,
        EffectsStarted: _handle_effects_started,
        EffectsStopped: _handle_effects_stopped,
        EffectApplied: _handle_effect_applied,
        EffectUnapplied: _handle_effect_unapplied,
        AttrsValueChanged: _revise_regular_attr_dependents}

    def _notify(self, msg):
        BaseSubscriber._notify(self, msg)
        # Relay all messages to python modifiers, as in case of python modifiers
        # any message may result in deleting dependent attributes
        self._revise_python_attr_dependents(msg)

    # Affector-related auxiliary methods
    def __generate_local_affector_specs(self, item, effect_ids):
        """Get local affector specs for passed item and effects."""
        affector_specs = set()
        item_effects = item._type_effects
        for effect_id in effect_ids:
            effect = item_effects[effect_id]
            for modifier in effect.local_modifiers:
                affector_spec = AffectorSpec(item, effect, modifier)
                affector_specs.add(affector_spec)
        return affector_specs

    def __generate_projected_affectors(self, item, effect_ids):
        """Get projected affector specs for passed item and effects."""
        affector_specs = set()
        item_effects = item._type_effects
        for effect_id in effect_ids:
            effect = item_effects[effect_id]
            for modifier in effect.projected_modifiers:
                affector_spec = AffectorSpec(item, effect, modifier)
                affector_specs.add(affector_spec)
        return affector_specs

    def __subscribe_python_affector_spec(self, fit, affector_spec):
        """Subscribe affector spec with python modifier."""
        to_subscribe = set()
        for msg_type in affector_spec.modifier.revise_msg_types:
            # Subscribe service to new message type only if there's no such
            # subscription yet
            if (
                msg_type not in self._handler_map and
                msg_type not in self.__subscribed_affectors
            ):
                to_subscribe.add(msg_type)
            # Add affector spec to subscriber map to let it receive messages
            self.__subscribed_affectors.add_data_entry(msg_type, affector_spec)
        if to_subscribe:
            fit._subscribe(self, to_subscribe)

    def __unsubscribe_python_affector_spec(self, fit, affector_spec):
        """Unsubscribe affector spec with python modifier."""
        to_ubsubscribe = set()
        for msg_type in affector_spec.modifier.revise_msg_types:
            # Make sure affector spec will not receive messages anymore
            self.__subscribed_affectors.rm_data_entry(msg_type, affector_spec)
            # Unsubscribe service from message type if there're no recipients
            # anymore
            if (
                msg_type not in self._handler_map and
                msg_type not in self.__subscribed_affectors
            ):
                to_ubsubscribe.add(msg_type)
        if to_ubsubscribe:
            fit._unsubscribe(self, to_ubsubscribe)

    # Projector-related auxiliary methods
    def __generate_projectors(self, item, effect_ids):
        """Get projectors spawned by the item."""
        projectors = set()
        item_effects = item._type_effects
        for effect_id in effect_ids:
            effect = item_effects[effect_id]
            if effect.category_id != EffectCategoryId.target:
                continue
            # While projectors which carry no modifiers are technically
            # projectors, calculator doesn't care about them, thus it makes no
            # sense to generate and store them
            if not effect.projected_modifiers:
                continue
            projector = Projector(item, effect)
            projectors.add(projector)
        return projectors
