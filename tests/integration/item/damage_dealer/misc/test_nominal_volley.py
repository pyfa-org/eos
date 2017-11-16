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


class TestItemDmgMiscNominalVolley(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.capacity)
        self.mkattr(attr_id=AttrId.volume)
        self.mkattr(attr_id=AttrId.charge_rate)
        self.mkattr(attr_id=AttrId.reload_time)
        self.mkattr(attr_id=AttrId.dmg_multiplier)
        self.mkattr(attr_id=AttrId.em_dmg)
        self.mkattr(attr_id=AttrId.thermal_dmg)
        self.mkattr(attr_id=AttrId.kinetic_dmg)
        self.mkattr(attr_id=AttrId.explosive_dmg)
        self.cycle_attr = self.mkattr()
        self.effect = self.mkeffect(
            effect_id=EffectId.projectile_fired,
            category_id=EffectCategoryId.active,
            duration_attr_id=self.cycle_attr.id)

    def test_no_attr_single_em(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.thermal_dmg: 6.3,
            AttrId.kinetic_dmg: 7.4,
            AttrId.explosive_dmg: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 15.75)
        self.assertAlmostEqual(volley.kinetic, 18.5)
        self.assertAlmostEqual(volley.explosive, 21.25)
        self.assertAlmostEqual(volley.total, 55.5)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_attr_single_therm(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.em_dmg: 5.2,
            AttrId.kinetic_dmg: 7.4,
            AttrId.explosive_dmg: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 13)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 18.5)
        self.assertAlmostEqual(volley.explosive, 21.25)
        self.assertAlmostEqual(volley.total, 52.75)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_single_kin(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.em_dmg: 5.2,
            AttrId.thermal_dmg: 6.3,
            AttrId.explosive_dmg: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 13)
        self.assertAlmostEqual(volley.thermal, 15.75)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 21.25)
        self.assertAlmostEqual(volley.total, 50)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_single_expl(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.em_dmg: 5.2,
            AttrId.thermal_dmg: 6.3,
            AttrId.kinetic_dmg: 7.4}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 13)
        self.assertAlmostEqual(volley.thermal, 15.75)
        self.assertAlmostEqual(volley.kinetic, 18.5)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 47.25)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_all(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={AttrId.volume: 0.2}).id)
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

    def test_single_zero_attr_em(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={AttrId.volume: 0.2, AttrId.em_dmg: 0}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_zero_attr_therm(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={AttrId.volume: 0.2, AttrId.thermal_dmg: 0}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_zero_attr_kin(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={AttrId.volume: 0.2, AttrId.kinetic_dmg: 0}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_zero_attr_expl(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={AttrId.volume: 0.2, AttrId.explosive_dmg: 0}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effective(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.em_dmg: 5.2,
            AttrId.thermal_dmg: 6.3,
            AttrId.kinetic_dmg: 7.4,
            AttrId.explosive_dmg: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistProfile(0.2, 0.2, 0.8, 1)
        volley = item.get_nominal_volley(tgt_resists=profile)
        self.assertAlmostEqual(volley.em, 10.4)
        self.assertAlmostEqual(volley.thermal, 12.6)
        self.assertAlmostEqual(volley.kinetic, 3.7)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 26.7)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effective_no_attr_single_em(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.thermal_dmg: 6.3,
            AttrId.kinetic_dmg: 7.4,
            AttrId.explosive_dmg: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistProfile(0.2, 0.2, 0.8, 1)
        volley = item.get_nominal_volley(tgt_resists=profile)
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 12.6)
        self.assertAlmostEqual(volley.kinetic, 3.7)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 16.3)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effective_no_attr_single_therm(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.em_dmg: 5.2,
            AttrId.kinetic_dmg: 7.4,
            AttrId.explosive_dmg: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistProfile(0.2, 0.2, 0.8, 1)
        volley = item.get_nominal_volley(tgt_resists=profile)
        self.assertAlmostEqual(volley.em, 10.4)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 3.7)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 14.1)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effective_no_attr_single_kin(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.em_dmg: 5.2,
            AttrId.thermal_dmg: 6.3,
            AttrId.explosive_dmg: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistProfile(0.2, 0.2, 0.8, 1)
        volley = item.get_nominal_volley(tgt_resists=profile)
        self.assertAlmostEqual(volley.em, 10.4)
        self.assertAlmostEqual(volley.thermal, 12.6)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 23)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effective_no_attr_single_expl(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.em_dmg: 5.2,
            AttrId.thermal_dmg: 6.3,
            AttrId.kinetic_dmg: 7.4}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistProfile(0.2, 0.2, 0.8, 1)
        volley = item.get_nominal_volley(tgt_resists=profile)
        self.assertAlmostEqual(volley.em, 10.4)
        self.assertAlmostEqual(volley.thermal, 12.6)
        self.assertAlmostEqual(volley.kinetic, 3.7)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 26.7)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effective_no_attr_all(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={AttrId.volume: 0.2}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistProfile(0.2, 0.2, 0.8, 1)
        volley = item.get_nominal_volley(tgt_resists=profile)
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effective_single_zero_attr_em(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={AttrId.volume: 0.2, AttrId.em_dmg: 0}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistProfile(0.2, 0.2, 0.8, 1)
        volley = item.get_nominal_volley(tgt_resists=profile)
        self.assertAlmostEqual(volley.em, 0)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effective_single_zero_attr_therm(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={AttrId.volume: 0.2, AttrId.thermal_dmg: 0}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistProfile(0.2, 0.2, 0.8, 1)
        volley = item.get_nominal_volley(tgt_resists=profile)
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effective_single_zero_attr_kin(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={AttrId.volume: 0.2, AttrId.kinetic_dmg: 0}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistProfile(0.2, 0.2, 0.8, 1)
        volley = item.get_nominal_volley(tgt_resists=profile)
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_effective_single_zero_attr_expl(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={AttrId.volume: 0.2, AttrId.explosive_dmg: 0}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistProfile(0.2, 0.2, 0.8, 1)
        volley = item.get_nominal_volley(tgt_resists=profile)
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_charged_cycles(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 2.1,
            AttrId.em_dmg: 5.2,
            AttrId.thermal_dmg: 6.3,
            AttrId.kinetic_dmg: 7.4,
            AttrId.explosive_dmg: 8.5}).id)
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

    def test_no_source(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.dmg_multiplier: 2.5,
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 5000},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 0.2,
            AttrId.em_dmg: 5.2,
            AttrId.thermal_dmg: 6.3,
            AttrId.kinetic_dmg: 7.4,
            AttrId.explosive_dmg: 8.5}).id)
        fit.modules.high.append(item)
        fit.source = None
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
