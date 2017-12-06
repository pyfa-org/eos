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
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.source.testcase import SourceTestCase


class TestSourceSwitchItemClass(SourceTestCase):
    """Check that all item classes switch source properly."""

    def setUp(self):
        SourceTestCase.setUp(self)
        self.src_attr_id = self.allocate_attr_id('src1', 'src2')
        self.tgt_attr_id = self.allocate_attr_id('src1', 'src2')
        self.mkattr(src='src1', attr_id=self.src_attr_id)
        self.mkattr(src='src2', attr_id=self.src_attr_id)
        self.mkattr(src='src1', attr_id=self.tgt_attr_id)
        self.mkattr(src='src2', attr_id=self.tgt_attr_id)

    def prepare_item_type(self):
        """Prepare item type for source switch test.

        Create item type in both sources. Both items modify target attribute on
        itself: item in source1 will have its value at 18, item in source2 - 14,
        if everything is processed correctly.

        Returns:
            Item type ID.
        """
        modifier_src1 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_filter_extra_arg=None,
            tgt_attr_id=self.tgt_attr_id,
            operator=ModOperator.mod_add,
            src_attr_id=self.src_attr_id)
        modifier_src2 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_filter_extra_arg=None,
            tgt_attr_id=self.tgt_attr_id,
            operator=ModOperator.post_mul,
            src_attr_id=self.src_attr_id)
        effect_src1 = self.mkeffect(
            src='src1',
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_src1])
        effect_src2 = self.mkeffect(
            src='src2',
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_src2])
        item_type_id = self.allocate_type_id('src1', 'src2')
        self.mktype(
            src='src1',
            type_id=item_type_id,
            attrs={self.src_attr_id: 5, self.tgt_attr_id: 13},
            effects=[effect_src1])
        self.mktype(
            src='src2',
            type_id=item_type_id,
            attrs={self.src_attr_id: 2, self.tgt_attr_id: 7},
            effects=[effect_src2])
        return item_type_id

    def test_booster(self):
        booster = Booster(self.prepare_item_type())
        self.fit.boosters.add(booster)
        self.assertAlmostEqual(booster.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(booster.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_character(self):
        character = Character(self.prepare_item_type())
        self.fit.character = character
        self.assertAlmostEqual(character.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(character.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge(self):
        module = ModuleHigh(self.prepare_item_type())
        charge = Charge(self.prepare_item_type())
        module.charge = charge
        self.fit.modules.high.append(module)
        self.assertAlmostEqual(charge.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(charge.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_drone(self):
        drone = Drone(self.prepare_item_type())
        self.fit.drones.add(drone)
        self.assertAlmostEqual(drone.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(drone.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effect_beacon(self):
        effect_beacon = EffectBeacon(self.prepare_item_type())
        self.fit.effect_beacon = effect_beacon
        self.assertAlmostEqual(effect_beacon.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(effect_beacon.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fighter_squad(self):
        fighter_squad = FighterSquad(self.prepare_item_type())
        self.fit.fighters.add(fighter_squad)
        self.assertAlmostEqual(fighter_squad.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(fighter_squad.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_implant(self):
        implant = Implant(self.prepare_item_type())
        self.fit.implants.add(implant)
        self.assertAlmostEqual(implant.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(implant.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_high(self):
        module = ModuleHigh(self.prepare_item_type())
        self.fit.modules.high.append(module)
        self.assertAlmostEqual(module.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(module.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_med(self):
        module = ModuleMed(self.prepare_item_type())
        self.fit.modules.med.append(module)
        self.assertAlmostEqual(module.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(module.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_module_low(self):
        module = ModuleLow(self.prepare_item_type())
        self.fit.modules.low.append(module)
        self.assertAlmostEqual(module.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(module.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rig(self):
        rig = Rig(self.prepare_item_type())
        self.fit.rigs.add(rig)
        self.assertAlmostEqual(rig.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(rig.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ship(self):
        ship = Ship(self.prepare_item_type())
        self.fit.ship = ship
        self.assertAlmostEqual(ship.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(ship.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_skill(self):
        skill = Skill(self.prepare_item_type())
        self.fit.skills.add(skill)
        self.assertAlmostEqual(skill.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(skill.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_stance(self):
        stance = Stance(self.prepare_item_type())
        self.fit.stance = stance
        self.assertAlmostEqual(stance.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(stance.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_subsystem(self):
        subsystem = Subsystem(self.prepare_item_type())
        self.fit.subsystems.add(subsystem)
        self.assertAlmostEqual(subsystem.attrs[self.tgt_attr_id], 18)
        # Action
        self.fit.source = 'src2'
        # Verification
        self.assertAlmostEqual(subsystem.attrs[self.tgt_attr_id], 14)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
