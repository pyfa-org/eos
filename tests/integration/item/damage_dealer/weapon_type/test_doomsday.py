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


from eos import EffectMode
from eos import Fit
from eos import ModuleHigh
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemDmgDoomsday(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.em_dmg)
        self.mkattr(attr_id=AttrId.thermal_dmg)
        self.mkattr(attr_id=AttrId.kinetic_dmg)
        self.mkattr(attr_id=AttrId.explosive_dmg)
        self.cycle_attr = self.mkattr()
        self.effect = self.mkeffect(
            effect_id=EffectId.super_weapon_amarr,
            category_id=EffectCategoryId.target,
            duration_attr_id=self.cycle_attr.id)

    def test_nominal_volley_generic(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.em_dmg: 52000,
                    AttrId.thermal_dmg: 63000,
                    AttrId.kinetic_dmg: 74000,
                    AttrId.explosive_dmg: 85000,
                    self.cycle_attr.id: 250000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 52000)
        self.assertAlmostEqual(volley.thermal, 63000)
        self.assertAlmostEqual(volley.kinetic, 74000)
        self.assertAlmostEqual(volley.explosive, 85000)
        self.assertAlmostEqual(volley.total, 274000)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_nominal_volley_multiplier(self):
        self.mkattr(attr_id=AttrId.dmg_multiplier)
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.em_dmg: 52000,
                    AttrId.thermal_dmg: 63000,
                    AttrId.kinetic_dmg: 74000,
                    AttrId.explosive_dmg: 85000,
                    self.cycle_attr.id: 250000,
                    AttrId.dmg_multiplier: 5.5},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 52000)
        self.assertAlmostEqual(volley.thermal, 63000)
        self.assertAlmostEqual(volley.kinetic, 74000)
        self.assertAlmostEqual(volley.explosive, 85000)
        self.assertAlmostEqual(volley.total, 274000)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_nominal_volley_insufficient_state(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.em_dmg: 52000,
                    AttrId.thermal_dmg: 63000,
                    AttrId.kinetic_dmg: 74000,
                    AttrId.explosive_dmg: 85000,
                    self.cycle_attr.id: 250000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.online)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_nominal_volley_disabled_effect(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.em_dmg: 52000,
                    AttrId.thermal_dmg: 63000,
                    AttrId.kinetic_dmg: 74000,
                    AttrId.explosive_dmg: 85000,
                    self.cycle_attr.id: 250000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.set_effect_mode(self.effect.id, EffectMode.force_stop)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_nominal_dps_no_reload(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.em_dmg: 52000,
                    AttrId.thermal_dmg: 63000,
                    AttrId.kinetic_dmg: 74000,
                    AttrId.explosive_dmg: 85000,
                    self.cycle_attr.id: 250000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_nominal_dps(reload=False)
        self.assertAlmostEqual(dps.em, 208)
        self.assertAlmostEqual(dps.thermal, 252)
        self.assertAlmostEqual(dps.kinetic, 296)
        self.assertAlmostEqual(dps.explosive, 340)
        self.assertAlmostEqual(dps.total, 1096)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_nominal_dps_reload(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.em_dmg: 52000,
                    AttrId.thermal_dmg: 63000,
                    AttrId.kinetic_dmg: 74000,
                    AttrId.explosive_dmg: 85000,
                    self.cycle_attr.id: 250000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 208)
        self.assertAlmostEqual(dps.thermal, 252)
        self.assertAlmostEqual(dps.kinetic, 296)
        self.assertAlmostEqual(dps.explosive, 340)
        self.assertAlmostEqual(dps.total, 1096)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
