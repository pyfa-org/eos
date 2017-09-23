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
from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import Attribute, Effect, EffectCategory
from eos.data.cachable.modifier import DogmaModifier
from tests.integration.stats.stat_testcase import StatTestCase


class TestStatsDamageDps(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.em_damage)
        self.ch.attribute(attribute_id=Attribute.thermal_damage)
        self.ch.attribute(attribute_id=Attribute.kinetic_damage)
        self.ch.attribute(attribute_id=Attribute.explosive_damage)
        self.ch.attribute(attribute_id=Attribute.damage_multiplier)
        self.ch.attribute(attribute_id=Attribute.module_reactivation_delay, default_value=0)
        self.ch.attribute(attribute_id=Attribute.volume)
        self.ch.attribute(attribute_id=Attribute.capacity)
        self.ch.attribute(attribute_id=Attribute.reload_time)
        self.ch.attribute(attribute_id=Attribute.charge_rate)
        self.cycle_attr = self.ch.attribute()
        self.dd_effect = self.ch.effect(
            effect_id=Effect.projectile_fired, category=EffectCategory.active, duration_attribute=self.cycle_attr.id
        )

    def test_empty(self):
        fit = Fit()
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertIsNone(stats_dps.thermal)
        self.assertIsNone(stats_dps.kinetic)
        self.assertIsNone(stats_dps.explosive)
        self.assertIsNone(stats_dps.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_single(self):
        src_attr = self.ch.attribute()
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=Attribute.damage_multiplier,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier])
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000, src_attr.id: 1.5
        }, effects=(self.dd_effect, effect), default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.explosive_damage: 9.6,
            Attribute.volume: 1
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 1.44)
        self.assertAlmostEqual(stats_dps.thermal, 2.88)
        self.assertAlmostEqual(stats_dps.kinetic, 5.76)
        self.assertAlmostEqual(stats_dps.explosive, 11.52)
        self.assertAlmostEqual(stats_dps.total, 21.6)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_multiple(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item1.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.explosive_damage: 9.6,
            Attribute.volume: 1
        }).id)
        fit.modules.high.append(item1)
        item2 = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2000, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item2.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 12, Attribute.thermal_damage: 24,
            Attribute.kinetic_damage: 48, Attribute.explosive_damage: 96,
            Attribute.volume: 1
        }).id)
        fit.modules.high.append(item2)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 12.96)
        self.assertAlmostEqual(stats_dps.thermal, 25.92)
        self.assertAlmostEqual(stats_dps.kinetic, 51.84)
        self.assertAlmostEqual(stats_dps.explosive, 103.68)
        self.assertAlmostEqual(stats_dps.total, 194.4)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_arguments_custom_profile(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.explosive_damage: 9.6,
            Attribute.volume: 1
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps(target_resistances=ResistanceProfile(0, 1, 1, 1))
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertAlmostEqual(stats_dps.thermal, 0)
        self.assertAlmostEqual(stats_dps.kinetic, 0)
        self.assertAlmostEqual(stats_dps.explosive, 0)
        self.assertAlmostEqual(stats_dps.total, 0.96)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_arguments_custom_reload(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 3000, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.explosive_damage: 9.6,
            Attribute.volume: 1
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps(reload=True)
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.48)
        self.assertAlmostEqual(stats_dps.thermal, 0.96)
        self.assertAlmostEqual(stats_dps.kinetic, 1.92)
        self.assertAlmostEqual(stats_dps.explosive, 3.84)
        self.assertAlmostEqual(stats_dps.total, 7.2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_arguments_custom_filter(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type(group=55, attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item1.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.explosive_damage: 9.6,
            Attribute.volume: 1
        }).id)
        fit.modules.high.append(item1)
        item2 = ModuleHigh(self.ch.type(group=54, attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2000, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item2.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 12, Attribute.thermal_damage: 24,
            Attribute.kinetic_damage: 48, Attribute.explosive_damage: 96,
            Attribute.volume: 1
        }).id)
        fit.modules.high.append(item2)
        # Action
        stats_dps = fit.stats.get_nominal_dps(item_filter=lambda i: i._eve_type.group == 55)
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertAlmostEqual(stats_dps.thermal, 1.92)
        self.assertAlmostEqual(stats_dps.kinetic, 3.84)
        self.assertAlmostEqual(stats_dps.explosive, 7.68)
        self.assertAlmostEqual(stats_dps.total, 14.4)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_single_none_em(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.thermal_damage: 2.4, Attribute.kinetic_damage: 4.8,
            Attribute.explosive_damage: 9.6, Attribute.volume: 1
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertAlmostEqual(stats_dps.thermal, 1.92)
        self.assertAlmostEqual(stats_dps.kinetic, 3.84)
        self.assertAlmostEqual(stats_dps.explosive, 7.68)
        self.assertAlmostEqual(stats_dps.total, 13.44)
        # Cleanup
        # Failure to fetch damage value is not issue for this test
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_single_none_therm(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.kinetic_damage: 4.8,
            Attribute.explosive_damage: 9.6, Attribute.volume: 1
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertIsNone(stats_dps.thermal)
        self.assertAlmostEqual(stats_dps.kinetic, 3.84)
        self.assertAlmostEqual(stats_dps.explosive, 7.68)
        self.assertAlmostEqual(stats_dps.total, 12.48)
        # Cleanup
        # Failure to fetch damage value is not issue for this test
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_single_none_kin(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.explosive_damage: 9.6, Attribute.volume: 1
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertAlmostEqual(stats_dps.thermal, 1.92)
        self.assertIsNone(stats_dps.kinetic)
        self.assertAlmostEqual(stats_dps.explosive, 7.68)
        self.assertAlmostEqual(stats_dps.total, 10.56)
        # Cleanup
        # Failure to fetch damage value is not issue for this test
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_single_none_expl(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.volume: 1
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertAlmostEqual(stats_dps.thermal, 1.92)
        self.assertAlmostEqual(stats_dps.kinetic, 3.84)
        self.assertIsNone(stats_dps.explosive)
        self.assertAlmostEqual(stats_dps.total, 6.72)
        # Cleanup
        # Failure to fetch damage value is not issue for this test
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_single_none_all(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={Attribute.volume: 1}).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertIsNone(stats_dps.thermal)
        self.assertIsNone(stats_dps.kinetic)
        self.assertIsNone(stats_dps.explosive)
        self.assertIsNone(stats_dps.total)
        # Cleanup
        # Failure to fetch damage values is not issue for this test
        self.assertEqual(len(self.log), 4)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_em(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 0, Attribute.volume: 1
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0)
        self.assertIsNone(stats_dps.thermal)
        self.assertIsNone(stats_dps.kinetic)
        self.assertIsNone(stats_dps.explosive)
        self.assertAlmostEqual(stats_dps.total, 0)
        # Cleanup
        # Failure to fetch damage values is not issue for this test
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_therm(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.thermal_damage: 0, Attribute.volume: 1
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertAlmostEqual(stats_dps.thermal, 0)
        self.assertIsNone(stats_dps.kinetic)
        self.assertIsNone(stats_dps.explosive)
        self.assertAlmostEqual(stats_dps.total, 0)
        # Cleanup
        # Failure to fetch damage values is not issue for this test
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_kin(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.kinetic_damage: 0, Attribute.volume: 1
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertIsNone(stats_dps.thermal)
        self.assertAlmostEqual(stats_dps.kinetic, 0)
        self.assertIsNone(stats_dps.explosive)
        self.assertAlmostEqual(stats_dps.total, 0)
        # Cleanup
        # Failure to fetch damage values is not issue for this test
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_expl(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.explosive_damage: 0, Attribute.volume: 1
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertIsNone(stats_dps.em)
        self.assertIsNone(stats_dps.thermal)
        self.assertIsNone(stats_dps.kinetic)
        self.assertAlmostEqual(stats_dps.explosive, 0)
        self.assertAlmostEqual(stats_dps.total, 0)
        # Cleanup
        # Failure to fetch damage values is not issue for this test
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_none_and_data(self):
        # As container for damage dealers is not ordered,
        # this test may be unreliable (even if there's issue,
        # it won't fail each run)
        fit = Fit()
        item1 = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2500, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item1.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.explosive_damage: 9.6,
            Attribute.volume: 1
        }).id)
        fit.modules.high.append(item1)
        item2 = ModuleHigh(self.ch.type(attributes={
            Attribute.damage_multiplier: 2, Attribute.capacity: 1, Attribute.charge_rate: 1,
            self.cycle_attr.id: 2000, Attribute.reload_time: 2000
        }, effects=[self.dd_effect], default_effect=self.dd_effect).id, state=State.active)
        item2.charge = Charge(self.ch.type(attributes={Attribute.volume: 1}).id)
        fit.modules.high.append(item2)
        # Action
        stats_dps = fit.stats.get_nominal_dps()
        # Verification
        self.assertAlmostEqual(stats_dps.em, 0.96)
        self.assertAlmostEqual(stats_dps.thermal, 1.92)
        self.assertAlmostEqual(stats_dps.kinetic, 3.84)
        self.assertAlmostEqual(stats_dps.explosive, 7.68)
        self.assertAlmostEqual(stats_dps.total, 14.4)
        # Cleanup
        self.assertEqual(len(self.log), 4)
        self.assert_fit_buffers_empty(fit)
