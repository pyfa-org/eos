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


import logging
from unittest.mock import patch

from eos import *
from eos.const.eos import State
from tests.integration.sim.rah.rah_testcase import RahSimTestCase


class TestRahSimResult(RahSimTestCase):

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=7)
    def test_single_run(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.5, 0.65, 0.75, 0.9))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 1)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.925)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.655)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.5895)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=8)
    def test_double_run(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.5, 0.65, 0.75, 0.9))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item1 = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item1)
        rah_item2 = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item2)
        # Verify
        self.assertAlmostEqual(rah_item1.attributes[self.armor_em.id], 0.97)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_therm.id], 0.88)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_kin.id], 0.805)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_exp.id], 0.745)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_em.id], 0.97)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_therm.id], 0.88)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_kin.id], 0.805)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_exp.id], 0.745)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.472, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.512, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.501, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.522, places=3)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=82)
    def test_double_run_unsynced(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.5, 0.65, 0.75, 0.9))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item1 = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item1)
        rah_item2 = ModuleLow(rah_type_id, state=State.overload)
        fit.modules.low.equip(rah_item2)
        # Verify
        self.assertAlmostEqual(rah_item1.attributes[self.armor_em.id], 0.975, places=3)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_therm.id], 0.835, places=3)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_kin.id], 0.83, places=3)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_exp.id], 0.76, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_em.id], 0.979, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_therm.id], 0.91, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_kin.id], 0.796, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_exp.id], 0.715, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.479, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.5, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.509, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.509, places=3)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=75)
    def test_no_loop_ignore_initial_adaptation(self):
        # Same as double unsynced, but with amount of ticks insufficient
        # to detect loop
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.5, 0.65, 0.75, 0.9))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item1 = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item1)
        rah_item2 = ModuleLow(rah_type_id, state=State.overload)
        fit.modules.low.equip(rah_item2)
        # Verify
        # We ignored 10 first ticks, which corresponds to 5 cycles of non-heated RAH
        # ceil(ceil(15 / 6) * 1.5). 10 ticks instead of 5 because heated RAH is also
        # cycling, and we stop taking ticks only when slowest (unheated) RAH just
        # finished 5th cycle
        self.assertAlmostEqual(rah_item1.attributes[self.armor_em.id], 0.971, places=3)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_therm.id], 0.834, places=3)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_kin.id], 0.834, places=3)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_exp.id], 0.761, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_em.id], 0.987, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_therm.id], 0.912, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_kin.id], 0.789, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_exp.id], 0.712, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.48, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.501, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.506, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.508, places=3)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=5)
    def test_no_loop_half_history(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.5, 0.65, 0.75, 0.9))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item1 = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item1)
        rah_item2 = ModuleLow(rah_type_id, state=State.overload)
        fit.modules.low.equip(rah_item2)
        # Verify
        # Same as previous test, but here whole history is just 5 ticks, and we cannot
        # ignore all of them - here we should ignore just 2 first ticks
        self.assertAlmostEqual(rah_item1.attributes[self.armor_em.id], 0.94, places=3)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_therm.id], 0.88, places=3)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_kin.id], 0.82, places=3)
        self.assertAlmostEqual(rah_item1.attributes[self.armor_exp.id], 0.76, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_em.id], 0.97, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_therm.id], 0.85, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_kin.id], 0.85, places=3)
        self.assertAlmostEqual(rah_item2.attributes[self.armor_exp.id], 0.73, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.458, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.495, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.535, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.52, places=3)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=3)
    def test_order_multi(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.675, 0.675, 0.675, 0.675))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        # From real tests, gecko vs gnosis
        # ---loop---
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.790 0.910 (kin therm > em explo)
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.88)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.88)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.594, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.554, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.554, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.594, places=3)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=7)
    def test_order_therm_kin_exp(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.675, 0.675, 0.675, 0.675))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        fit.default_incoming_damage = DamageProfile(0, 1, 1, 1)
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        # From real tests, gecko vs gnosis with 2 EM hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.790 0.910 (kin therm > explo)
        # 2 0.970 0.730 0.850 0.850 (therm > kin)
        # ---loop---
        # 3 1.000 0.790 0.805 0.805
        # 4 1.000 0.850 0.775 0.775
        # 5 1.000 0.820 0.745 0.835 (kin > explo)
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 1)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.775)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.805)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.675, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.553, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.523, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.543, places=3)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=7)
    def test_order_em_kin_exp(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.675, 0.675, 0.675, 0.675))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        fit.default_incoming_damage = DamageProfile(1, 0, 1, 1)
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        # From real tests, gecko vs gnosis with 2 thermal hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.910 0.790 0.790 (kin explo > em)
        # 2 0.850 0.970 0.730 0.850 (kin > explo)
        # ---loop---
        # 3 0.805 1.000 0.790 0.805
        # 4 0.775 1.000 0.850 0.775
        # 5 0.835 1.000 0.820 0.745 (explo > em)
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.805)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 1)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.775)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.543, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.675, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.553, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.523, places=3)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=7)
    def test_order_em_therm_exp(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.675, 0.675, 0.675, 0.675))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        fit.default_incoming_damage = DamageProfile(1, 1, 0, 1)
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        # From real tests, gecko vs gnosis with 2 kinetic hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.910 0.790 (explo therm > em)
        # 2 0.850 0.730 0.970 0.850 (therm > explo)
        # ---loop---
        # 3 0.805 0.790 1.000 0.805
        # 4 0.775 0.850 1.000 0.775
        # 5 0.835 0.820 1.000 0.745 (explo > em)
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.805)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 1)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.775)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.543, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.553, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.675, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.523, places=3)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    @patch('eos.fit.sim.reactive_armor_hardener.MAX_SIMULATION_TICKS', new=7)
    def test_order_em_therm_kin(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.675, 0.675, 0.675, 0.675))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        fit.default_incoming_damage = DamageProfile(1, 1, 1, 0)
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        # From real tests, gecko vs gnosis with 2 explosive hardeners
        # 0 0.850 0.850 0.850 0.850
        # 1 0.910 0.790 0.790 0.910 (kin therm > em)
        # 2 0.850 0.730 0.850 0.970 (therm > kin)
        # ---loop---
        # 3 0.805 0.790 0.805 1.000
        # 4 0.775 0.850 0.775 1.000
        # 5 0.835 0.820 0.745 1.000 (kin > em)
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.805)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.82)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.775)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 1)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.543, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.553, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.523, places=3)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.675, places=3)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_no_ship(self):
        # Setup
        rah_type_id = 1
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.85)
        # Cleanup
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_unexpected_exception(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.5, 0.65, 0.75, 0.9))
        # Set cycle time to zero to force exception
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 0)
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        fit.modules.low.equip(rah_item)
        # Verify
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.85)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.425)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.5525)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.6375)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.765)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.fit.sim.reactive_armor_hardener')
        self.assertEqual(log_record.levelno, logging.WARNING)
        self.assertEqual(log_record.msg, 'unexpected exception, setting unsimulated resonances')
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)
