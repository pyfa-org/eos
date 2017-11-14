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
from eos.const.eve import AttrId, EffectId, EffectCategoryId
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemDmgSmartbomb(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.ch.attr(attr_id=AttrId.em_dmg)
        self.ch.attr(attr_id=AttrId.thermal_dmg)
        self.ch.attr(attr_id=AttrId.kinetic_dmg)
        self.ch.attr(attr_id=AttrId.explosive_dmg)
        self.cycle_attr = self.ch.attr()
        self.effect = self.ch.effect(
            effect_id=EffectId.emp_wave, category_id=EffectCategoryId.active,
            duration_attr_id=self.cycle_attr.id)

    def test_nominal_volley_generic(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.em_dmg: 52,
                    AttrId.thermal_dmg: 63,
                    AttrId.kinetic_dmg: 74,
                    AttrId.explosive_dmg: 85,
                    self.cycle_attr.id: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 52)
        self.assertAlmostEqual(volley.thermal, 63)
        self.assertAlmostEqual(volley.kinetic, 74)
        self.assertAlmostEqual(volley.explosive, 85)
        self.assertAlmostEqual(volley.total, 274)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_nominal_volley_multiplier(self):
        self.ch.attr(attr_id=AttrId.dmg_multiplier)
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.em_dmg: 52,
                    AttrId.thermal_dmg: 63,
                    AttrId.kinetic_dmg: 74,
                    AttrId.explosive_dmg: 85,
                    self.cycle_attr.id: 5000,
                    AttrId.dmg_multiplier: 5.5},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 52)
        self.assertAlmostEqual(volley.thermal, 63)
        self.assertAlmostEqual(volley.kinetic, 74)
        self.assertAlmostEqual(volley.explosive, 85)
        self.assertAlmostEqual(volley.total, 274)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_nominal_volley_insufficient_state(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.em_dmg: 52,
                    AttrId.thermal_dmg: 63,
                    AttrId.kinetic_dmg: 74,
                    AttrId.explosive_dmg: 85,
                    self.cycle_attr.id: 5000},
                effects=[self.effect], default_effect=self.effect).id,
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
            self.ch.type(
                attrs={
                    AttrId.em_dmg: 52,
                    AttrId.thermal_dmg: 63,
                    AttrId.kinetic_dmg: 74,
                    AttrId.explosive_dmg: 85,
                    self.cycle_attr.id: 5000},
                effects=[self.effect], default_effect=self.effect).id,
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
            self.ch.type(
                attrs={
                    AttrId.em_dmg: 52,
                    AttrId.thermal_dmg: 63,
                    AttrId.kinetic_dmg: 74,
                    AttrId.explosive_dmg: 85,
                    self.cycle_attr.id: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_nominal_dps(reload=False)
        self.assertAlmostEqual(dps.em, 10.4)
        self.assertAlmostEqual(dps.thermal, 12.6)
        self.assertAlmostEqual(dps.kinetic, 14.8)
        self.assertAlmostEqual(dps.explosive, 17)
        self.assertAlmostEqual(dps.total, 54.8)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_nominal_dps_reload(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.em_dmg: 52,
                    AttrId.thermal_dmg: 63,
                    AttrId.kinetic_dmg: 74,
                    AttrId.explosive_dmg: 85,
                    self.cycle_attr.id: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 10.4)
        self.assertAlmostEqual(dps.thermal, 12.6)
        self.assertAlmostEqual(dps.kinetic, 14.8)
        self.assertAlmostEqual(dps.explosive, 17)
        self.assertAlmostEqual(dps.total, 54.8)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
