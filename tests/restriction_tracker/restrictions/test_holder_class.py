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


from eos.const.eos import Restriction, Slot
from eos.const.eve import Attribute, Group, Category
from eos.fit.holder.item import *
from tests.restriction_tracker.restriction_testcase import RestrictionTestCase


class TestHolderClass(RestrictionTestCase):
    """Check functionality of holder class verification"""

    def test_booster_pass(self):
        item = self.ch.type_(type_id=1, category=Category.implant, attributes={Attribute.boosterness: 3})
        holder = Booster(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_booster_fail_category(self):
        item = self.ch.type_(type_id=1, category=1008, attributes={Attribute.boosterness: 3})
        holder = Booster(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Booster)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_booster_fail_attr(self):
        item = self.ch.type_(type_id=1, category=Category.implant)
        holder = Booster(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Booster)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_character_pass(self):
        item = self.ch.type_(type_id=1, group=Group.character)
        holder = Character(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_character_fail_group(self):
        item = self.ch.type_(type_id=1, group=1008)
        holder = Character(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Character)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_charge_pass(self):
        item = self.ch.type_(type_id=1, category=Category.charge)
        holder = Charge(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_charge_fail_category(self):
        item = self.ch.type_(type_id=1, category=1008)
        holder = Charge(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Charge)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_drone_ass(self):
        item = self.ch.type_(type_id=1, category=Category.drone)
        holder = Drone(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_drone_fail_category(self):
        item = self.ch.type_(type_id=1, category=1008)
        holder = Drone(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Drone)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_effect_beacon_pass(self):
        item = self.ch.type_(type_id=1, group=Group.effect_beacon)
        holder = EffectBeacon(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_effect_beacon_fail_group(self):
        item = self.ch.type_(type_id=1, group=1008)
        holder = EffectBeacon(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, EffectBeacon)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_implant_pass(self):
        item = self.ch.type_(type_id=1, category=Category.implant, attributes={Attribute.implantness: 3})
        holder = Implant(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_implant_fail_category(self):
        item = self.ch.type_(type_id=1, category=1008, attributes={Attribute.implantness: 3})
        holder = Implant(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Implant)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_implant_fail_attr(self):
        item = self.ch.type_(type_id=1, category=Category.implant)
        holder = Implant(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Implant)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_module_high_pass(self):
        item = self.ch.type_(type_id=1, category=Category.module)
        item.slots = {Slot.module_high}
        holder = ModuleHigh(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_module_high_fail_category(self):
        item = self.ch.type_(type_id=1, category=1008)
        item.slots = {Slot.module_high}
        holder = ModuleHigh(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, ModuleHigh)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)

    def test_module_high_fail_slot(self):
        item = self.ch.type_(type_id=1, category=Category.module)
        item.slots = {1008}
        holder = ModuleHigh(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, ModuleHigh)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_module_medium_pass(self):
        item = self.ch.type_(type_id=1, category=Category.module)
        item.slots = {Slot.module_med}
        holder = ModuleMed(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_module_med_fail_category(self):
        item = self.ch.type_(type_id=1, category=1008)
        item.slots = {Slot.module_med}
        holder = ModuleMed(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, ModuleMed)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)

    def test_module_med_fail_slot(self):
        item = self.ch.type_(type_id=1, category=Category.module)
        item.slots = {1008}
        holder = ModuleMed(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, ModuleMed)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_module_low_pass(self):
        item = self.ch.type_(type_id=1, category=Category.module)
        item.slots = {Slot.module_low}
        holder = ModuleLow(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_module_low_fail_category(self):
        item = self.ch.type_(type_id=1, category=1008)
        item.slots = {Slot.module_low}
        holder = ModuleLow(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, ModuleLow)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)

    def test_module_low_fail_slot(self):
        item = self.ch.type_(type_id=1, category=Category.module)
        item.slots = {1008}
        holder = ModuleLow(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, ModuleLow)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_rig_pass(self):
        item = self.ch.type_(type_id=1, category=Category.module)
        item.slots = {Slot.rig}
        holder = Rig(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_rig_fail_category(self):
        item = self.ch.type_(type_id=1, category=1008)
        item.slots = {Slot.rig}
        holder = Rig(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Rig)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)

    def test_rig_fail_slot(self):
        item = self.ch.type_(type_id=1, category=Category.module)
        item.slots = {1008}
        holder = Rig(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Rig)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_ship_pass(self):
        item = self.ch.type_(type_id=1, category=Category.ship)
        holder = Ship(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_ship_fail_category(self):
        item = self.ch.type_(type_id=1, category=1008)
        holder = Ship(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Ship)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_skill_pass(self):
        item = self.ch.type_(type_id=1, category=Category.skill)
        holder = Skill(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_skill_fail_category(self):
        item = self.ch.type_(type_id=1, category=1008)
        holder = Skill(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Skill)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_stance_pass(self):
        item = self.ch.type_(type_id=1, group=Group.ship_modifier)
        holder = Stance(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_stance_fail_group(self):
        item = self.ch.type_(type_id=1, group=1008)
        holder = Stance(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Stance)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_subsystem_pass(self):
        item = self.ch.type_(type_id=1, category=Category.subsystem)
        item.slots = {Slot.subsystem}
        holder = Subsystem(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_subsystem_fail_category(self):
        item = self.ch.type_(type_id=1, category=1008)
        holder = Subsystem(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Subsystem)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_subsystem_fail_slot(self):
        item = self.ch.type_(type_id=1, category=Category.subsystem)
        item.slots = {1008}
        holder = Subsystem(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Subsystem)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_single_replacement(self):
        item = self.ch.type_(type_id=1, category=Category.implant, attributes={Attribute.boosterness: 3})
        holder = Implant(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Implant)
        self.assertEqual(len(restriction_error.expected_classes), 1)
        self.assertIn(Booster, restriction_error.expected_classes)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_multiple_replacements(self):
        item = self.ch.type_(type_id=1, category=Category.implant,
                             attributes={Attribute.boosterness: 3, Attribute.implantness: 1})
        holder = Drone(1)
        holder.item = item
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.holder_class)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.holder_class, Drone)
        self.assertEqual(len(restriction_error.expected_classes), 2)
        self.assertIn(Booster, restriction_error.expected_classes)
        self.assertIn(Implant, restriction_error.expected_classes)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
