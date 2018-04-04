# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
from eos import FighterSquad
from eos import Implant
from eos import ModuleHigh
from eos import ModuleLow
from eos import ModuleMid
from eos import Restriction
from eos import Rig
from eos import Ship
from eos import Skill
from eos import Stance
from eos import Subsystem
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestLoadedItem(RestrictionTestCase):
    """Check functionality of loaded/unloaded item verification."""

    def test_pass_autocharge_not_loaded(self):
        container_effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.target)
        container = ModuleHigh(self.mktype(
            attrs={
                AttrId.charge_size: 3,
                AttrId.ammo_loaded: self.allocate_type_id()},
            effects=[container_effect]).id)
        self.fit.modules.high.append(container)
        self.assertIn(container_effect.id, container.autocharges)
        item = container.autocharges[container_effect.id]
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_booster_pass_loaded(self):
        item = Booster(self.mktype().id)
        self.fit.boosters.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_booster_fail_not_loaded(self):
        item = Booster(self.allocate_type_id())
        self.fit.boosters.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_character_pass_loaded(self):
        item = Character(self.mktype().id)
        self.fit.character = item
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_character_fail_not_loaded(self):
        item = Character(self.allocate_type_id())
        self.fit.character = item
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge_pass_loaded(self):
        item = Charge(self.mktype().id)
        container = ModuleHigh(self.mktype().id)
        container.charge = item
        self.fit.modules.high.append(container)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge_fail_not_loaded(self):
        item = Charge(self.allocate_type_id())
        container = ModuleHigh(self.mktype().id)
        container.charge = item
        self.fit.modules.high.append(container)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_drone_pass_loaded(self):
        item = Drone(self.mktype().id)
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_drone_fail_not_loaded(self):
        item = Drone(self.allocate_type_id())
        self.fit.drones.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effect_beacon_pass_loaded(self):
        item = EffectBeacon(self.mktype().id)
        self.fit.effect_beacon = item
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effect_beacon_fail_not_loaded(self):
        item = EffectBeacon(self.allocate_type_id())
        self.fit.effect_beacon = item
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fighter_squad_pass_loaded(self):
        item = FighterSquad(self.mktype().id)
        self.fit.fighters.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fighter_squad_fail_not_loaded(self):
        item = FighterSquad(self.allocate_type_id())
        self.fit.fighters.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_implant_pass_loaded(self):
        item = Implant(self.mktype().id)
        self.fit.implants.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_implant_fail_not_loaded(self):
        item = Implant(self.allocate_type_id())
        self.fit.implants.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_high_pass_loaded(self):
        item = ModuleHigh(self.mktype().id)
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_high_fail_not_loaded(self):
        item = ModuleHigh(self.allocate_type_id())
        self.fit.modules.high.append(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_mid_pass_loaded(self):
        item = ModuleMid(self.mktype().id)
        self.fit.modules.mid.append(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_mid_fail_not_loaded(self):
        item = ModuleMid(self.allocate_type_id())
        self.fit.modules.mid.append(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_low_pass_loaded(self):
        item = ModuleLow(self.mktype().id)
        self.fit.modules.low.append(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_low_fail_not_loaded(self):
        item = ModuleLow(self.allocate_type_id())
        self.fit.modules.low.append(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rig_pass_loaded(self):
        item = Rig(self.mktype().id)
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rig_fail_not_loaded(self):
        item = Rig(self.allocate_type_id())
        self.fit.rigs.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ship_pass_loaded(self):
        item = Ship(self.mktype().id)
        self.fit.ship = item
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ship_fail_not_loaded(self):
        item = Ship(self.allocate_type_id())
        self.fit.ship = item
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_skill_pass_loaded(self):
        item = Skill(self.mktype().id)
        self.fit.skills.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_skill_fail_not_loaded(self):
        item = Skill(self.allocate_type_id())
        self.fit.skills.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_stance_pass_loaded(self):
        item = Stance(self.mktype().id)
        self.fit.stance = item
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_stance_fail_not_loaded(self):
        item = Stance(self.allocate_type_id())
        self.fit.stance = item
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_subsystem_pass_loaded(self):
        item = Subsystem(self.mktype().id)
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_subsystem_fail_not_loaded(self):
        item = Subsystem(self.allocate_type_id())
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.loaded_item)
        # Verification
        self.assertIsNotNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
