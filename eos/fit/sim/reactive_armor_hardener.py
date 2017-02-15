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


from copy import copy
from logging import getLogger
from math import ceil, floor

from eos.const.eos import State
from eos.const.eve import Attribute, Effect
from eos.fit.messages import (
    ItemAdded, ItemRemoved, ItemStateChanged, AttrValueChanged,
    AttrValueChangedMasked, DefaultIncomingDamageChanged
)
from eos.util.pubsub import BaseSubscriber
from eos.util.round import sig_round


logger = getLogger(__name__)


MAX_SIMULATION_TICKS = 500
SIG_DIGITS = 10
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


class RahState:
    """Store state of one RAH for single simulation tick"""

    def __init__(self, item, cycling, resonances):
        self.item = item
        self.cycling = cycling
        self.resonances = resonances
        self._rounded_resonances = {attr: sig_round(value, SIG_DIGITS) for attr, value in resonances.items()}

    # Use rounded resonances for more reliable loop detection,
    # as without it accumulated float errors may lead to failed
    # loop detection, in case float values are really close,
    # but still different
    def __hash__(self):
        return hash((id(self.item), self.cycling, frozenset(self._rounded_resonances.items())))

    def __eq__(self, other):
        return all((
            self.item is other.item,
            self.cycling == other.cycling,
            self._rounded_resonances == other._rounded_resonances
        ))


class ReactiveArmorHardenerSimulator(BaseSubscriber):
    """
    Simulator which enables RAH's adaptation to incoming
    damage pattern.
    """

    def __init__(self, fit):
        # Contains all known RAHs and results of simulation
        # Format: {RAH item: {resonance attribute: resonance value}}
        self.__data = {}
        self.__fit = fit
        self.__running = False
        fit._subscribe(self, self._handler_map.keys())

    def get_resonance(self, item, attr):
        """
        Get specified resonance for specified RAH item.
        """
        # Try fetching already simulated results
        resonances = self.__data[item]
        try:
            resonance = resonances[attr]
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
                resonance = self.__data[item][attr]
            # Fetch requested resonance after successful simulation
            else:
                resonance = self.__data[item][attr]
            # Send notifications and do cleanup regardless of simulation
            # success
            finally:
                # Even though caller requested specific resonance of specific
                # RAH, we've calculated all resonances for all RAHs, thus we
                # need to send notifications about all calculated values
                for item in self.__data:
                    for attr in res_attrs:
                        item.attributes._override_value_may_change(attr)
                self.__running = False
        return resonance

    def _run_simulation(self):
        """Controls flow of actual RAH simulation"""
        # Put unsimulated resonances into container for results
        self.__set_unsimulated_resonances()

        # If there's no ship, simulation is meaningless - keep unsimulated results
        try:
            ship_attrs = self.__fit.ship.attributes
        except AttributeError:
            return

        # Containers for tick state history. We need history to detect loops, which helps
        # to receive more accurate resonances and do it faster in majority of the cases.
        # List contains actual history, set is for fast membership test
        # Format: [frozenset(RAH history entries), ...]
        tick_states_chronology = []
        # Format: {frozenset(RAH history entries), ...}
        tick_states_seen = set()

        incoming_damage = self.__fit.default_incoming_damage

        # Container for damage each RAH received during its cycle. May
        # span across several simulation ticks for multi-RAH setups
        # Format: {RAH item: {resonance attribute: damage received}}
        cycle_damage_data = {item: {attr: 0 for attr in res_attrs} for item in self.__data}

        for time_passed, cycled, cycling_data in self.__sim_tick_iter(MAX_SIMULATION_TICKS):
            # For each RAH, calculate damage received during this tick and
            # add it to damage received during RAH cycle
            for item, item_cycle_damage in cycle_damage_data.items():
                for attr in res_attrs:
                    item_cycle_damage[attr] += (
                        getattr(incoming_damage, profile_attrib_map[attr]) * ship_attrs[attr] * time_passed
                    )

            for item in cycled:
                # If RAH just finished its cycle, make resist switch - get new resonances
                new_resonances = self.__get_next_resonances(
                    self.__data[item], cycle_damage_data[item],
                    item.attributes[Attribute.resistance_shift_amount] / 100
                )

                # Then write these resonances to dictionary with results and notify
                # everyone about these changes. This is needed to get updated ship
                # resonances next tick
                self.__data[item].update(new_resonances)
                for attr in res_attrs:
                    item.attributes._override_value_may_change(attr)

                # Reset damage counter for RAH which completed its cycle
                for attr in res_attrs:
                    cycle_damage_data[item][attr] = 0

            # Record current tick state
            tick_state = frozenset(
                # Copy resonances, as we will be modifying them each tick
                RahState(item, cycling_data[item], copy(resonances)) for item, resonances in self.__data.items()
            )

            # See if we're in a loop, if we are - calculate average
            # resists across tick states which are within the loop
            if tick_state in tick_states_seen:
                tick_states_loop = tick_states_chronology[tick_states_chronology.index(tick_state):]
                for item, resonances in self.__get_average_resonances(tick_states_loop).items():
                    self.__data[item] = resonances
                return

            # Update history only if we don't have such entries
            tick_states_seen.add(tick_state)
            tick_states_chronology.append(tick_state)

        # If we didn't find any RAH state loops during specified amount of sim ticks,
        # calculate average resonances based on whole history, excluding initial
        # adaptation period
        else:
            ticks_to_ignore = min(
                self.__estimate_initial_adaptation_ticks(tick_states_chronology),
                # Never ignore more than half of the history
                floor(len(tick_states_chronology) / 2)
            )
            for item, resonances in self.__get_average_resonances(tick_states_chronology[ticks_to_ignore:]).items():
                self.__data[item] = resonances
            return

    def __set_unsimulated_resonances(self):
        """
        Put unsimulated (modified by other items, but not modified
        by overrides from simulator) resonance values into results.
        """
        for item, resonances in self.__data.items():
            for attr in res_attrs:
                resonances[attr] = item.attributes._get_without_overrides(attr)

    def __sim_tick_iter(self, max_ticks):
        """
        Iterate over points in time when cycle of any RAH is finished.
        Return time passed since last tick, list of RAHs finished cycling
        and map with info on how long each RAH has been in current cycle.
        """
        if max_ticks < 1:
            raise StopIteration
        # Keep track of RAH cycle data in this map
        # Format: {RAH item: current cycle time}
        iter_cycle_data = {item: 0 for item in self.__data}
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
            # Format: {remaining cycle time: {RAH items}}
            remaining_time_map = {}
            for item, cycling_time in iter_cycle_data.items():
                remaining_cycle_time = item.cycle_time - cycling_time
                remaining_time_map.setdefault(remaining_cycle_time, set()).add(item)
            sorted_remaining_times = sorted(remaining_time_map)
            # Pick time remaining until some RAH finishes its cycle
            time_passed = sorted_remaining_times[0]
            cycled = remaining_time_map[time_passed]
            # Have time tolerance to cancel float calculation errors:
            # take not just 1st RAHs which strictly finished cycle,
            # but also a few beneath them, if they are really close.
            # If it's not done, it's possible to miss tick state loop
            # formed by multiple RAHs which are out of sync with each
            # other in some cases. E.g., while normal RAH does 17
            # cycles, heated one does 20. This is supposed to be loop,
            # if their resonances match, but
            # >>> sum([0.85]*20) == 17
            # False
            for remaining_cycle_time in sorted_remaining_times[1:]:
                if sig_round(remaining_cycle_time, SIG_DIGITS) <= 0:
                    cycled.add(remaining_time_map[remaining_cycle_time])
                else:
                    break
            # Update map which tracks RAHs' cycle states
            for item in iter_cycle_data:
                if item in cycled:
                    iter_cycle_data[item] = 0
                else:
                    iter_cycle_data[item] += time_passed
            yield time_passed, cycled, copy(iter_cycle_data)

    def __get_next_resonances(self, current_resonances, received_damage, shift_amount):
        """
        Calculate new resonances RAH should take on the next cycle, based on current
        resonances, damage received during current cycle and shift amount.
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
        new_resonances = {}
        # Donate
        for resonance_attr in sorted_resonance_attrs[:donors]:
            current_resonance = current_resonances[resonance_attr]
            # Can't borrow more than it has
            to_donate = min(1 - current_resonance, shift_amount)
            donated_amount += to_donate
            new_resonances[resonance_attr] = current_resonance + to_donate
        # Take
        for resonance_attr in sorted_resonance_attrs[donors:]:
            current_resonance = current_resonances[resonance_attr]
            new_resonances[resonance_attr] = current_resonance - donated_amount / recipients
        return new_resonances

    def __get_average_resonances(self, tick_states):
        """
        Receive iterable with tick states and use it to calculate
        average resonance value for each RAH
        """
        # Container for resonances each RAH used
        # Format: {RAH item: [resonance maps]}
        used_resonances = {}
        for tick_state in tick_states:
            for item_state in tick_state:
                # Add resonances to container only when RAH cycle
                # is just starting
                if item_state.cycling == 0:
                    used_resonances.setdefault(item_state.item, []).append(item_state.resonances)
        # Calculate average values
        # Format: {RAH item: averaged resonances}
        averaged_resonances = {}
        for item, resonances in used_resonances.items():
            averaged_resonances[item] = {
                attr: sum(r[attr] for r in resonances) / len(resonances) for attr in res_attrs
            }
        return averaged_resonances

    def __estimate_initial_adaptation_ticks(self, tick_states):
        """
        Pick RAH which has the slowest adaptation and guesstimate
        its approximate adaptation period in ticks for the worst-case
        """
        # Get max amount of time it takes to exhaust the highest resistance
        # of each RAH
        # Format: {RAH item: amount of cycles}
        exhaustion_cycles = {}
        for item in self.__data:
            # Calculate how many cycles it would take for highest resistance
            # (lowest resonance) to be exhausted
            exhaustion_cycles[item] = max(ceil(
                (1 - item.attributes._get_without_overrides(attr)) /
                (item.attributes[Attribute.resistance_shift_amount] / 100)
            ) for attr in res_attrs)
        # Slowest RAH is the one which takes the most time to exhaust
        # its highest resistance when it's used strictly as donor
        slowest_rah = max(self.__data, key=lambda i: exhaustion_cycles[i] * i.cycle_time)
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
        for tick_state in tick_states[ignored_tick_amount:]:
            # Once slowest RAH cycles desired amount of times, do not count
            # this tick and break the loop
            for item_state in tick_state:
                if item_state.item is slowest_rah:
                    if item_state.cycling == 0:
                        cycle_count += 1
                    break
            if cycle_count >= slowest_cycles:
                break
            tick_count += 1
        return tick_count

    # Message handling
    def _handle_item_addition(self, message):
        item = message.item
        if self.__is_rah(item) is True and item.state >= State.active:
            self.__register(item)
            self.__clear_results()

    def _handle_item_removal(self, message):
        item = message.item
        if self.__is_rah(item) is True and item.state >= State.active:
            self.__unregister(item)
            self.__clear_results()

    def _handle_state_switch(self, message):
        if self.__is_rah(message.item) is not True:
            return
        item, old_state, new_state = message
        if old_state < State.active and new_state >= State.active:
            self.__register(item)
            self.__clear_results()
        elif new_state < State.active and old_state >= State.active:
            self.__unregister(item)
            self.__clear_results()

    def _handle_attr_change(self, message):
        # Ship resistances
        if message.item is self.__fit.ship and message.attr in res_attrs:
            self.__clear_results()
        # RAH shift amount or cycle time
        elif message.item in self.__data and (
            message.attr == Attribute.resistance_shift_amount or
            # Duration change invalidates results only when there're
            # more than 1 RAHs
            (message.attr == self.__get_duration_attr_id(message.item) and len(self.__data) > 1)
        ):
            self.__clear_results()

    def _handle_attr_change_masked(self, message):
        # We've set up overrides on RAHs' resonance attributes, but when
        # base (not modified by simulator) values of these attributes changes,
        # we should re-run simulator - as now we have different resonance value
        # to base sim results off
        if message.item in self.__data and message.attr in res_attrs:
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

    def __register(self, item):
        """Make sure the sim knows about the RAH and the RAH knows about the sim"""
        for attr in res_attrs:
            item.attributes._set_override_callback(attr, (self.get_resonance, (item, attr), {}))
        self.__data.setdefault(item, {})

    def __unregister(self, item):
        """Remove all connections between the sim and passed RAH"""
        for attr in res_attrs:
            item.attributes._del_override_callback(attr)
        try:
            del self.__data[item]
        except KeyError:
            pass

    def __clear_results(self):
        """Remove simulation results, if there're any"""
        for resonances in self.__data.values():
            resonances.clear()
