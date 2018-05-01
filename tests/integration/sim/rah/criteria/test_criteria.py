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


from eos import EffectMode
from eos import ModuleLow
from eos import Ship
from eos import State
from eos.const.eve import EffectId
from tests.integration.sim.rah.testcase import RahSimTestCase


class TestRahSimCriteria(RahSimTestCase):

    def test_active_added(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        # Action
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
        self.assert_log_entries(0)

    def test_active_switched(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.online)
        self.fit.modules.low.equip(rah)
        # Action
        rah.state = State.active
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
        self.assert_log_entries(0)

    def test_inactive_added(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.online)
        # Action
        self.fit.modules.low.equip(rah)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.85)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.9)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_inactive_switched(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        self.fit.modules.low.equip(rah)
        # Action
        rah.state = State.online
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.85)
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.9)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)

    def test_not_rah(self):
        # Setup
        ship = Ship(self.make_ship_type((0.5, 0.65, 0.75, 0.9)).id)
        self.fit.ship = ship
        rah = ModuleLow(
            self.make_rah_type((0.85, 0.85, 0.85, 0.85), 6, 1000).id,
            state=State.active)
        # RAH is detected using effect, thus if item doesn't have RAH effect,
        # it's not RAH
        rah.set_effect_mode(
            EffectId.adaptive_armor_hardener, EffectMode.force_stop)
        # Action
        self.fit.modules.low.equip(rah)
        # Verification
        self.assertAlmostEqual(rah.attrs[self.armor_em.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_therm.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_kin.id], 0.85)
        self.assertAlmostEqual(rah.attrs[self.armor_expl.id], 0.85)
        # Effect is not seen - modifiers do not work too
        self.assertAlmostEqual(ship.attrs[self.armor_em.id], 0.5)
        self.assertAlmostEqual(ship.attrs[self.armor_therm.id], 0.65)
        self.assertAlmostEqual(ship.attrs[self.armor_kin.id], 0.75)
        self.assertAlmostEqual(ship.attrs[self.armor_expl.id], 0.9)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)
