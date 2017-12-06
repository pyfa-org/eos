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


from eos import Booster
from eos import Character
from eos import Charge
from eos import Drone
from eos import EffectBeacon
from eos import EffectMode
from eos import FighterSquad
from eos import Implant
from eos import ModuleHigh
from eos import ModuleLow
from eos import ModuleMed
from eos import Restriction
from eos import Rig
from eos import Ship
from eos import Skill
from eos import Stance
from eos import Subsystem
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.const.eve import TypeCategoryId
from eos.const.eve import TypeGroupId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestItemClass(RestrictionTestCase):
    """Check functionality of item class verification."""

    def test_booster_pass_no_source(self):
        # Make sure fit without a source doesn't cause any failures
        item = Booster(self.mktype(
            category_id=1008,
            attrs={AttrId.boosterness: 3}).id)
        self.fit.boosters.add(item)
        self.fit.source = None
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_booster_pass(self):
        item = Booster(self.mktype(
            category_id=TypeCategoryId.implant,
            attrs={AttrId.boosterness: 3}).id)
        self.fit.boosters.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_booster_fail_category(self):
        item = Booster(self.mktype(
            category_id=1008,
            attrs={AttrId.boosterness: 3}).id)
        self.fit.boosters.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Booster)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_booster_fail_attr(self):
        item = Booster(self.mktype(category_id=TypeCategoryId.implant).id)
        self.fit.boosters.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Booster)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_character_pass(self):
        item = Character(self.mktype(group_id=TypeGroupId.character).id)
        self.fit.character = item
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_character_fail_group(self):
        item = Character(self.mktype(group_id=1008).id)
        self.fit.character = item
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Character)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge_pass(self):
        item = Charge(self.mktype(category_id=TypeCategoryId.charge).id)
        container = ModuleHigh(self.mktype().id)
        container.charge = item
        self.fit.modules.high.append(container)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge_fail_category(self):
        item = Charge(self.mktype(category_id=1008).id)
        container = ModuleHigh(self.mktype().id)
        container.charge = item
        self.fit.modules.high.append(container)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Charge)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_drone_pass(self):
        item = Drone(self.mktype(category_id=TypeCategoryId.drone).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_drone_fail_category(self):
        item = Drone(self.mktype(category_id=1008).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Drone)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effect_beacon_pass(self):
        item = EffectBeacon(self.mktype(group_id=TypeGroupId.effect_beacon).id)
        self.fit.effect_beacon = item
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effect_beacon_fail_group(self):
        item = EffectBeacon(self.mktype(group_id=1008).id)
        self.fit.effect_beacon = item
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, EffectBeacon)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fighter_squad_pass(self):
        item = FighterSquad(self.mktype(
            category_id=TypeCategoryId.fighter,
            attrs={AttrId.fighter_squadron_is_heavy: 1.0}).id)
        self.fit.fighters.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fighter_squad_fail_category(self):
        item = FighterSquad(self.mktype(
            category_id=1008,
            attrs={AttrId.fighter_squadron_is_heavy: 1.0}).id)
        self.fit.fighters.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, FighterSquad)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fighter_squad_fail_attr(self):
        item = FighterSquad(self.mktype(category_id=TypeCategoryId.fighter).id)
        self.fit.fighters.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, FighterSquad)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_implant_pass(self):
        item = Implant(self.mktype(
            category_id=TypeCategoryId.implant,
            attrs={AttrId.implantness: 3}).id)
        self.fit.implants.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_implant_fail_category(self):
        item = Implant(self.mktype(
            category_id=1008,
            attrs={AttrId.implantness: 3}).id)
        self.fit.implants.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Implant)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_implant_fail_attr(self):
        item = Implant(self.mktype(category_id=1008).id)
        self.fit.implants.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Implant)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_high_pass(self):
        effect = self.mkeffect(
            effect_id=EffectId.hi_power,
            category_id=EffectCategoryId.passive)
        item = ModuleHigh(self.mktype(
            category_id=TypeCategoryId.module,
            effects=[effect]).id)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_high_pass_disabled_effect(self):
        # Make sure disabled high slot effect doesn't prevent item from passing
        # the check
        effect = self.mkeffect(
            effect_id=EffectId.hi_power,
            category_id=EffectCategoryId.passive)
        item = ModuleHigh(self.mktype(
            category_id=TypeCategoryId.module,
            effects=[effect]).id)
        item.set_effect_mode(effect.id, EffectMode.force_stop)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_high_fail_category(self):
        effect = self.mkeffect(
            effect_id=EffectId.hi_power,
            category_id=EffectCategoryId.passive)
        item = ModuleHigh(self.mktype(category_id=1008, effects=[effect]).id)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, ModuleHigh)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_high_fail_effect(self):
        effect = self.mkeffect(
            effect_id=1008,
            category_id=EffectCategoryId.passive)
        item = ModuleHigh(self.mktype(category_id=1008, effects=[effect]).id)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, ModuleHigh)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_medium_pass(self):
        effect = self.mkeffect(
            effect_id=EffectId.med_power,
            category_id=EffectCategoryId.passive)
        item = ModuleMed(self.mktype(
            category_id=TypeCategoryId.module,
            effects=[effect]).id)
        self.fit.modules.med.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_medium_pass_disabled_effect(self):
        effect = self.mkeffect(
            effect_id=EffectId.med_power,
            category_id=EffectCategoryId.passive)
        item = ModuleMed(self.mktype(
            category_id=TypeCategoryId.module,
            effects=[effect]).id)
        item.set_effect_mode(effect.id, EffectMode.force_stop)
        self.fit.modules.med.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_medium_fail_category(self):
        effect = self.mkeffect(
            effect_id=EffectId.med_power,
            category_id=EffectCategoryId.passive)
        item = ModuleMed(self.mktype(category_id=1008, effects=[effect]).id)
        self.fit.modules.med.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, ModuleMed)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_medium_fail_effect(self):
        effect = self.mkeffect(
            effect_id=1008,
            category_id=EffectCategoryId.passive)
        item = ModuleMed(self.mktype(
            category_id=TypeCategoryId.module,
            effects=[effect]).id)
        self.fit.modules.med.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, ModuleMed)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_low_pass(self):
        effect = self.mkeffect(
            effect_id=EffectId.lo_power,
            category_id=EffectCategoryId.passive)
        item = ModuleLow(self.mktype(
            category_id=TypeCategoryId.module,
            effects=[effect]).id)
        self.fit.modules.low.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_low_pass_disabled_effect(self):
        effect = self.mkeffect(
            effect_id=EffectId.lo_power,
            category_id=EffectCategoryId.passive)
        item = ModuleLow(self.mktype(
            category_id=TypeCategoryId.module,
            effects=[effect]).id)
        item.set_effect_mode(effect.id, EffectMode.force_stop)
        self.fit.modules.low.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_low_fail_category(self):
        effect = self.mkeffect(
            effect_id=EffectId.lo_power,
            category_id=EffectCategoryId.passive)
        item = ModuleLow(self.mktype(category_id=1008, effects=[effect]).id)
        self.fit.modules.low.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, ModuleLow)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_low_fail_effect(self):
        effect = self.mkeffect(
            effect_id=1008,
            category_id=EffectCategoryId.passive)
        item = ModuleLow(self.mktype(
            category_id=TypeCategoryId.module,
            effects=[effect]).id)
        self.fit.modules.low.append(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, ModuleLow)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rig_pass(self):
        effect = self.mkeffect(
            effect_id=EffectId.rig_slot,
            category_id=EffectCategoryId.passive)
        item = Rig(self.mktype(
            category_id=TypeCategoryId.module,
            effects=[effect]).id)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rig_pass_disabled_effect(self):
        effect = self.mkeffect(
            effect_id=EffectId.rig_slot,
            category_id=EffectCategoryId.passive)
        item = Rig(self.mktype(
            category_id=TypeCategoryId.module,
            effects=[effect]).id)
        item.set_effect_mode(effect.id, EffectMode.force_stop)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rig_fail_category(self):
        effect = self.mkeffect(
            effect_id=EffectId.rig_slot,
            category_id=EffectCategoryId.passive)
        item = Rig(self.mktype(category_id=1008, effects=[effect]).id)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Rig)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rig_fail_effect(self):
        effect = self.mkeffect(
            effect_id=1008,
            category_id=EffectCategoryId.passive)
        item = Rig(self.mktype(
            category_id=TypeCategoryId.module,
            effects=[effect]).id)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Rig)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ship_pass(self):
        item = Ship(self.mktype(category_id=TypeCategoryId.ship).id)
        self.fit.ship = item
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ship_fail_category(self):
        item = Ship(self.mktype(category_id=1008).id)
        self.fit.ship = item
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Ship)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_skill_pass(self):
        item = Skill(self.mktype(category_id=TypeCategoryId.skill).id)
        self.fit.skills.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_skill_fail_category(self):
        item = Skill(self.mktype(category_id=1008).id)
        self.fit.skills.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Skill)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_stance_pass(self):
        item = Stance(self.mktype(group_id=TypeGroupId.ship_modifier).id)
        self.fit.stance = item
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_stance_fail_group(self):
        item = Stance(self.mktype(group_id=1008).id)
        self.fit.stance = item
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Stance)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_subsystem_pass(self):
        effect = self.mkeffect(
            effect_id=EffectId.subsystem,
            category_id=EffectCategoryId.passive)
        item = Subsystem(self.mktype(
            category_id=TypeCategoryId.subsystem,
            effects=[effect]).id)
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_subsystem_pass_disabled_effect(self):
        effect = self.mkeffect(
            effect_id=EffectId.subsystem,
            category_id=EffectCategoryId.passive)
        item = Subsystem(self.mktype(
            category_id=TypeCategoryId.subsystem,
            effects=[effect]).id)
        item.set_effect_mode(effect.id, EffectMode.force_stop)
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_subsystem_fail_category(self):
        effect = self.mkeffect(
            effect_id=EffectId.subsystem,
            category_id=EffectCategoryId.passive)
        item = Subsystem(self.mktype(category_id=1008, effects=[effect]).id)
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Subsystem)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_subsystem_fail_effect(self):
        effect = self.mkeffect(
            effect_id=1008,
            category_id=EffectCategoryId.passive)
        item = Subsystem(self.mktype(
            category_id=TypeCategoryId.subsystem,
            effects=[effect]).id)
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Subsystem)
        self.assertCountEqual(error.allowed_classes, [])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_replacement(self):
        item = Implant(self.mktype(
            category_id=TypeCategoryId.implant,
            attrs={AttrId.boosterness: 3}).id)
        self.fit.implants.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Implant)
        self.assertCountEqual(error.allowed_classes, [Booster])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_multiple_replacements(self):
        item = Drone(self.mktype(
            category_id=TypeCategoryId.implant,
            attrs={AttrId.boosterness: 3, AttrId.implantness: 1}).id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.item_class)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.item_class, Drone)
        self.assertCountEqual(error.allowed_classes, [Booster, Implant])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
