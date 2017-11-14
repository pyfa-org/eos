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


class TestStatsDmgDps(StatsTestCase):

    def setUp(self):
        StatsTestCase.setUp(self)
        self.ch.attr(attr_id=AttrId.em_dmg)
        self.ch.attr(attr_id=AttrId.thermal_dmg)
        self.ch.attr(attr_id=AttrId.kinetic_dmg)
        self.ch.attr(attr_id=AttrId.explosive_dmg)
        self.ch.attr(attr_id=AttrId.dmg_multiplier)
        self.ch.attr(
            attr_id=AttrId.module_reactivation_delay, default_value=0)
        self.ch.attr(attr_id=AttrId.volume)
        self.ch.attr(attr_id=AttrId.capacity)
        self.ch.attr(attr_id=AttrId.reload_time)
        self.ch.attr(attr_id=AttrId.charge_rate)
        self.cycle_attr = self.ch.attr()
        self.dd_effect = self.ch.effect(
            effect_id=EffectId.projectile_fired,
            category_id=EffectCategoryId.active,
            duration_attr_id=self.cycle_attr.id)

    def test_empty(self):
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertIsNone(stats_dps.thermal)
        self.assertIsNone(stats_dps.kinetic)
        self.assertIsNone(stats_dps.explosive)
        self.assertIsNone(stats_dps.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single(self):
        src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=AttrId.dmg_multiplier,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        effect = self.ch.effect(
            category_id=EffectCategoryId.passive, modifiers=[modifier])
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000, src_attr.id: 1.5},
                effects=(self.dd_effect, effect),
                default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attrs={
            AttrId.em_dmg: 1.2, AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8, AttrId.explosive_dmg: 9.6,
            AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 1.44)
        self.assertAlmostEqual(stats_dps.thermal, 2.88)
        self.assertAlmostEqual(stats_dps.kinetic, 5.76)
        self.assertAlmostEqual(stats_dps.explosive, 11.52)
        self.assertAlmostEqual(stats_dps.total, 21.6)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_multiple(self):
        item1 = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item1.charge = Charge(self.ch.type(attrs={
            AttrId.em_dmg: 1.2, AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8, AttrId.explosive_dmg: 9.6,
            AttrId.volume: 1}).id)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2000,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item2.charge = Charge(self.ch.type(attrs={
            AttrId.em_dmg: 12, AttrId.thermal_dmg: 24,
            AttrId.kinetic_dmg: 48, AttrId.explosive_dmg: 96,
            AttrId.volume: 1}).id)
        self.fit.modules.high.append(item2)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 12.96)
        self.assertAlmostEqual(stats_dps.thermal, 25.92)
        self.assertAlmostEqual(stats_dps.kinetic, 51.84)
        self.assertAlmostEqual(stats_dps.explosive, 103.68)
        self.assertAlmostEqual(stats_dps.total, 194.4)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_arguments_custom_profile(self):
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attrs={
            AttrId.em_dmg: 1.2, AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8, AttrId.explosive_dmg: 9.6,
            AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps(
            tgt_resists=ResistProfile(0, 1, 1, 1))
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertAlmostEqual(stats_dps.thermal, 0)
        self.assertAlmostEqual(stats_dps.kinetic, 0)
        self.assertAlmostEqual(stats_dps.explosive, 0)
        self.assertAlmostEqual(stats_dps.total, 0.96)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_arguments_custom_reload(self):
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 3000,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attrs={
            AttrId.em_dmg: 1.2, AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8, AttrId.explosive_dmg: 9.6,
            AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps(reload=True)
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.48)
        self.assertAlmostEqual(stats_dps.thermal, 0.96)
        self.assertAlmostEqual(stats_dps.kinetic, 1.92)
        self.assertAlmostEqual(stats_dps.explosive, 3.84)
        self.assertAlmostEqual(stats_dps.total, 7.2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_arguments_custom_filter(self):
        item1 = ModuleHigh(
            self.ch.type(
                group_id=55, attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect],
                default_effect=self.dd_effect).id,
            state=State.active)
        item1.charge = Charge(self.ch.type(attrs={
            AttrId.em_dmg: 1.2, AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8, AttrId.explosive_dmg: 9.6,
            AttrId.volume: 1}).id)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(
            self.ch.type(
                group_id=54, attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2000,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item2.charge = Charge(self.ch.type(attrs={
            AttrId.em_dmg: 12, AttrId.thermal_dmg: 24,
            AttrId.kinetic_dmg: 48, AttrId.explosive_dmg: 96,
            AttrId.volume: 1}).id)
        self.fit.modules.high.append(item2)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps(
            item_filter=lambda i: i._type.group_id == 55)
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertAlmostEqual(stats_dps.thermal, 1.92)
        self.assertAlmostEqual(stats_dps.kinetic, 3.84)
        self.assertAlmostEqual(stats_dps.explosive, 7.68)
        self.assertAlmostEqual(stats_dps.total, 14.4)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_none_em(self):
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attrs={
            AttrId.thermal_dmg: 2.4, AttrId.kinetic_dmg: 4.8,
            AttrId.explosive_dmg: 9.6, AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertAlmostEqual(stats_dps.thermal, 1.92)
        self.assertAlmostEqual(stats_dps.kinetic, 3.84)
        self.assertAlmostEqual(stats_dps.explosive, 7.68)
        self.assertAlmostEqual(stats_dps.total, 13.44)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_none_therm(self):
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attrs={
            AttrId.em_dmg: 1.2, AttrId.kinetic_dmg: 4.8,
            AttrId.explosive_dmg: 9.6, AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertIsNone(stats_dps.thermal)
        self.assertAlmostEqual(stats_dps.kinetic, 3.84)
        self.assertAlmostEqual(stats_dps.explosive, 7.68)
        self.assertAlmostEqual(stats_dps.total, 12.48)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_none_kin(self):
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attrs={
            AttrId.em_dmg: 1.2, AttrId.thermal_dmg: 2.4,
            AttrId.explosive_dmg: 9.6, AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertAlmostEqual(stats_dps.thermal, 1.92)
        self.assertIsNone(stats_dps.kinetic)
        self.assertAlmostEqual(stats_dps.explosive, 7.68)
        self.assertAlmostEqual(stats_dps.total, 10.56)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_none_expl(self):
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attrs={
            AttrId.em_dmg: 1.2, AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8, AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertAlmostEqual(stats_dps.thermal, 1.92)
        self.assertAlmostEqual(stats_dps.kinetic, 3.84)
        self.assertIsNone(stats_dps.explosive)
        self.assertAlmostEqual(stats_dps.total, 6.72)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_none_all(self):
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(
            attrs={AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertIsNone(stats_dps.thermal)
        self.assertIsNone(stats_dps.kinetic)
        self.assertIsNone(stats_dps.explosive)
        self.assertIsNone(stats_dps.total)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_zero_em(self):
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(
            attrs={AttrId.em_dmg: 0, AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0)
        self.assertIsNone(stats_dps.thermal)
        self.assertIsNone(stats_dps.kinetic)
        self.assertIsNone(stats_dps.explosive)
        self.assertAlmostEqual(stats_dps.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_zero_therm(self):
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attrs={
            AttrId.thermal_dmg: 0, AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertAlmostEqual(stats_dps.thermal, 0)
        self.assertIsNone(stats_dps.kinetic)
        self.assertIsNone(stats_dps.explosive)
        self.assertAlmostEqual(stats_dps.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_zero_kin(self):
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attrs={
            AttrId.kinetic_dmg: 0, AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertIsNone(stats_dps.thermal)
        self.assertAlmostEqual(stats_dps.kinetic, 0)
        self.assertIsNone(stats_dps.explosive)
        self.assertAlmostEqual(stats_dps.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_single_zero_expl(self):
        item = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attrs={
            AttrId.explosive_dmg: 0, AttrId.volume: 1}).id)
        self.fit.modules.high.append(item)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertIsNone(stats_dps.thermal)
        self.assertIsNone(stats_dps.kinetic)
        self.assertAlmostEqual(stats_dps.explosive, 0)
        self.assertAlmostEqual(stats_dps.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_none_and_data(self):
        # As container for damage dealers is not ordered, this test may be
        # unreliable (even if there's issue, it won't fail each run)
        item1 = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2500,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item1.charge = Charge(self.ch.type(attrs={
            AttrId.em_dmg: 1.2, AttrId.thermal_dmg: 2.4,
            AttrId.kinetic_dmg: 4.8, AttrId.explosive_dmg: 9.6,
            AttrId.volume: 1}).id)
        self.fit.modules.high.append(item1)
        item2 = ModuleHigh(
            self.ch.type(
                attrs={
                    AttrId.dmg_multiplier: 2, AttrId.capacity: 1,
                    AttrId.charge_rate: 1, self.cycle_attr.id: 2000,
                    AttrId.reload_time: 2000},
                effects=[self.dd_effect], default_effect=self.dd_effect).id,
            state=State.active)
        item2.charge = Charge(self.ch.type(
            attrs={AttrId.volume: 1}).id)
        self.fit.modules.high.append(item2)
        # Action
        stats_dps = self.fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertAlmostEqual(stats_dps.thermal, 1.92)
        self.assertAlmostEqual(stats_dps.kinetic, 3.84)
        self.assertAlmostEqual(stats_dps.explosive, 7.68)
        self.assertAlmostEqual(stats_dps.total, 14.4)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
