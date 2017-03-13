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


from eos import *
from eos.const.eos import Restriction, Slot
from eos.const.eve import Attribute, Group, Category
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestItemClass(RestrictionTestCase):
    """Check functionality of item class verification"""

    def test_booster_pass(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.implant, attributes={Attribute.boosterness: 3})
        item = Booster(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_booster_fail_category(self):
        fit = Fit()
        eve_type = self.ch.type(category=1008, attributes={Attribute.boosterness: 3})
        item = Booster(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Booster)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_booster_fail_attr(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.implant)
        item = Booster(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Booster)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_character_pass(self):
        fit = Fit()
        eve_type = self.ch.type(group=Group.character)
        item = Character(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_character_fail_group(self):
        fit = Fit()
        eve_type = self.ch.type(group=1008)
        item = Character(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Character)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_charge_pass(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.charge)
        item = Charge(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_charge_fail_category(self):
        fit = Fit()
        eve_type = self.ch.type(category=1008)
        item = Charge(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Charge)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_drone_ass(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.drone)
        item = Drone(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_drone_fail_category(self):
        fit = Fit()
        eve_type = self.ch.type(category=1008)
        item = Drone(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Drone)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_effect_beacon_pass(self):
        fit = Fit()
        eve_type = self.ch.type(group=Group.effect_beacon)
        item = EffectBeacon(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_effect_beacon_fail_group(self):
        fit = Fit()
        eve_type = self.ch.type(group=1008)
        item = EffectBeacon(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, EffectBeacon)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_implant_pass(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.implant, attributes={Attribute.implantness: 3})
        item = Implant(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_implant_fail_category(self):
        fit = Fit()
        eve_type = self.ch.type(category=1008, attributes={Attribute.implantness: 3})
        item = Implant(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Implant)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_implant_fail_attr(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.implant)
        item = Implant(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Implant)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_module_high_pass(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.module)
        eve_type.slots = {Slot.module_high}
        item = ModuleHigh(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_module_high_fail_category(self):
        fit = Fit()
        eve_type = self.ch.type(category=1008)
        eve_type.slots = {Slot.module_high}
        item = ModuleHigh(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleHigh)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)

    def test_module_high_fail_slot(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.module)
        eve_type.slots = {1008}
        item = ModuleHigh(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleHigh)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_module_medium_pass(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.module)
        eve_type.slots = {Slot.module_med}
        item = ModuleMed(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_module_med_fail_category(self):
        fit = Fit()
        eve_type = self.ch.type(category=1008)
        eve_type.slots = {Slot.module_med}
        item = ModuleMed(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleMed)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_module_med_fail_slot(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.module)
        eve_type.slots = {1008}
        item = ModuleMed(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleMed)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_module_low_pass(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.module)
        eve_type.slots = {Slot.module_low}
        item = ModuleLow(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_module_low_fail_category(self):
        fit = Fit()
        eve_type = self.ch.type(category=1008)
        eve_type.slots = {Slot.module_low}
        item = ModuleLow(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleLow)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_module_low_fail_slot(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.module)
        eve_type.slots = {1008}
        item = ModuleLow(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleLow)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_rig_pass(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.module)
        eve_type.slots = {Slot.rig}
        item = Rig(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_rig_fail_category(self):
        fit = Fit()
        eve_type = self.ch.type(category=1008)
        eve_type.slots = {Slot.rig}
        item = Rig(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Rig)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_rig_fail_slot(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.module)
        eve_type.slots = {1008}
        item = Rig(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Rig)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_ship_pass(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.ship)
        item = Ship(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_ship_fail_category(self):
        fit = Fit()
        eve_type = self.ch.type(category=1008)
        item = Ship(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Ship)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_skill_pass(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.skill)
        item = Skill(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_skill_fail_category(self):
        fit = Fit()
        eve_type = self.ch.type(category=1008)
        item = Skill(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Skill)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_stance_pass(self):
        fit = Fit()
        eve_type = self.ch.type(group=Group.ship_modifier)
        item = Stance(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_stance_fail_group(self):
        fit = Fit()
        eve_type = self.ch.type(group=1008)
        item = Stance(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Stance)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_subsystem_pass(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.subsystem)
        eve_type.slots = {Slot.subsystem}
        item = Subsystem(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_subsystem_fail_category(self):
        fit = Fit()
        eve_type = self.ch.type(category=1008)
        item = Subsystem(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Subsystem)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_subsystem_fail_slot(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.subsystem)
        eve_type.slots = {1008}
        item = Subsystem(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Subsystem)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_single_replacement(self):
        fit = Fit()
        eve_type = self.ch.type(category=Category.implant, attributes={Attribute.boosterness: 3})
        item = Implant(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Implant)
        self.assertEqual(len(restriction_error.expected_classes), 1)
        self.assertIn(Booster, restriction_error.expected_classes)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_multiple_replacements(self):
        fit = Fit()
        eve_type = self.ch.type(
            type_id=1, category=Category.implant, attributes={Attribute.boosterness: 3, Attribute.implantness: 1})
        item = Drone(eve_type.id)
        item._eve_type = eve_type
        fit._items.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Drone)
        self.assertEqual(len(restriction_error.expected_classes), 2)
        self.assertIn(Booster, restriction_error.expected_classes)
        self.assertIn(Implant, restriction_error.expected_classes)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
