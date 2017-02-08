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
from eos.fit.messages import ItemAdded, ItemRemoved, ItemStateChanged, AttrValueChanged, AttrValueChangedOverride
from eos.util.pubsub import BaseSubscriber


res_attrs = resattr_em, resattr_thermal, resattr_kinetic, resattr_explosive = (
    Attribute.armor_em_damage_resonance, Attribute.armor_thermal_damage_resonance,
    Attribute.armor_kinetic_damage_resonance, Attribute.armor_explosive_damage_resonance
)


class ReactiveArmorHardenerSimulator(BaseSubscriber):

    def __init__(self, fit):
        self.__rah_items = set()
        self.__simulation_results = {}
        self.__fit = fit
        self.__running = False
        fit._subscribe(self, self._handler_map.keys())

    def run_simulation(self):
        if len(self.__rah_items) == 0:
            return
        self.__running = True
        # Reset attributes on all known RAHs
        for rah in self.__rah_items:
            for attr in (
                Attribute.armor_em_damage_resonance, Attribute.armor_thermal_damage_resonance,
                Attribute.armor_kinetic_damage_resonance, Attribute.armor_explosive_damage_resonance
            ):
                rah.attributes._override_del(attr)
        # If there's no ship, simulation is meaningless
        try:
            ship_attrs = self.__fit.ship.attributes
        except AttributeError:
            self.__running = False
            return
        # Format: [{(rah item1, time cycling, profile), (rah item2, time cycling, profile), ...}, ...],
        history = []
        incoming_damage = self.__fit.default_incoming_damage
        # Find RAH with the slowest cycle time
        slow_rah = max(self.__rah_items, key=lambda i: i.cycle_time)
        # Simulation will stop when this RAH cycles this amount of times
        slow_cycles_max = 500
        slow_cycles_current = 0
        # Format: {rah item: damage received during cycle}
        damage_during_cycle = {rah: (0, 0, 0, 0) for rah in self.__rah_items}
        for time_passed, cycled_rahs, rah_states in self.__rah_state_iter():

            # Calculate damage received over passed time
            damage_current = (
                time_passed * incoming_damage.em * ship_attrs[Attribute.armor_em_damage_resonance],
                time_passed * incoming_damage.thermal * ship_attrs[Attribute.armor_thermal_damage_resonance],
                time_passed * incoming_damage.kinetic * ship_attrs[Attribute.armor_kinetic_damage_resonance],
                time_passed * incoming_damage.explosive * ship_attrs[Attribute.armor_explosive_damage_resonance]
            )
            for rah, damage_old in damage_during_cycle.items():
                damage_during_cycle[rah] = (
                    damage_old[0] + damage_current[0], damage_old[1] + damage_current[1],
                    damage_old[2] + damage_current[2], damage_old[3] + damage_current[3]
                )
            for rah_item in cycled_rahs:
                rah_profile = tuple(rah_item.attributes.get(attr) for attr in (
                    Attribute.armor_em_damage_resonance, Attribute.armor_thermal_damage_resonance,
                    Attribute.armor_kinetic_damage_resonance, Attribute.armor_explosive_damage_resonance
                ))
                new_profile = self.__get_next_profile(
                    rah_profile, damage_during_cycle[rah_item],
                    rah_item.attributes[Attribute.resistance_shift_amount]
                )
                rah_item.attributes._override_set(Attribute.armor_em_damage_resonance, new_profile[0])
                rah_item.attributes._override_set(Attribute.armor_thermal_damage_resonance, new_profile[1])
                rah_item.attributes._override_set(Attribute.armor_kinetic_damage_resonance, new_profile[2])
                rah_item.attributes._override_set(Attribute.armor_explosive_damage_resonance, new_profile[3])
                damage_during_cycle[rah_item] = (0, 0, 0, 0)

            # Get current resonance values and record state
            history_entry = set()
            for rah_item in self.__rah_items:
                rah_profile = tuple(rah_item.attributes.get(attr) for attr in (
                    Attribute.armor_em_damage_resonance, Attribute.armor_thermal_damage_resonance,
                    Attribute.armor_kinetic_damage_resonance, Attribute.armor_explosive_damage_resonance
                ))
                history_entry.add((rah_item, rah_states[rah_item], rah_profile))
            # See if we're in loop, end if we are
            if history_entry in history:
                for rah, profile in self.__average_history(history[history.index(history_entry):]).items():
                    rah.attributes._override_set(Attribute.armor_em_damage_resonance, profile[0])
                    rah.attributes._override_set(Attribute.armor_thermal_damage_resonance, profile[1])
                    rah.attributes._override_set(Attribute.armor_kinetic_damage_resonance, profile[2])
                    rah.attributes._override_set(Attribute.armor_explosive_damage_resonance, profile[3])
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
                        rah.attributes._override_set(Attribute.armor_em_damage_resonance, profile[0])
                        rah.attributes._override_set(Attribute.armor_thermal_damage_resonance, profile[1])
                        rah.attributes._override_set(Attribute.armor_kinetic_damage_resonance, profile[2])
                        rah.attributes._override_set(Attribute.armor_explosive_damage_resonance, profile[3])
                    self.__running = False
                    return

    def __get_next_profile(self, current_profile, received_damage, shift_amount):
        attr_position_map = {
            Attribute.armor_em_damage_resonance: 0,
            Attribute.armor_thermal_damage_resonance: 1,
            Attribute.armor_kinetic_damage_resonance: 2,
            Attribute.armor_explosive_damage_resonance: 3
        }
        shift_amount = shift_amount / 100
        victims = max(2, len(tuple(filter(lambda i: i == 0, received_damage))))
        burglars = 4 - victims
        received_damage_map = {attr: received_damage[pos] for attr, pos in attr_position_map.items()}
        profile_map = {attr: current_profile[pos] for attr, pos in attr_position_map.items()}
        attr_damage_sorted = sorted(received_damage_map.items(), key=lambda t: (t[1], t[0]))
        stolen_amount = 0
        # Steal
        for resonance_attr, dmg_taken in attr_damage_sorted[:victims]:
            to_steal = min(1 - profile_map[resonance_attr], shift_amount)
            stolen_amount += to_steal
            profile_map[resonance_attr] += to_steal
        # Give
        for resonance_attr, dmg_taken in attr_damage_sorted[victims:]:
            profile_map[resonance_attr] -= stolen_amount / burglars
        result = tuple(profile_map[attr] for attr in sorted(attr_position_map, key=attr_position_map.get))
        print(result)
        return result

    def __rah_state_iter(self):
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
            result[rah] = (
                sum(profile[0] for profile in profiles) / len(profiles),
                sum(profile[1] for profile in profiles) / len(profiles),
                sum(profile[2] for profile in profiles) / len(profiles),
                sum(profile[3] for profile in profiles) / len(profiles)
            )
        return result

    def _handle_item_addition(self, message):
        if self.__check_if_rah(message.item) is True and message.item.state >= State.active:
            self.__rah_items.add(message.item)
            self.__dependencies_changed()

    def _handle_item_removal(self, message):
        if self.__check_if_rah(message.item) is True and message.item.state >= State.active:
            self.__rah_items.discard(message.item)
            self.__dependencies_changed()

    def _handle_state_switch(self, message):
        if self.__check_if_rah(message.item) is not True:
            return
        old_state, new_state = message.old, message.new
        if old_state < State.active and new_state >= State.active:
            self.__rah_items.add(message.item)
            self.__dependencies_changed()
        elif new_state < State.active and old_state >= State.active:
            self.__rah_items.discard(message.item)
            self.__dependencies_changed()

    def _handle_attr_change(self, message):
        # Ship resistances changed
        if message.item is self.__fit.ship and message.attr in res_attrs:
            self.__dependencies_changed()
        # RAH resistances, shift amount and cycle time
        elif message.item in self.__rah_items and (message.attr in (
            *res_attrs, Attribute.resistance_shift_amount,
            self.__get_duration_attr_id(message.item)
        )):
            self.__dependencies_changed()

    _handler_map = {
        ItemAdded: _handle_item_addition,
        ItemRemoved: _handle_item_removal,
        ItemStateChanged: _handle_state_switch,
        AttrValueChanged: _handle_attr_change,
        AttrValueChangedOverride: _handle_attr_change
    }

    def _notify(self, message):
        if self.__running is True:
            return
        try:
            handler = self._handler_map[type(message)]
        except KeyError:
            return
        handler(self, message)

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

    def __install_callbacks(self, item):
        for res_attr in res_attrs:
            item.attributes._set_override_callback(res_attr, (self.get_rah_resonance, (item, res_attr), {}))

    def __remove_callbacks(self, item):
        for res_attr in res_attrs:
            item.attributes._del_override_callback(res_attr)

    def __dependencies_changed(self):
        self.__simulation_results.clear()

    def get_rah_resonance(self, item, attr):
        return self.__simulation_results[item][attr]
