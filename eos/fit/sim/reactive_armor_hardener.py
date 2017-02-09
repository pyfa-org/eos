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


from eos.const.eos import State
from eos.const.eve import Attribute, Effect
from eos.fit.messages import ItemAdded, ItemRemoved, ItemStateChanged, AttrValueChanged, AttrValueChangedMasked
from eos.util.frozen_dict import FrozenDict
from eos.util.pubsub import BaseSubscriber
from eos.util.round import round_to_significant_digits as round_sig


# We will be rounding almost each and every involved number to this
# amount of significant digits during simulation to cancel out float
# errors, which is needed for more reliable loop detection
KEEP_DIGITS = 10

res_attrs = (
    Attribute.armor_em_damage_resonance, Attribute.armor_thermal_damage_resonance,
    Attribute.armor_kinetic_damage_resonance, Attribute.armor_explosive_damage_resonance
)
res_attr_pattern_map = {
    Attribute.armor_em_damage_resonance: 'em',
    Attribute.armor_thermal_damage_resonance: 'thermal',
    Attribute.armor_kinetic_damage_resonance: 'kinetic',
    Attribute.armor_explosive_damage_resonance: 'explosive'
}
# When equal damage is received across several damage types, those which
# come earlier in this list will be picked as resistance donators
default_sorting = (
    Attribute.armor_em_damage_resonance, Attribute.armor_thermal_damage_resonance,
    Attribute.armor_kinetic_damage_resonance, Attribute.armor_explosive_damage_resonance
)


class ReactiveArmorHardenerSimulator(BaseSubscriber):

    def __init__(self, fit):
        # Format: {rah item: {resonance attribute: resonance value}}
        self.__rah_items = {}
        self.__fit = fit
        self.__running = False
        fit._subscribe(self, self._handler_map.keys())

    def run_simulation(self):
        if len(self.__rah_items) == 0:
            return
        self.__running = True
        # If there's no ship, simulation is meaningless
        try:
            ship_attrs = self.__fit.ship.attributes
        except AttributeError:
            self.__running = False
            return
        # Initialize results with base values (modified by other items, but not by sim)
        for rah_item, rah_resonances in self.__rah_items.items():
            for res_attr in res_attrs:
                rah_resonances[res_attr] = round_sig(rah_item.attributes._get_without_overrides(res_attr), KEEP_DIGITS)
        # Format: [{(RAH item 1, time cycling, profile), (RAH item 2, time cycling, profile), ...}, ...],
        history = []
        incoming_damage = self.__fit.default_incoming_damage
        # Find RAH with the slowest cycle time
        slow_rah = max(self.__rah_items, key=lambda i: i.cycle_time)
        # Simulation will stop when the slowest RAH cycles this amount of times
        slow_cycles_max = 500
        slow_cycles_current = 0

        # Format: {RAH item: {resonance attribute: damage received during RAH cycle for this resonance}}
        damage_during_cycle = {rah: {attr: 0 for attr in res_attrs} for rah in self.__rah_items}
        for time_passed, cycled_rahs, rah_states in self.__sim_tick_iter():

            # Calculate damage received over passed time
            damage_current = {attr: (
                time_passed * getattr(incoming_damage, res_attr_pattern_map[attr]) * ship_attrs[attr]
            ) for attr in res_attrs}

            # Add it up to damage already received by RAHs during past cycles
            for rah_item, rah_damage_during_cycle in damage_during_cycle.items():
                for attr in res_attrs:
                    rah_damage_during_cycle[attr] += damage_current[attr]

            for rah_item in cycled_rahs:
                new_profile = self.__get_next_profile(
                    self.__rah_items[rah_item], damage_during_cycle[rah_item],
                    rah_item.attributes[Attribute.resistance_shift_amount] / 100
                )

                # Set new profile and notify about changes
                self.__rah_items[rah_item].update(new_profile)
                for attr in res_attrs:
                    rah_item.attributes._override_value_may_change(attr)

                # Reset damage counter for RAH which completed its cycle
                for attr in res_attrs:
                    damage_during_cycle[rah_item][attr] = 0

            # Get current resonance values and record state
            history_entry = set()
            for rah_item, rah_profile in self.__rah_items.items():
                history_entry.add((rah_item, rah_states[rah_item], FrozenDict(rah_profile)))

            # See if we're in loop, end if we are
            if history_entry in history:
                for rah, profile in self.__average_history(history[history.index(history_entry):]).items():
                    self.__rah_items[rah] = profile
                    for attr in res_attrs:
                        rah.attributes._override_value_may_change(attr)
                self.__running = False
                return
            history.append(history_entry)

            # Break cycle if slowest RAH reached its limit
            if slow_rah in cycled_rahs:
                slow_cycles_current += 1
                if slow_cycles_current >= slow_cycles_max:
                    # TODO: make it not hardcoded, something along lines of
                    # ignoring ceil(15/6)*2 first cycles
                    cycles_to_ignore = 6
                    for rah, profile in self.__average_history(history[cycles_to_ignore:]).items():
                        self.__rah_items[rah] = profile
                        for attr in res_attrs:
                            rah.attributes._override_value_may_change(attr)
                    self.__running = False
                    return

    def __get_next_profile(self, current_profile, received_damage, shift_amount):
        # We take from at least 2 resists, possibly more if they do not take damage
        feeders = max(2, len(tuple(filter(lambda rah: received_damage[rah] == 0, received_damage))))
        stealers = 4 - feeders
        # Primary key for sorting is received damage, secondary is default order.
        # Secondary "sorting" happens due to default list order and stable sort
        sorted_damage_types = sorted(default_sorting, key=received_damage.get)
        fed_amount = 0
        new_profile = {}
        # Steal
        for resonance_attr in sorted_damage_types[:feeders]:
            current_resonance = current_profile[resonance_attr]
            to_feed = min(1 - current_resonance, shift_amount)
            fed_amount += to_feed
            new_profile[resonance_attr] = current_resonance + to_feed
        # Give
        for resonance_attr in sorted_damage_types[feeders:]:
            current_resonance = current_profile[resonance_attr]
            new_profile[resonance_attr] = current_resonance - fed_amount / stealers
        return new_profile

    def __sim_tick_iter(self):
        """
        Iterate over points in time when cycle of any RAH is finished.
        Return time passed since last tick, list of RAHs finished cycling
        and map with info on how long each RAH has been in current cycle.
        """
        # Format: {rah item: current cycle time}
        state = {rah: 0 for rah in self.__rah_items}
        yield 0, (), state
        while True:
            # Format: {remaining time: {rah items}}
            remaining_map = {}
            for rah, current_time in state.items():
                remaining_time = rah.cycle_time - current_time
                remaining_map.setdefault(remaining_time, set()).add(rah)
            time_passed = min(remaining_map)
            finished_cycle = remaining_map[time_passed]
            state = {rah: 0 if rah in finished_cycle else state[rah] + time_passed for rah in state}
            yield time_passed, finished_cycle, state

    def __average_history(self, history):
        # Format: {rah: [profiles]}
        used_profiles = {}
        for entry in history:
            for rah, cycle_time, profile in entry:
                if cycle_time == 0:
                    used_profiles.setdefault(rah, []).append(profile)
        # Format: {rah: profile}
        result = {}
        for rah, profiles in used_profiles.items():
            for attr in res_attrs:
                result.setdefault(rah, {})[attr] = sum(p[attr] for p in profiles) / len(profiles)
        return result

    # Message handling
    def _handle_item_addition(self, message):
        item = message.item
        if self.__check_if_rah(item) is True and item.state >= State.active:
            self.__register_rah(item)
            self.__clear_results()

    def _handle_item_removal(self, message):
        item = message.item
        if self.__check_if_rah(item) is True and item.state >= State.active:
            self.__unregister_rah(item)
            self.__clear_results()

    def _handle_state_switch(self, message):
        if self.__check_if_rah(message.item) is not True:
            return
        item, old_state, new_state = message
        if old_state < State.active and new_state >= State.active:
            self.__register_rah(item)
            self.__clear_results()
        elif new_state < State.active and old_state >= State.active:
            self.__unregister_rah(item)
            self.__clear_results()

    def _handle_attr_change(self, message):
        # Ship resistances
        if message.item is self.__fit.ship and message.attr in res_attrs:
            self.__clear_results()
        # RAH shift amount or cycle time
        elif message.item in self.__rah_items and (
            message.attr == Attribute.resistance_shift_amount or
            # Duration change invalidates results only when there're
            # more than 1 RAHs
            (message.attr == self.__get_duration_attr_id(message.item) and len(self.__rah_items) > 1)
        ):
            self.__clear_results()

    def _handle_attr_change_masked(self, message):
        # We've set up overrides on RAHs' resonance attributes, but when
        # base (not modified by simulator) values of these attributes change,
        # we should re-run simulator
        if message.item in self.__rah_items and message.attr in res_attrs:
            self.__clear_results()

    _handler_map = {
        ItemAdded: _handle_item_addition,
        ItemRemoved: _handle_item_removal,
        ItemStateChanged: _handle_state_switch,
        AttrValueChanged: _handle_attr_change,
        AttrValueChangedMasked: _handle_attr_change_masked
    }

    def _notify(self, message):
        if self.__running is True:
            return
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            return
        handler(self, message)

    # Auxiliary message handling methods
    def __check_if_rah(self, item):
        if not hasattr(item, 'cycle_time'):
            return False
        for effect in item._eve_type.effects:
            if effect.id == Effect.adaptive_armor_hardener:
                return True
        return False

    def __get_duration_attr_id(self, item):
        try:
            return item.default_effect.duration_attribute
        except AttributeError:
            return None

    def __register_rah(self, rah_item):
        for res_attr in res_attrs:
            rah_item.attributes._set_override_callback(res_attr, (self.get_rah_resonance, (rah_item, res_attr), {}))
        self.__rah_items.setdefault(rah_item, {})

    def __unregister_rah(self, rah_item):
        for res_attr in res_attrs:
            rah_item.attributes._del_override_callback(res_attr)
        try:
            del self.__rah_items[rah_item]
        except KeyError:
            pass

    def __clear_results(self):
        for ress in self.__rah_items.values():
            ress.clear()

    def get_rah_resonance(self, item, attr):
        resonances = self.__rah_items[item]
        try:
            resonance = resonances[attr]
        except KeyError:
            self.__clear_results()
            self.run_simulation()
            resonance = resonances[attr]
        return resonance
