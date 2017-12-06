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


from eos import DmgProfile
from eos import ModuleLow
from eos import Ship
from eos import Skill
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.sim.rah.testcase import RahSimTestCase


class TestRahSimCleanup(RahSimTestCase):

    def test_rah_added(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        # Force resonance calculation
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.9)
        # Action
        self.fit.modules.low.equip(rah)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.655)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.5895)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rah_removed(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Force resonance calculation
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.655)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.5895)
        # Action
        self.fit.modules.low.remove(rah)
        # Verification
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.9)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rah_state_switch_up(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.online)
        self.fit.modules.low.equip(rah)
        # Force resonance calculation
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.85)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.9)
        # Action
        rah.state = State.active
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.655)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.5895)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rah_state_switch_down(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Force resonance calculation
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.655)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.5895)
        # Action
        rah.state = State.online
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.85)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.9)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ship_resonance(self):
        # Setup
        skill_attr = self.mkattr(high_is_good=False, stackable=False)
        skill_modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=self.armor_therm.id,
            operator=ModOperator.post_mul,
            src_attr_id=skill_attr.id)
        skill_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[skill_modifier])
        skill_type = self.mktype(
            attrs={skill_attr.id: 0.5},
            effects=[skill_effect])
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        skill = Skill(skill_type.id)
        # Force resonance calculation
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.655)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.5895)
        # Action
        self.fit.skills.add(skill)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.7)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.7)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.325)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.525)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.63)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rah_resonance(self):
        # Setup
        skill_attr = self.mkattr(high_is_good=False, stackable=False)
        skill_modifier = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=self.armor_kin.id,
            operator=ModOperator.post_mul,
            src_attr_id=skill_attr.id)
        skill_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[skill_modifier])
        skill_type = self.mktype(
            attrs={skill_attr.id: 0.5},
            effects=[skill_effect])
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        skill = Skill(skill_type.id)
        # Force resonance calculation
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.655)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.5895)
        # Action
        self.fit.skills.add(skill)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.97)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.79)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.65)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.565)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.485)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.5135)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.4875)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.5085)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rah_shift(self):
        # Setup
        skill_attr = self.mkattr(high_is_good=False, stackable=False)
        skill_modifier = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=self.shift_attr.id,
            operator=ModOperator.post_mul,
            src_attr_id=skill_attr.id)
        skill_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[skill_modifier])
        skill_type = self.mktype(
            attrs={skill_attr.id: 0.1},
            effects=[skill_effect])
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        skill = Skill(skill_type.id)
        # Force resonance calculation
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.655)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.5895)
        # Action
        self.fit.skills.add(skill)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.928)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.802)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.67)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.6032)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.6015)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.603)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_cycle_time(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah_type = self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000)
        rah1 = ModuleLow(rah_type.id, state=State.active)
        rah2 = ModuleLow(rah_type.id, state=State.active)
        self.fit.modules.low.equip(rah1)
        self.fit.modules.low.equip(rah2)
        # Force resonance calculation
        self.assertAlmostEqual(rah1.attrs[self.armor_em.id], 0.97)
        self.assertAlmostEqual(rah1.attrs[self.armor_therm.id], 0.88)
        self.assertAlmostEqual(rah1.attrs[self.armor_kin.id], 0.805)
        self.assertAlmostEqual(rah1.attrs[self.armor_exp.id], 0.745)
        self.assertAlmostEqual(rah2.attrs[self.armor_em.id], 0.97)
        self.assertAlmostEqual(rah2.attrs[self.armor_therm.id], 0.88)
        self.assertAlmostEqual(rah2.attrs[self.armor_kin.id], 0.805)
        self.assertAlmostEqual(rah2.attrs[self.armor_exp.id], 0.745)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.472, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.512, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.501, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.522, places=3)
        # Action
        rah2.state = State.overload
        # Verification
        self.assertAlmostEqual(rah1.attrs[self.armor_em.id], 0.975, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_therm.id], 0.835, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_kin.id], 0.83, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_exp.id], 0.76, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_em.id], 0.979, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_therm.id], 0.91, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_kin.id], 0.796, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_exp.id], 0.715, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.479, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.5, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.509, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.509, places=3)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_dmg_profile_default(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Force resonance calculation
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 0.655)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.5895)
        # Action
        self.fit.default_incoming_dmg = DmgProfile(1, 0, 0, 0)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.4)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_exp.id], 1)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.2)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship.attrs[self.armor_exp.id], 0.9)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
