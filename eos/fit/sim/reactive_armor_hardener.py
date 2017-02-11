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


from collections import namedtuple
from copy import copy
from logging import getLogger
from math import ceil

from eos.const.eos import State
from eos.const.eve import Attribute, Effect
from eos.fit.messages import (
    ItemAdded, ItemRemoved, ItemStateChanged, AttrValueChanged,
    AttrValueChangedMasked, DefaultIncomingDamageChanged
)
from eos.util.pubsub import BaseSubscriber


RahHistoryEntry = namedtuple('RahHistoryEntry', ('cycling_time', 'resonances'))


logger = getLogger(__name__)


MAX_SIMULATION_TICKS = 500
# List all armor resonance attributes and also define default sorting order.
# When equal damage is received across several damage types, those which
# come earlier in this list will be picked as donors
res_attrs = (
    Attribute.armor_em_damage_resonance, Attribute.armor_thermal_damage_resonance,
    Attribute.armor_kinetic_damage_resonance, Attribute.armor_explosive_damage_resonance
)
# Format: {resonance attribute: damage profile field}
profile_attrib_map = {
    Attribute.armor_em_damage_resonance: 'em',
    Attribute.armor_thermal_damage_resonance: 'thermal',
    Attribute.armor_kinetic_damage_resonance: 'kinetic',
    Attribute.armor_explosive_damage_resonance: 'explosive'
}


class ReactiveArmorHardenerSimulator(BaseSubscriber):
    """
    Simulator which enables RAH's adaptation to incoming
    damage pattern.
    """

    def __init__(self, fit):
        # Contains all known RAHs and results of simulation
        # Format: {rah item: {resonance attribute: resonance value}}
        self.__rah_items = {}
        self.__fit = fit
        self.__running = False
        fit._subscribe(self, self._handler_map.keys())

    def get_rah_resonance(self, rah_item, res_attr):
        """
        Get specified resonance for specified RAH item.
        """
        # Try fetching already simulated results
        rah_resonances = self.__rah_items[rah_item]
        try:
            rah_resonance = rah_resonances[res_attr]
        # If no results are readily available, run simulatiomn
        except KeyError:
            self.__clear_results()
            self.__running = True
            try:
                self._run_simulation()
            except KeyboardInterrupt:
                raise
            # In case of any errors, use unsimulated RAH attributes
            except Exception:
                logger.error('unexpected exception in RAH simulator')
                self.__set_unsimulated_resonances()
                rah_resonance = self.__rah_items[rah_item][res_attr]
            # Fetch requested resonance after successful simulation
            else:
                rah_resonance = self.__rah_items[rah_item][res_attr]
            # Send notifications and do cleanup regardless of simulation
            # success
            finally:
                # Even though caller requested specific resonance of specific
                # RAH, we've calculated all resonances for all RAHs, thus we
                # need to send notifications about all calculated values
                for rah_item in self.__rah_items:
                    for res_attr in res_attrs:
                        rah_item.attributes._override_value_may_change(res_attr)
                self.__running = False
        return rah_resonance

    def _run_simulation(self):
        """Controls flow of actual RAH simulation"""

        # Put unsimulated resonances into container for results
        self.__set_unsimulated_resonances()

        # If there's no ship, simulation is meaningless - keep unsimulated results
        try:
            ship_attrs = self.__fit.ship.attributes
        except AttributeError:
            return

        # Container for tick state history. We need history to detect loops, which helps
        # to receive more accurate resonances and do it faster in majority of the cases
        # Format: [{RAH item: RAH history entry}, ...]
        tick_state_history = []
        incoming_damage = self.__fit.default_incoming_damage

        # Container for damage each RAH received during its cycle. May
        # span across several simulation ticks for multi-RAH setups
        # Format: {RAH item: {resonance attribute: damage received}}
        damage_during_cycle = {rah_item: {res_attr: 0 for res_attr in res_attrs} for rah_item in self.__rah_items}

        for time_passed, cycled_rahs, rahs_cycling_data in self.__sim_tick_iter(MAX_SIMULATION_TICKS):
            # For each RAH, calculate damage received during this tick and
            # add it to damage received during RAH cycle
            for rah_item, rah_damage_during_cycle in damage_during_cycle.items():
                for res_attr in res_attrs:
                    rah_damage_during_cycle[res_attr] += (
                        getattr(incoming_damage, profile_attrib_map[res_attr]) *
                        # Default ship resonance to 1 when not specified
                        ship_attrs.get(res_attr, 1) *
                        time_passed
                    )

            for rah_item in cycled_rahs:
                # If RAH just finished its cycle, make resist switch - get new
                # resonance profile
                new_profile = self.__get_next_profile(
                    self.__rah_items[rah_item], damage_during_cycle[rah_item],
                    rah_item.attributes[Attribute.resistance_shift_amount] / 100
                )

                # Then write this profile to dictionary with results and notify
                # everyone about these changes. This is needed to get updated ship
                # resonances next tick
                self.__rah_items[rah_item].update(new_profile)
                for res_attr in res_attrs:
                    rah_item.attributes._override_value_may_change(res_attr)

                # Reset damage counter for RAH which completed its cycle
                for res_attr in res_attrs:
                    damage_during_cycle[rah_item][res_attr] = 0

            # Record current tick state
            tick_state = {}
            for rah_item, rah_profile in self.__rah_items.items():
                tick_state[rah_item] = RahHistoryEntry(rahs_cycling_data[rah_item], copy(rah_profile))

            # See if we're in a loop, if we are - calculate average
            # resists across tick states which are withing the loop
            if tick_state in tick_state_history:
                loop_tick_states = tick_state_history[tick_state_history.index(tick_state):]
                for rah_item, rah_profile in self.__get_average_resonances(loop_tick_states).items():
                    self.__rah_items[rah_item] = rah_profile
                return
            tick_state_history.append(tick_state)

        # If we didn't find any RAH state loops during specified amount of sim ticks,
        # calculate average profiles based on whole history, excluding initial adaptation
        # period
        else:
            ticks_to_ignore = self.__get_initial_adaptation_ticks(tick_state_history)
            # Never ignore more than half of the history
            ticks_to_consider = max(len(tick_state_history) - ticks_to_ignore, ceil(len(tick_state_history) / 2))
            for rah_item, rah_profile in self.__get_average_resonances(tick_state_history[-ticks_to_consider:]).items():
                self.__rah_items[rah_item] = rah_profile
            return

    def __set_unsimulated_resonances(self):
        """
        Put unsimulated (modified by other items, but not modified
        by overrides from simulator) resonance values into results.
        """
        for rah_item, rah_resonances in self.__rah_items.items():
            for attr in res_attrs:
                rah_resonances[attr] = rah_item.attributes._get_without_overrides(attr)

    def __sim_tick_iter(self, max_ticks):
        """
        Iterate over points in time when cycle of any RAH is finished.
        Return time passed since last tick, list of RAHs finished cycling
        and map with info on how long each RAH has been in current cycle.
        """
        if max_ticks < 1:
            raise StopIteration
        # Keep track of RAH cycle data in this map
        # Format: {rah item: current cycle time}
        iter_cycle_data = {rah: 0 for rah in self.__rah_items}
        # Always copy cycle data map to make sure it's not getting
        # modified from outside, which may alter iter state
        yield 0, (), copy(iter_cycle_data)
        # We've already yielded 1 value
        tick = 1
        while True:
            # Stop iteration when current tick exceedes limit
            tick += 1
            if tick > max_ticks:
                raise StopIteration
            # Format: {remaining cycle time: {rah items}}
            remaining_time_map = {}
            for rah_item, rah_cycling_time in iter_cycle_data.items():
                rah_remaining_cycle_time = rah_item.cycle_time - rah_cycling_time
                remaining_time_map.setdefault(rah_remaining_cycle_time, set()).add(rah_item)
            # Pick time remaining until any of RAHs finishes its cycle
            time_passed = min(remaining_time_map)
            rahs_finished_cycle = remaining_time_map[time_passed]
            # Update map which tracks RAHs' cycle states
            for rah_item in iter_cycle_data:
                if rah_item in rahs_finished_cycle:
                    iter_cycle_data[rah_item] = 0
                else:
                    iter_cycle_data[rah_item] += time_passed
            yield time_passed, rahs_finished_cycle, copy(iter_cycle_data)

    def __get_next_profile(self, current_profile, received_damage, shift_amount):
        """
        Calculate new resonance profile RAH should take on the next cycle,
        based on current resonance profile, damage received during current
        cycle and shift amount.
        """
        # We borrow resistances from at least 2 resist types,
        # possibly more if ship didn't take damage of these types
        donors = max(2, len(tuple(filter(lambda rah: received_damage[rah] == 0, received_damage))))
        recipients = 4 - donors
        # Primary key for sorting is received damage, secondary is default order.
        # Default order "sorting" happens due to default order of attributes
        # and stable sorting against primary key.
        sorted_resonance_attrs = sorted(res_attrs, key=received_damage.get)
        donated_amount = 0
        new_profile = {}
        # Donate
        for resonance_attr in sorted_resonance_attrs[:donors]:
            current_resonance = current_profile[resonance_attr]
            # Can't borrow more than it has
            to_donate = min(1 - current_resonance, shift_amount)
            donated_amount += to_donate
            new_profile[resonance_attr] = current_resonance + to_donate
        # Take
        for resonance_attr in sorted_resonance_attrs[donors:]:
            current_resonance = current_profile[resonance_attr]
            new_profile[resonance_attr] = current_resonance - donated_amount / recipients
        return new_profile

    def __get_average_resonances(self, history):
        """
        Receive iterable with history entries and use it to calculate
        average resonance value for each RAH
        """
        # Container for resonance profiles each RAH used
        # Format: {rah item: [profiles]}
        used_profiles = {}
        for entry in history:
            for rah_item, rah_data in entry.items():
                # Add profile to container only when RAH cycle
                # is just starting
                if rah_data.cycling_time == 0:
                    used_profiles.setdefault(rah_item, []).append(rah_data.resonances)
        # Calculate average values
        # Format: {rah item: averaged profile}
        averaged_resonances = {}
        for rah_item, rah_profiles in used_profiles.items():
            rah_resonances = averaged_resonances[rah_item] = {}
            for res_attr in res_attrs:
                rah_resonances[res_attr] = sum(p[res_attr] for p in rah_profiles) / len(rah_profiles)
        return averaged_resonances

    def __get_initial_adaptation_ticks(self, tick_state_history):
        """
        Pick RAH which has the slowest adaptation and guesstimate
        its approximate adaptation period in ticks for the worst-case
        """
        # Get max amount of time it takes to exhaust the highest resistance
        # of each RAH
        # Format: {rah item: amount of cycles}
        exhaustion_cycles = {}
        for rah_item in self.__rah_items:
            # Calculate how many cycles it would take for highest resistance
            # (lowest resonance) to be exhausted
            exhaustion_cycles[rah_item] = max(ceil(
                (1 - rah_item.attributes._get_without_overrides(res_attr)) /
                (rah_item.attributes[Attribute.resistance_shift_amount] / 100)
            ) for res_attr in res_attrs)
        # Slowest RAH is the one which takes the most time to exhaust
        # its highest resistance when it's used strictly as donor
        slowest_rah = max(self.__rah_items, key=lambda i: exhaustion_cycles[i] * i.cycle_time)
        # Multiply amount of resistance exhaustion cycles by 1.5, to give
        # RAH more time for 'finer' adjustments
        slowest_cycles = ceil(exhaustion_cycles[slowest_rah] * 1.5)
        if slowest_cycles == 0:
            return 0
        # We rely on cycling time attribute to be zero in order to determine
        # that cycle for the slowest RAH has just ended. It is zero for the
        # very first tick in the history too, thus we skip it, but take it
        # into initial tick count
        ignored_tick_amount = 1
        tick_count = ignored_tick_amount
        cycle_count = 0
        for tick_state in tick_state_history[ignored_tick_amount:]:
            tick_count += 1
                # Once slowest RAH cycles desired amount of times, break the loop
            if tick_state[slowest_rah].cycling_time == 0:
                cycle_count += 1
                if cycle_count >= slowest_cycles:
                    break
        return tick_count

    # Message handling
    def _handle_item_addition(self, message):
        item = message.item
        if self.__is_rah(item) is True and item.state >= State.active:
            self.__register_rah(item)
            self.__clear_results()

    def _handle_item_removal(self, message):
        item = message.item
        if self.__is_rah(item) is True and item.state >= State.active:
            self.__unregister_rah(item)
            self.__clear_results()

    def _handle_state_switch(self, message):
        if self.__is_rah(message.item) is not True:
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
        # base (not modified by simulator) values of these attributes changes,
        # we should re-run simulator - as now we have different resonance value
        # to base sim results off
        if message.item in self.__rah_items and message.attr in res_attrs:
            self.__clear_results()

    def _handle_changed_damage_profile(self, _):
        self.__clear_results()

    _handler_map = {
        ItemAdded: _handle_item_addition,
        ItemRemoved: _handle_item_removal,
        ItemStateChanged: _handle_state_switch,
        AttrValueChanged: _handle_attr_change,
        AttrValueChangedMasked: _handle_attr_change_masked,
        DefaultIncomingDamageChanged: _handle_changed_damage_profile
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
    def __is_rah(self, item):
        """Verify if passed item is a RAH or not"""
        if not hasattr(item, 'cycle_time'):
            return False
        for effect in item._eve_type.effects:
            if effect.id == Effect.adaptive_armor_hardener:
                return True
        return False

    def __get_duration_attr_id(self, item):
        """Get ID of an attribute which stores cycle time for this module"""
        try:
            return item.default_effect.duration_attribute
        except AttributeError:
            return None

    def __register_rah(self, rah_item):
        """Make sure the sim knows about the RAH and the RAH knows about the sim"""
        for res_attr in res_attrs:
            rah_item.attributes._set_override_callback(res_attr, (self.get_rah_resonance, (rah_item, res_attr), {}))
        self.__rah_items.setdefault(rah_item, {})

    def __unregister_rah(self, rah_item):
        """Remove all connections between the sim and passed RAH"""
        for res_attr in res_attrs:
            rah_item.attributes._del_override_callback(res_attr)
        try:
            del self.__rah_items[rah_item]
        except KeyError:
            pass

    def __clear_results(self):
        """Remove simulation results, if there're any"""
        for rah_resonances in self.__rah_items.values():
            rah_resonances.clear()
