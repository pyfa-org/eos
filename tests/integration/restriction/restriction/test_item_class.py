# ==============================================================================
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
# ==============================================================================


from eos import *
from eos.const.eve import (
    AttributeId, CategoryId, EffectId, EffectCategoryId, GroupId)
from tests.integration.restriction.restriction_testcase import (
    RestrictionTestCase)


class TestItemClass(RestrictionTestCase):
    """Check functionality of item class verification."""

    def test_booster_pass_no_source(self):
        # Make sure fit without a source doesn't cause any failures
        item = Booster(self.ch.type(
            category=1008, attributes={AttributeId.boosterness: 3}).id)
        self.fit.boosters.add(item)
        self.fit.source = None
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_booster_pass(self):
        item = Booster(self.ch.type(
            category=CategoryId.implant,
            attributes={AttributeId.boosterness: 3}).id)
        self.fit.boosters.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_booster_fail_category(self):
        item = Booster(self.ch.type(
            category=1008, attributes={AttributeId.boosterness: 3}).id)
        self.fit.boosters.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Booster)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_booster_fail_attr(self):
        item = Booster(self.ch.type(category=CategoryId.implant).id)
        self.fit.boosters.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Booster)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_character_pass(self):
        item = Character(self.ch.type(group=GroupId.character).id)
        self.fit.character = item
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_character_fail_group(self):
        item = Character(self.ch.type(group=1008).id)
        self.fit.character = item
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Character)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_charge_pass(self):
        item = Charge(self.ch.type(category=CategoryId.charge).id)
        container = ModuleHigh(self.ch.type().id)
        container.charge = item
        self.fit.modules.high.append(container)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_charge_fail_category(self):
        item = Charge(self.ch.type(category=1008).id)
        container = ModuleHigh(self.ch.type().id)
        container.charge = item
        self.fit.modules.high.append(container)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Charge)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_drone_pass(self):
        item = Drone(self.ch.type(category=CategoryId.drone).id)
        self.fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_drone_fail_category(self):
        item = Drone(self.ch.type(category=1008).id)
        self.fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Drone)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_effect_beacon_pass(self):
        item = EffectBeacon(self.ch.type(group=GroupId.effect_beacon).id)
        self.fit.effect_beacon = item
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_effect_beacon_fail_group(self):
        item = EffectBeacon(self.ch.type(group=1008).id)
        self.fit.effect_beacon = item
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, EffectBeacon)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_fighter_squad_pass(self):
        item = FighterSquad(self.ch.type(
            category=CategoryId.fighter,
            attributes={AttributeId.fighter_squadron_is_heavy: 1.0}).id)
        self.fit.fighters.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_fighter_squad_fail_category(self):
        item = FighterSquad(self.ch.type(
            category=1008,
            attributes={AttributeId.fighter_squadron_is_heavy: 1.0}).id)
        self.fit.fighters.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, FighterSquad)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_fighter_squad_fail_attr(self):
        item = FighterSquad(self.ch.type(category=CategoryId.fighter).id)
        self.fit.fighters.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, FighterSquad)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_implant_pass(self):
        item = Implant(self.ch.type(
            category=CategoryId.implant,
            attributes={AttributeId.implantness: 3}).id)
        self.fit.implants.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_implant_fail_category(self):
        item = Implant(self.ch.type(
            category=1008, attributes={AttributeId.implantness: 3}).id)
        self.fit.implants.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Implant)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_implant_fail_attr(self):
        item = Implant(self.ch.type(category=1008).id)
        self.fit.implants.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Implant)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_module_high_pass(self):
        effect = self.ch.effect(
            effect_id=EffectId.hi_power, category=EffectCategoryId.passive)
        item = ModuleHigh(self.ch.type(
            category=CategoryId.module, effects=[effect]).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_module_high_pass_disabled_effect(self):
        # Make sure disabled high slot effect doesn't prevent item from passing
        # the check
        effect = self.ch.effect(
            effect_id=EffectId.hi_power, category=EffectCategoryId.passive)
        item = ModuleHigh(self.ch.type(
            category=CategoryId.module, effects=[effect]).id)
        item.set_effect_run_mode(effect.id, EffectRunMode.force_stop)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_module_high_fail_category(self):
        effect = self.ch.effect(
            effect_id=EffectId.hi_power, category=EffectCategoryId.passive)
        item = ModuleHigh(self.ch.type(category=1008, effects=[effect]).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleHigh)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)

    def test_module_high_fail_effect(self):
        effect = self.ch.effect(
            effect_id=1008, category=EffectCategoryId.passive)
        item = ModuleHigh(self.ch.type(category=1008, effects=[effect]).id)
        self.fit.modules.high.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleHigh)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_module_medium_pass(self):
        effect = self.ch.effect(
            effect_id=EffectId.med_power, category=EffectCategoryId.passive)
        item = ModuleMed(self.ch.type(
            category=CategoryId.module, effects=[effect]).id)
        self.fit.modules.med.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_module_medium_pass_disabled_effect(self):
        effect = self.ch.effect(
            effect_id=EffectId.med_power, category=EffectCategoryId.passive)
        item = ModuleMed(self.ch.type(
            category=CategoryId.module, effects=[effect]).id)
        item.set_effect_run_mode(effect.id, EffectRunMode.force_stop)
        self.fit.modules.med.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_module_medium_fail_category(self):
        effect = self.ch.effect(
            effect_id=EffectId.med_power, category=EffectCategoryId.passive)
        item = ModuleMed(self.ch.type(category=1008, effects=[effect]).id)
        self.fit.modules.med.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleMed)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_module_medium_fail_effect(self):
        effect = self.ch.effect(
            effect_id=1008, category=EffectCategoryId.passive)
        item = ModuleMed(self.ch.type(
            category=CategoryId.module, effects=[effect]).id)
        self.fit.modules.med.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleMed)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_module_low_pass(self):
        effect = self.ch.effect(
            effect_id=EffectId.lo_power, category=EffectCategoryId.passive)
        item = ModuleLow(self.ch.type(
            category=CategoryId.module, effects=[effect]).id)
        self.fit.modules.low.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_module_low_pass_disabled_effect(self):
        effect = self.ch.effect(
            effect_id=EffectId.lo_power, category=EffectCategoryId.passive)
        item = ModuleLow(self.ch.type(
            category=CategoryId.module, effects=[effect]).id)
        item.set_effect_run_mode(effect.id, EffectRunMode.force_stop)
        self.fit.modules.low.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_module_low_fail_category(self):
        effect = self.ch.effect(
            effect_id=EffectId.lo_power, category=EffectCategoryId.passive)
        item = ModuleLow(self.ch.type(category=1008, effects=[effect]).id)
        self.fit.modules.low.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleLow)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_module_low_fail_effect(self):
        effect = self.ch.effect(
            effect_id=1008, category=EffectCategoryId.passive)
        item = ModuleLow(self.ch.type(
            category=CategoryId.module, effects=[effect]).id)
        self.fit.modules.low.append(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, ModuleLow)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_rig_pass(self):
        effect = self.ch.effect(
            effect_id=EffectId.rig_slot, category=EffectCategoryId.passive)
        item = Rig(self.ch.type(
            category=CategoryId.module, effects=[effect]).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_rig_pass_disabled_effect(self):
        effect = self.ch.effect(
            effect_id=EffectId.rig_slot, category=EffectCategoryId.passive)
        item = Rig(self.ch.type(
            category=CategoryId.module, effects=[effect]).id)
        item.set_effect_run_mode(effect.id, EffectRunMode.force_stop)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_rig_fail_category(self):
        effect = self.ch.effect(
            effect_id=EffectId.rig_slot, category=EffectCategoryId.passive)
        item = Rig(self.ch.type(category=1008, effects=[effect]).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Rig)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_rig_fail_effect(self):
        effect = self.ch.effect(
            effect_id=1008, category=EffectCategoryId.passive)
        item = Rig(self.ch.type(
            category=CategoryId.module, effects=[effect]).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Rig)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_ship_pass(self):
        item = Ship(self.ch.type(category=CategoryId.ship).id)
        self.fit.ship = item
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_ship_fail_category(self):
        item = Ship(self.ch.type(category=1008).id)
        self.fit.ship = item
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Ship)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_skill_pass(self):
        item = Skill(self.ch.type(category=CategoryId.skill).id)
        self.fit.skills.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_skill_fail_category(self):
        item = Skill(self.ch.type(category=1008).id)
        self.fit.skills.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Skill)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_stance_pass(self):
        item = Stance(self.ch.type(group=GroupId.ship_modifier).id)
        self.fit.stance = item
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_stance_fail_group(self):
        item = Stance(self.ch.type(group=1008).id)
        self.fit.stance = item
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Stance)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_subsystem_pass(self):
        effect = self.ch.effect(
            effect_id=EffectId.subsystem, category=EffectCategoryId.passive)
        item = Subsystem(self.ch.type(
            category=CategoryId.subsystem, effects=[effect]).id)
        self.fit.subsystems.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_subsystem_pass_disabled_effect(self):
        effect = self.ch.effect(
            effect_id=EffectId.subsystem, category=EffectCategoryId.passive)
        item = Subsystem(self.ch.type(
            category=CategoryId.subsystem, effects=[effect]).id)
        item.set_effect_run_mode(effect.id, EffectRunMode.force_stop)
        self.fit.subsystems.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_subsystem_fail_category(self):
        effect = self.ch.effect(
            effect_id=EffectId.subsystem, category=EffectCategoryId.passive)
        item = Subsystem(self.ch.type(category=1008, effects=[effect]).id)
        self.fit.subsystems.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Subsystem)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_subsystem_fail_effect(self):
        effect = self.ch.effect(
            effect_id=1008, category=EffectCategoryId.passive)
        item = Subsystem(self.ch.type(
            category=CategoryId.subsystem, effects=[effect]).id)
        self.fit.subsystems.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Subsystem)
        self.assertEqual(len(restriction_error.expected_classes), 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_single_replacement(self):
        item = Implant(self.ch.type(
            category=CategoryId.implant,
            attributes={AttributeId.boosterness: 3}).id)
        self.fit.implants.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Implant)
        self.assertEqual(len(restriction_error.expected_classes), 1)
        self.assertIn(Booster, restriction_error.expected_classes)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_multiple_replacements(self):
        item = Drone(self.ch.type(
            category=CategoryId.implant,
            attributes={
                AttributeId.boosterness: 3, AttributeId.implantness: 1}).id)
        self.fit.drones.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.item_class, Drone)
        self.assertEqual(len(restriction_error.expected_classes), 2)
        self.assertIn(Booster, restriction_error.expected_classes)
        self.assertIn(Implant, restriction_error.expected_classes)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
