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


import logging
from unittest.mock import patch

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


class TestRahSimResult(RahSimTestCase):

    @patch('eos.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=7)
    def test_single_run(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.655)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.5895)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    @patch('eos.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=8)
    def test_double_run(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah_type = self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000)
        rah1 = ModuleLow(rah_type.id, state=State.active)
        rah2 = ModuleLow(rah_type.id, state=State.active)
        self.fit.modules.low.equip(rah1)
        self.fit.modules.low.equip(rah2)
        # Verification
        self.assertAlmostEqual(rah1.attrs[self.armor_em.id], 0.97)
        self.assertAlmostEqual(rah1.attrs[self.armor_therm.id], 0.88)
        self.assertAlmostEqual(rah1.attrs[self.armor_kin.id], 0.805)
        self.assertAlmostEqual(rah1.attrs[self.armor_expl.id], 0.745)
        self.assertAlmostEqual(rah2.attrs[self.armor_em.id], 0.97)
        self.assertAlmostEqual(rah2.attrs[self.armor_therm.id], 0.88)
        self.assertAlmostEqual(rah2.attrs[self.armor_kin.id], 0.805)
        self.assertAlmostEqual(rah2.attrs[self.armor_expl.id], 0.745)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.472, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.512, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.501, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.522, places=3)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    @patch('eos.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=82)
    def test_double_run_unsynced(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah_type = self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000)
        rah1 = ModuleLow(rah_type.id, state=State.active)
        rah2 = ModuleLow(rah_type.id, state=State.overload)
        self.fit.modules.low.equip(rah1)
        self.fit.modules.low.equip(rah2)
        # Verification
        self.assertAlmostEqual(rah1.attrs[self.armor_em.id], 0.975, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_therm.id], 0.835, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_kin.id], 0.83, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_expl.id], 0.76, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_em.id], 0.979, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_therm.id], 0.91, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_kin.id], 0.796, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_expl.id], 0.715, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.479, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.5, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.509, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.509, places=3)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    @patch('eos.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=75)
    def test_no_loop_ignore_initial_adaptation(self):
        # Same as double unsynced, but with quantity of ticks insufficient to
        # detect loop
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah_type = self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000)
        rah1 = ModuleLow(rah_type.id, state=State.active)
        rah2 = ModuleLow(rah_type.id, state=State.overload)
        self.fit.modules.low.equip(rah1)
        self.fit.modules.low.equip(rah2)
        # Verification
        # We ignored 10 first ticks, which corresponds to 5 cycles of non-heated
        # RAH ceil(ceil(15 / 6) * 1.5). 10 ticks instead of 5 because heated RAH
        # is also cycling, and we stop taking ticks only when slowest (unheated)
        # RAH just finished 5th cycle
        self.assertAlmostEqual(rah1.attrs[self.armor_em.id], 0.971, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_therm.id], 0.834, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_kin.id], 0.834, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_expl.id], 0.761, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_em.id], 0.987, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_therm.id], 0.912, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_kin.id], 0.789, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_expl.id], 0.712, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.48, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.501, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.506, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.508, places=3)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    @patch('eos.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=5)
    def test_no_loop_half_history(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah_type = self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000)
        rah1 = ModuleLow(rah_type.id, state=State.active)
        rah2 = ModuleLow(rah_type.id, state=State.overload)
        self.fit.modules.low.equip(rah1)
        self.fit.modules.low.equip(rah2)
        # Verification
        # Same as previous test, but here whole history is just 5 ticks, and we
        # cannot ignore all of them - here we should ignore just 2 first ticks
        self.assertAlmostEqual(rah1.attrs[self.armor_em.id], 0.94, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_therm.id], 0.88, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_kin.id], 0.82, places=3)
        self.assertAlmostEqual(rah1.attrs[self.armor_expl.id], 0.76, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_em.id], 0.97, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_therm.id], 0.85, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_kin.id], 0.85, places=3)
        self.assertAlmostEqual(rah2.attrs[self.armor_expl.id], 0.73, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.458, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.495, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.535, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.52, places=3)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    @patch('eos.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=3)
    def test_order_multi(self):
        # Setup
        ship = Ship(self.make_ship_type((0.675, 0.675, 0.675, 0.675)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Verification
        # From real tests, gecko vs gnosis
        # ---loop---
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.790 0.910 (kin therm > em expl)
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.88)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.88)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.594, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.554, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.554, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.594, places=3)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    @patch('eos.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=7)
    def test_order_therm_kin_exp(self):
        # Setup
        self.fit.rah_incoming_dmg = DmgProfile(0, 1, 1, 1)
        ship = Ship(self.make_ship_type((0.675, 0.675, 0.675, 0.675)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Verification
        # From real tests, gecko vs gnosis with 2 EM hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.790 0.910 (kin therm > expl)
        # 2 0.970 0.730 0.850 0.850 (therm > kin)
        # ---loop---
        # 3 1.000 0.790 0.805 0.805
        # 4 1.000 0.850 0.775 0.775
        # 5 1.000 0.820 0.745 0.835 (kin > expl)
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.775)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.805)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.675, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.553, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.523, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.543, places=3)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    @patch('eos.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=7)
    def test_order_em_kin_exp(self):
        # Setup
        self.fit.rah_incoming_dmg = DmgProfile(1, 0, 1, 1)
        ship = Ship(self.make_ship_type((0.675, 0.675, 0.675, 0.675)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Verification
        # From real tests, gecko vs gnosis with 2 thermal hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.910 0.790 0.790 (kin expl > em)
        # 2 0.850 0.970 0.730 0.850 (kin > expl)
        # ---loop---
        # 3 0.805 1.000 0.790 0.805
        # 4 0.775 1.000 0.850 0.775
        # 5 0.835 1.000 0.820 0.745 (expl > em)
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.805)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.775)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.543, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.675, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.553, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.523, places=3)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    @patch('eos.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=7)
    def test_order_em_therm_exp(self):
        # Setup
        self.fit.rah_incoming_dmg = DmgProfile(1, 1, 0, 1)
        ship = Ship(self.make_ship_type((0.675, 0.675, 0.675, 0.675)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Verification
        # From real tests, gecko vs gnosis with 2 kinetic hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.910 0.790 (expl therm > em)
        # 2 0.850 0.730 0.970 0.850 (therm > expl)
        # ---loop---
        # 3 0.805 0.790 1.000 0.805
        # 4 0.775 0.850 1.000 0.775
        # 5 0.835 0.820 1.000 0.745 (expl > em)
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.805)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 1)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.775)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.543, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.553, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.675, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.523, places=3)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    @patch('eos.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=7)
    def test_order_em_therm_kin(self):
        # Setup
        self.fit.rah_incoming_dmg = DmgProfile(1, 1, 1, 0)
        ship = Ship(self.make_ship_type((0.675, 0.675, 0.675, 0.675)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Verification
        # From real tests, gecko vs gnosis with 2 explosive hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.790 0.910 (kin therm > em)
        # 2 0.850 0.730 0.850 0.970 (therm > kin)
        # ---loop---
        # 3 0.805 0.790 0.805 1.000
        # 4 0.775 0.850 0.775 1.000
        # 5 0.835 0.820 0.745 1.000 (kin > em)
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.805)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.775)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 1)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.543, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.553, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.523, places=3)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.675, places=3)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_ship_absent(self):
        # Setup
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.85)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_ship_not_loaded(self):
        # Setup
        self.fit.ship = Ship(self.allocate_type_id())
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.85)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_unexpected_exception(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        # Set cycle time to zero to force exception
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 0).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.85)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.425)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.5525)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.6375)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.765)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.name, 'eos.sim.reactive_armor_hardener')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            'unexpected exception, setting unsimulated resonances')
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)

    def test_unexpected_exception_with_modification(self):
        # Setup
        skill_attr = self.mkattr(high_is_good=False, stackable=False)
        skill_modifier = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=self.armor_em.id,
            operator=ModOperator.post_mul,
            src_attr_id=skill_attr.id)
        skill_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[skill_modifier])
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 0).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        skill = Skill(self.mktype(
            attrs={skill_attr.id: 0.5},
            effects=[skill_effect]).id)
        self.fit.skills.add(skill)
        # Verification
        # Skill should change RAH unsimulated EM resonance, and ship EM
        # resonance via RAH effect
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.425)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.85)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.2125)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.5525)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.6375)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.765)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(log_record.name, 'eos.sim.reactive_armor_hardener')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(
            log_record.msg,
            'unexpected exception, setting unsimulated resonances')
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
