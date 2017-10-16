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
from eos.const.eve import AttributeId, EffectId, EffectCategoryId
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemDamageMiscNominalVolley(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attr(attribute_id=AttributeId.capacity)
        self.ch.attr(attribute_id=AttributeId.volume)
        self.ch.attr(attribute_id=AttributeId.charge_rate)
        self.ch.attr(attribute_id=AttributeId.reload_time)
        self.ch.attr(attribute_id=AttributeId.damage_multiplier)
        self.ch.attr(attribute_id=AttributeId.em_damage)
        self.ch.attr(attribute_id=AttributeId.thermal_damage)
        self.ch.attr(attribute_id=AttributeId.kinetic_damage)
        self.ch.attr(attribute_id=AttributeId.explosive_damage)
        self.cycle_attr = self.ch.attr()
        self.effect = self.ch.effect(
            effect_id=EffectId.projectile_fired,
            category=EffectCategoryId.active,
            duration_attribute=self.cycle_attr.id)

    def test_no_attrib_single_em(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.thermal_damage: 6.3,
            AttributeId.kinetic_damage: 7.4,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 15.75)
        self.assertAlmostEqual(volley.kinetic, 18.5)
        self.assertAlmostEqual(volley.explosive, 21.25)
        self.assertAlmostEqual(volley.total, 55.5)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_attrib_single_therm(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.em_damage: 5.2,
            AttributeId.kinetic_damage: 7.4,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 13)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 18.5)
        self.assertAlmostEqual(volley.explosive, 21.25)
        self.assertAlmostEqual(volley.total, 52.75)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_no_attrib_single_kin(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.em_damage: 5.2,
            AttributeId.thermal_damage: 6.3,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 13)
        self.assertAlmostEqual(volley.thermal, 15.75)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 21.25)
        self.assertAlmostEqual(volley.total, 50)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_no_attrib_single_expl(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.em_damage: 5.2,
            AttributeId.thermal_damage: 6.3,
            AttributeId.kinetic_damage: 7.4}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 13)
        self.assertAlmostEqual(volley.thermal, 15.75)
        self.assertAlmostEqual(volley.kinetic, 18.5)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 47.25)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_no_attrib_all(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(
            attributes={AttributeId.volume: 0.2}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 4)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_attrib_em(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(
            attributes={AttributeId.volume: 0.2, AttributeId.em_damage: 0}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_attrib_therm(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.thermal_damage: 0}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_attrib_kin(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.kinetic_damage: 0}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_attrib_expl(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.explosive_damage: 0}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_effective(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.em_damage: 5.2,
            AttributeId.thermal_damage: 6.3, AttributeId.kinetic_damage: 7.4,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistanceProfile(
            em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = item.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 10.4)
        self.assertAlmostEqual(volley.thermal, 12.6)
        self.assertAlmostEqual(volley.kinetic, 3.7)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 26.7)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_effective_no_attrib_single_em(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.thermal_damage: 6.3,
            AttributeId.kinetic_damage: 7.4,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistanceProfile(
            em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = item.get_nominal_volley(target_resistances=profile)
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 12.6)
        self.assertAlmostEqual(volley.kinetic, 3.7)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 16.3)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_effective_no_attrib_single_therm(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.em_damage: 5.2,
            AttributeId.kinetic_damage: 7.4,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistanceProfile(
            em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = item.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 10.4)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 3.7)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 14.1)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_effective_no_attrib_single_kin(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.em_damage: 5.2,
            AttributeId.thermal_damage: 6.3,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistanceProfile(
            em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = item.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 10.4)
        self.assertAlmostEqual(volley.thermal, 12.6)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 23)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_effective_no_attrib_single_expl(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.em_damage: 5.2,
            AttributeId.thermal_damage: 6.3,
            AttributeId.kinetic_damage: 7.4}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistanceProfile(
            em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = item.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 10.4)
        self.assertAlmostEqual(volley.thermal, 12.6)
        self.assertAlmostEqual(volley.kinetic, 3.7)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 26.7)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_effective_no_attrib_all(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(
            attributes={AttributeId.volume: 0.2}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistanceProfile(
            em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = item.get_nominal_volley(target_resistances=profile)
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 4)
        self.assert_fit_buffers_empty(fit)

    def test_effective_single_zero_attrib_em(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(
            attributes={AttributeId.volume: 0.2, AttributeId.em_damage: 0}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistanceProfile(
            em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = item.get_nominal_volley(target_resistances=profile)
        self.assertAlmostEqual(volley.em, 0)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_effective_single_zero_attrib_therm(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.thermal_damage: 0}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistanceProfile(
            em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = item.get_nominal_volley(target_resistances=profile)
        self.assertIsNone(volley.em)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_effective_single_zero_attrib_kin(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.kinetic_damage: 0}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistanceProfile(
            em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = item.get_nominal_volley(target_resistances=profile)
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertIsNone(volley.explosive)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_effective_single_zero_attrib_expl(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.explosive_damage: 0}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistanceProfile(
            em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        volley = item.get_nominal_volley(target_resistances=profile)
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_no_charged_cycles(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 2.1, AttributeId.em_damage: 5.2,
            AttributeId.thermal_damage: 6.3, AttributeId.kinetic_damage: 7.4,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_no_source(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500, AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2, AttributeId.em_damage: 5.2,
            AttributeId.thermal_damage: 6.3, AttributeId.kinetic_damage: 7.4,
            AttributeId.explosive_damage: 8.5}).id)
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
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
