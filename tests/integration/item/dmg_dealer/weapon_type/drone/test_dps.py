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


from eos import Drone
from eos import Fit
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemDmgDroneDps(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.dmg_mult)
        self.mkattr(attr_id=AttrId.em_dmg)
        self.mkattr(attr_id=AttrId.therm_dmg)
        self.mkattr(attr_id=AttrId.kin_dmg)
        self.mkattr(attr_id=AttrId.expl_dmg)
        self.cycle_attr = self.mkattr()
        self.effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.target,
            duration_attr_id=self.cycle_attr.id)

    def test_no_reload(self):
        fit = Fit()
        item = Drone(
            self.mktype(
                attrs={
                    AttrId.dmg_mult: 2.5,
                    AttrId.em_dmg: 52,
                    AttrId.therm_dmg: 63,
                    AttrId.kin_dmg: 74,
                    AttrId.expl_dmg: 85,
                    self.cycle_attr.id: 4000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        fit.drones.add(item)
        # Verification
        dps = item.get_dps(reload=False)
        self.assertAlmostEqual(dps.em, 32.5)
        self.assertAlmostEqual(dps.thermal, 39.375)
        self.assertAlmostEqual(dps.kinetic, 46.25)
        self.assertAlmostEqual(dps.explosive, 53.125)
        self.assertAlmostEqual(dps.total, 171.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_reload(self):
        fit = Fit()
        item = Drone(
            self.mktype(
                attrs={
                    AttrId.dmg_mult: 2.5,
                    AttrId.em_dmg: 52,
                    AttrId.therm_dmg: 63,
                    AttrId.kin_dmg: 74,
                    AttrId.expl_dmg: 85,
                    self.cycle_attr.id: 4000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        fit.drones.add(item)
        # Verification
        dps = item.get_dps(reload=True)
        self.assertAlmostEqual(dps.em, 32.5)
        self.assertAlmostEqual(dps.thermal, 39.375)
        self.assertAlmostEqual(dps.kinetic, 46.25)
        self.assertAlmostEqual(dps.explosive, 53.125)
        self.assertAlmostEqual(dps.total, 171.25)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)
