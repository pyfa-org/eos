# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from eos.const.eos import State, Scope
from eos.fit.messages import HolderAdded, HolderRemoved, HolderStateChanged, EffectsEnabled, EffectsDisabled
from eos.util.pubsub import BaseSubscriber
from .affector import Affector
from .register import LinkRegister


class LinkTracker(BaseSubscriber):
    """
    Serve as intermediate layer between fit and holder link register.
    Implements methods which make it easier for fit to add, modify and
    remove holders (by implementing higher-level logic which deals with
    state, scope and attribute filters), and exposes two main register
    getters for external use.

    Required arguments:
    fit -- Fit object to which tracker is assigned
    """

    def __init__(self, fit):
        self._fit = fit
        self._register = LinkRegister(fit)
        fit._subscribe(self, self._handler_map.keys())

    def get_affectors(self, holder, attr=None):
        """
        Get affectors which are influencing the holder.

        Required arguments:
        holder -- holder, for which we're getting affectors

        Optional arguments:
        attr -- target attribute ID filter; only affectors
        which influence attribute with this ID will be returned.
        If None, all affectors influencing holder are returned
        (default None)

        Return value:
        Set with Affector objects
        """
        if attr is None:
            affectors = self._register.get_affectors(holder)
        else:
            affectors = set()
            for affector in self._register.get_affectors(holder):
                if affector.modifier.tgt_attr == attr:
                    affectors.add(affector)
        return affectors

    def get_affectees(self, affector):
        """
        Get affectees being influenced by the affector.

        Required arguments:
        affector -- affector, for which we're getting affectees

        Return value:
        Set with holders
        """
        return self._register.get_affectees(affector)

    def clear_holder_attribute_dependents(self, holder, attr):
        """
        Clear calculated attributes relying on the passed attribute.

        Required arguments:
        holder -- holder, which carries attribute in question
        attr -- ID of attribute
        """
        # Clear attributes capped by this attribute
        cap_map = holder.attributes._cap_map
        if cap_map is not None:
            for capped_attr in (cap_map.get(attr) or ()):
                del holder.attributes[capped_attr]
        # Clear attributes which are using this attribute as modification source
        for affector in self.__generate_affectors(holder, effect_filter=holder._enabled_effects):
            modifier = affector.modifier
            # Skip affectors which do not use attribute being damaged as source
            if modifier.src_attr != attr:
                continue
            # Go through all holders targeted by modifier
            for target_holder in self.get_affectees(affector):
                # And remove target attribute
                del target_holder.attributes[modifier.tgt_attr]

    def __generate_affectors(self, holder, effect_filter=None, state_filter=None, scope_filter=None):
        """
        Get all affectors spawned by the holder.

        Required arguments:
        holder -- holder, for which affectors are generated

        Optional arguments:
        effect filter -- filter results to include affectors, which
        carry modifiers generated from effects with IDs on this list;
        if None, no filtering occurs (default None)
        state_filter -- filter results by state required by affector's
        modifier, which should be in this iterable; if None, no
        filtering occurs (default None)
        scope_filter -- filter results by scope defined in affector's
        modifier, which should be in this iterable; if None, no
        filtering occurs (default None)

        Return value:
        Set with Affector objects, satisfying passed filters
        """
        affectors = set()
        for effect in holder.item.effects:
            if effect_filter is not None and effect.id not in effect_filter:
                continue
            for modifier in effect.modifiers:
                if state_filter is not None and modifier.state not in state_filter:
                    continue
                if scope_filter is not None and modifier.scope not in scope_filter:
                    continue
                affector = Affector(holder, modifier)
                affectors.add(affector)
        return affectors

    # Message handling
    def _handle_holder_addition(self, message):
        """
        Put the holder under influence of registered affectors
        and enable its affectors according to its state.
        """
        self._register.register_affectee(message.holder)
        states = set(filter(lambda s: s <= message.holder.state, State))
        self.__enable_states(message.holder, states)

    def _handle_holder_removal(self, message):
        """
        Disable holder affectors and remove it from influence
        of of registered affectors.
        """
        states = set(filter(lambda s: s <= message.holder.state, State))
        self.__disable_states(message.holder, states)
        self._register.unregister_affectee(message.holder)

    def _handle_holder_state_change(self, message):
        """
        Enable/disable affectors based on state change direction.
        """
        holder, old_state, new_state = message
        if new_state > old_state:
            states = set(filter(lambda s: old_state < s <= new_state, State))
            self.__enable_states(holder, states)
        elif old_state < new_state:
            states = set(filter(lambda s: new_state < s <= old_state, State))
            self.__disable_states(holder, states)

    def _handle_holder_effects_enabling(self, message):
        """
        Enable effects carried by the holder.
        """
        processed_states = set(filter(lambda s: s <= message.holder.state, State))
        processed_scopes = (Scope.local,)
        affectors = self.__generate_affectors(
            message.holder, effect_filter=message.effects, state_filter=processed_states,
            scope_filter=processed_scopes
        )
        self.__enable_affectors(affectors)

    def _handle_holder_effects_disabling(self, message):
        """
        Disable effects carried by the holder.
        """
        processed_states = set(filter(lambda s: s <= message.holder.state, State))
        processed_scopes = (Scope.local,)
        affectors = self.__generate_affectors(
            message.holder, effect_filter=message.effects, state_filter=processed_states,
            scope_filter=processed_scopes
        )
        self.__disable_affectors(affectors)

    _handler_map = {
        HolderAdded: _handle_holder_addition,
        HolderRemoved: _handle_holder_removal,
        HolderStateChanged: _handle_holder_state_change,
        EffectsEnabled: _handle_holder_effects_enabling,
        EffectsDisabled: _handle_holder_effects_disabling
    }

    def _notify(self, message):
        # Attribute calculations need source for base attributes
        # and attributes metadata
        if self._fit.source is None:
            return
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            return
        handler(self, message)

    # Private methods for message handlers
    def __enable_states(self, holder, states):
        """
        Handle state switch upwards.

        Required arguments:
        holder -- holder, for which states are switched
        states -- iterable with states, which are passed
        during state switch, except for initial state
        """
        processed_effects = holder._enabled_effects
        processed_scopes = (Scope.local,)
        affectors = self.__generate_affectors(
            holder, effect_filter=processed_effects,
            state_filter=states, scope_filter=processed_scopes
        )
        self.__enable_affectors(affectors)

    def __disable_states(self, holder, states):
        """
        Handle state switch downwards.

        Required arguments:
        holder -- holder, for which states are switched
        states -- iterable with states, which are passed
        during state switch, except for final state
        """
        processed_effects = holder._enabled_effects
        processed_scopes = (Scope.local,)
        affectors = self.__generate_affectors(
            holder, effect_filter=processed_effects,
            state_filter=states, scope_filter=processed_scopes
        )
        self.__disable_affectors(affectors)

    def __enable_affectors(self, affectors):
        """
        Enable effect of affectors on their target holders.

        Required arguments:
        affectors -- iterable with affectors to enable
        """
        # Clear attributes only after registration jobs
        for affector in affectors:
            self._register.register_affector(affector)
        self.__clear_affectors_dependents(affectors)

    def __disable_affectors(self, affectors):
        """
        Remove effect of affectors from their target holders.

        Required arguments:
        affectors -- iterable with affectors to disable
        """
        # Clear attributes before unregistering, otherwise
        # we won't clean them up properly
        self.__clear_affectors_dependents(affectors)
        for affector in affectors:
            self._register.unregister_affector(affector)

    def __clear_affectors_dependents(self, affectors):
        """
        Clear calculated attributes which are relying on
        passed affectors.

        Required arguments:
        affectors -- iterable with affectors in question
        """
        for affector in affectors:
            # Go through all holders targeted by modifier
            for target_holder in self.get_affectees(affector):
                # And remove target attribute
                del target_holder.attributes[affector.modifier.tgt_attr]
