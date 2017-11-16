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
from eos.const.eos import ModDomain, ModOperator, ModTgtFilter
from eos.const.eve import AttrId, EffectId, EffectCategoryId
from tests.integration.stats.stats_testcase import StatsTestCase


class TestStatsDmgVolley(StatsTestCase):

    def setUp(self):
        StatsTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.em_dmg)
        self.mkattr(attr_id=AttrId.thermal_dmg)
        self.mkattr(attr_id=AttrId.kinetic_dmg)
        self.mkattr(attr_id=AttrId.explosive_dmg)
        self.mkattr(attr_id=AttrId.dmg_multiplier)
        self.dd_effect = self.mkeffect(
            effect_id=EffectId.projectile_fired,
            category_id=EffectCategoryId.active)

    def test_empty(self):
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertIsNone(stats_volley.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single(self):
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=AttrId.dmg_multiplier,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2, src_attr.id: 1.5},
                effects=(self.dd_effect, effect),
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.em_dmg: 1.2,
            AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8,
            AttrId.explosive_dmg: 9.6}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 3.6)
        self.assertAlmostEqual(stats_volley.thermal, 7.2)
        self.assertAlmostEqual(stats_volley.kinetic, 14.4)
        self.assertAlmostEqual(stats_volley.explosive, 28.8)
        self.assertAlmostEqual(stats_volley.total, 54)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_multiple(self):
        item1 = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item1.charge = Charge(self.mktype(attrs={
            AttrId.em_dmg: 1.2,
            AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8,
            AttrId.explosive_dmg: 9.6}).id)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item2.charge = Charge(self.mktype(attrs={
            AttrId.em_dmg: 12,
            AttrId.thermal_dmg: 24,
            AttrId.kinetic_dmg: 48,
            AttrId.explosive_dmg: 96}).id)
        self.fit.modules.high.append(item2)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 26.4)
        self.assertAlmostEqual(stats_volley.thermal, 52.8)
        self.assertAlmostEqual(stats_volley.kinetic, 105.6)
        self.assertAlmostEqual(stats_volley.explosive, 211.2)
        self.assertAlmostEqual(stats_volley.total, 396)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_arguments_custom_profile(self):
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.em_dmg: 1.2,
            AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8,
            AttrId.explosive_dmg: 9.6}).id)
        self.fit.modules.high.append(item)
        # Action
        resists = ResistProfile(0, 1, 1, 1)
        stats_volley = self.fit.stats.get_nominal_volley(tgt_resists=resists)
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertAlmostEqual(stats_volley.thermal, 0)
        self.assertAlmostEqual(stats_volley.kinetic, 0)
        self.assertAlmostEqual(stats_volley.explosive, 0)
        self.assertAlmostEqual(stats_volley.total, 2.4)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_arguments_custom_filter(self):
        item1 = ModuleHigh(
            self.mktype(
                group_id=55,
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item1.charge = Charge(self.mktype(attrs={
            AttrId.em_dmg: 1.2,
            AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8,
            AttrId.explosive_dmg: 9.6}).id)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(
            self.mktype(
                group_id=54,
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item2.charge = Charge(self.mktype(attrs={
            AttrId.em_dmg: 12,
            AttrId.thermal_dmg: 24,
            AttrId.kinetic_dmg: 48,
            AttrId.explosive_dmg: 96}).id)
        self.fit.modules.high.append(item2)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley(
            item_filter=lambda i: i._type.group_id == 55)
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertAlmostEqual(stats_volley.thermal, 4.8)
        self.assertAlmostEqual(stats_volley.kinetic, 9.6)
        self.assertAlmostEqual(stats_volley.explosive, 19.2)
        self.assertAlmostEqual(stats_volley.total, 36)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_none_em(self):
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8,
            AttrId.explosive_dmg: 9.6}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertAlmostEqual(stats_volley.thermal, 4.8)
        self.assertAlmostEqual(stats_volley.kinetic, 9.6)
        self.assertAlmostEqual(stats_volley.explosive, 19.2)
        self.assertAlmostEqual(stats_volley.total, 33.6)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_none_therm(self):
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.em_dmg: 1.2,
            AttrId.kinetic_dmg: 4.8,
            AttrId.explosive_dmg: 9.6}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertIsNone(stats_volley.thermal)
        self.assertAlmostEqual(stats_volley.kinetic, 9.6)
        self.assertAlmostEqual(stats_volley.explosive, 19.2)
        self.assertAlmostEqual(stats_volley.total, 31.2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_none_kin(self):
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.em_dmg: 1.2,
            AttrId.thermal_dmg: 2.4,
            AttrId.explosive_dmg: 9.6}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertAlmostEqual(stats_volley.thermal, 4.8)
        self.assertIsNone(stats_volley.kinetic)
        self.assertAlmostEqual(stats_volley.explosive, 19.2)
        self.assertAlmostEqual(stats_volley.total, 26.4)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_none_expl(self):
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.em_dmg: 1.2,
            AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertAlmostEqual(stats_volley.thermal, 4.8)
        self.assertAlmostEqual(stats_volley.kinetic, 9.6)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 16.8)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_none_all(self):
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.mktype().id)
        self.fit.modules.high.append(item)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertIsNone(stats_volley.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_zero_em(self):
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={AttrId.em_dmg: 0}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 0)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_zero_therm(self):
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={AttrId.thermal_dmg: 0}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertAlmostEqual(stats_volley.thermal, 0)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_zero_kin(self):
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={AttrId.kinetic_dmg: 0}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertAlmostEqual(stats_volley.kinetic, 0)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_zero_expl(self):
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={AttrId.explosive_dmg: 0}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertAlmostEqual(stats_volley.explosive, 0)
        self.assertAlmostEqual(stats_volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_and_data(self):
        # As container for damage dealers is not ordered, this test may be
        # unreliable (even if there's issue, it won't fail each run)
        item1 = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item1.charge = Charge(self.mktype(attrs={
            AttrId.em_dmg: 1.2,
            AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8,
            AttrId.explosive_dmg: 9.6}).id)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(
            self.mktype(
                attrs={AttrId.dmg_multiplier: 2},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item2.charge = Charge(self.mktype().id)
        self.fit.modules.high.append(item2)
        # Action
        stats_volley = self.fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertAlmostEqual(stats_volley.thermal, 4.8)
        self.assertAlmostEqual(stats_volley.kinetic, 9.6)
        self.assertAlmostEqual(stats_volley.explosive, 19.2)
        self.assertAlmostEqual(stats_volley.total, 36)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
