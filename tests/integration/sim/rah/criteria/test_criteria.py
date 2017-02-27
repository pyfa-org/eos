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


class TestRahSimCriteria(RahSimTestCase):

    def test_active_added(self):
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
        # Action
        fit.modules.low.equip(rah_item)
        # Verification
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

    def test_active_switched(self):
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
        # Action
        rah_item.state = State.active
        # Verification
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

    def test_inactive_added(self):
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
        # Action
        fit.modules.low.equip(rah_item)
        # Verification
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.85)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.9)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_inactive_switched(self):
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
        # Action
        rah_item.state = State.online
        # Verification
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.85)
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.9)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_not_rah(self):
        # Setup
        ship_type_id = 1
        rah_type_id = 2
        self.make_ship_type(ship_type_id, (0.5, 0.65, 0.75, 0.9))
        rah_type = self.make_rah_type(rah_type_id, (0.85, 0.85, 0.85, 0.85), 6, 1000)
        # RAH is detected using default effect, thus if item doesn't have
        # RAH effect as default, it's not RAH
        rah_type.default_effect = None
        # Compose fit
        fit = Fit()
        ship_item = Ship(ship_type_id)
        fit.ship = ship_item
        rah_item = ModuleLow(rah_type_id, state=State.active)
        # Action
        fit.modules.low.equip(rah_item)
        # Verification
        self.assertAlmostEqual(rah_item.attributes[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah_item.attributes[self.armor_exp.id], 0.85)
        # Unsimulated resonance multipliers are still applied
        self.assertAlmostEqual(ship_item.attributes[self.armor_em.id], 0.425)
        self.assertAlmostEqual(ship_item.attributes[self.armor_therm.id], 0.5525)
        self.assertAlmostEqual(ship_item.attributes[self.armor_kin.id], 0.6375)
        self.assertAlmostEqual(ship_item.attributes[self.armor_exp.id], 0.765)
        # Cleanup
        fit.ship = None
        fit.modules.low.clear()
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
