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
from eos.const.eve import Attribute, Effect, EffectCategory, Group, Category
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestItemClass(RestrictionTestCase):
    """Check functionality of item class verification"""

    def test_booster_pass(self):
        fit = Fit()
        item = Booster(self.ch.type(category=Category.implant, attributes={Attribute.boosterness: 3}).id)
        fit.boosters.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_booster_fail_category(self):
        fit = Fit()
        item = Booster(self.ch.type(category=1008, attributes={Attribute.boosterness: 3}).id)
        fit.boosters.add(item)
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
        item = Booster(self.ch.type(category=Category.implant).id)
        fit.boosters.add(item)
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
        item = Character(self.ch.type(group=Group.character).id)
        fit.character = item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_character_fail_group(self):
        fit = Fit()
        item = Character(self.ch.type(group=1008).id)
        fit.character = item
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
        item = Charge(self.ch.type(category=Category.charge).id)
        container = ModuleHigh(self.ch.type().id)
        container.charge = item
        fit.modules.high.append(container)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_charge_fail_category(self):
        fit = Fit()
        item = Charge(self.ch.type(category=1008).id)
        container = ModuleHigh(self.ch.type().id)
        container.charge = item
        fit.modules.high.append(container)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Charge)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_drone_pass(self):
        fit = Fit()
        item = Drone(self.ch.type(category=Category.drone).id)
        fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_drone_fail_category(self):
        fit = Fit()
        item = Drone(self.ch.type(category=1008).id)
        fit.drones.add(item)
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
        item = EffectBeacon(self.ch.type(group=Group.effect_beacon).id)
        fit.effect_beacon = item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_effect_beacon_fail_group(self):
        fit = Fit()
        item = EffectBeacon(self.ch.type(group=1008).id)
        fit.effect_beacon = item
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
        item = Implant(self.ch.type(category=Category.implant, attributes={Attribute.implantness: 3}).id)
        fit.implants.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_implant_fail_category(self):
        fit = Fit()
        item = Implant(self.ch.type(category=1008, attributes={Attribute.implantness: 3}).id)
        fit.implants.add(item)
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
        item = Implant(self.ch.type(category=1008).id)
        fit.implants.add(item)
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
        effect = self.ch.effect(effect_id=Effect.hi_power, category=EffectCategory.passive)
        item = ModuleHigh(self.ch.type(category=Category.module, effects=[effect]).id)
        fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_module_high_fail_category(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.hi_power, category=EffectCategory.passive)
        item = ModuleHigh(self.ch.type(category=1008, effects=[effect]).id)
        fit.modules.high.append(item)
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
        effect = self.ch.effect(effect_id=1008, category=EffectCategory.passive)
        item = ModuleHigh(self.ch.type(category=1008, effects=[effect]).id)
        fit.modules.high.append(item)
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
        effect = self.ch.effect(effect_id=Effect.med_power, category=EffectCategory.passive)
        item = ModuleMed(self.ch.type(category=Category.module, effects=[effect]).id)
        fit.modules.med.append(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_module_med_fail_category(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.med_power, category=EffectCategory.passive)
        item = ModuleMed(self.ch.type(category=1008, effects=[effect]).id)
        fit.modules.med.append(item)
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
        effect = self.ch.effect(effect_id=1008, category=EffectCategory.passive)
        item = ModuleMed(self.ch.type(category=Category.module, effects=[effect]).id)
        fit.modules.med.append(item)
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
        effect = self.ch.effect(effect_id=Effect.lo_power, category=EffectCategory.passive)
        item = ModuleLow(self.ch.type(category=Category.module, effects=[effect]).id)
        fit.modules.low.append(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_module_low_fail_category(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.lo_power, category=EffectCategory.passive)
        item = ModuleLow(self.ch.type(category=1008, effects=[effect]).id)
        fit.modules.low.append(item)
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
        effect = self.ch.effect(effect_id=1008, category=EffectCategory.passive)
        item = ModuleLow(self.ch.type(category=Category.module, effects=[effect]).id)
        fit.modules.low.append(item)
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
        effect = self.ch.effect(effect_id=Effect.rig_slot, category=EffectCategory.passive)
        item = Rig(self.ch.type(category=Category.module, effects=[effect]).id)
        fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_rig_fail_category(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.rig_slot, category=EffectCategory.passive)
        item = Rig(self.ch.type(category=1008, effects=[effect]).id)
        fit.rigs.add(item)
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
        effect = self.ch.effect(effect_id=1008, category=EffectCategory.passive)
        item = Rig(self.ch.type(category=Category.module, effects=[effect]).id)
        fit.rigs.add(item)
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
        item = Ship(self.ch.type(category=Category.ship).id)
        fit.ship = item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_ship_fail_category(self):
        fit = Fit()
        item = Ship(self.ch.type(category=1008).id)
        fit.ship = item
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
        item = Skill(self.ch.type(category=Category.skill).id)
        fit.skills.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_skill_fail_category(self):
        fit = Fit()
        item = Skill(self.ch.type(category=1008).id)
        fit.skills.add(item)
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
        item = Stance(self.ch.type(group=Group.ship_modifier).id)
        fit.stance = item
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_stance_fail_group(self):
        fit = Fit()
        item = Stance(self.ch.type(group=1008).id)
        fit.stance = item
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
        effect = self.ch.effect(effect_id=Effect.subsystem, category=EffectCategory.passive)
        item = Subsystem(self.ch.type(category=Category.subsystem, effects=[effect]).id)
        fit.subsystems.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_subsystem_fail_category(self):
        fit = Fit()
        effect = self.ch.effect(effect_id=Effect.subsystem, category=EffectCategory.passive)
        item = Subsystem(self.ch.type(category=1008, effects=[effect]).id)
        fit.subsystems.add(item)
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
        effect = self.ch.effect(effect_id=1008, category=EffectCategory.passive)
        item = Subsystem(self.ch.type(category=Category.subsystem, effects=[effect]).id)
        fit.subsystems.add(item)
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
        item = Implant(self.ch.type(category=Category.implant, attributes={Attribute.boosterness: 3}).id)
        fit.implants.add(item)
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
        item = Drone(self.ch.type(
            category=Category.implant, attributes={Attribute.boosterness: 3, Attribute.implantness: 1}
        ).id)
        fit.drones.add(item)
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
