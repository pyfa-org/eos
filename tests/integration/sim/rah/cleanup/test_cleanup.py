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
from eos.const.eos import State
from tests.integration.sim.rah.rah_testcase import RahSimTestCase


class TestRahSimCleanup(RahSimTestCase):

    def test_rah_added(self):
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
        # Force ship resist calculation
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.9)
        # Action
        fit.modules.low.equip(rah_item)
        # Verify
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.5895)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_rah_removed(self):
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
        # Force ship resist calculation
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.5895)
        # Action
        fit.modules.low.remove(rah_item)
        # Verify
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.9)
        # Cleanup
        fit.ship = None
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_rah_state_switch_up(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.5, 0.65, 0.75, 0.9))
        self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.online)
        fit.modules.low.equip(rah_item)
        # Force ship resist calculation
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.9)
        # Action
        rah_item.state = State.active
        # Verify
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.5895)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_rah_state_switch_down(self):
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
        # Force ship resist calculation
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.5895)
        # Action
        rah_item.state = State.online
        # Verify
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.9)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_damage_profile_default(self):
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
        # Force ship resist calculation
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.60125)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.615)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.5895)
        # Action
        fit.default_incoming_damage = DamageProfile(em=1, thermal=0, kinetic=0, explosive=0)
        # Verify
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.2)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.9)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
