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


class TestItemDamageMiscNominalDps(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.ch.attr(attribute_id=AttributeId.capacity)
        self.ch.attr(attribute_id=AttributeId.volume)
        self.ch.attr(attribute_id=AttributeId.charge_rate)
        self.ch.attr(attribute_id=AttributeId.reload_time)
        self.ch.attr(attribute_id=AttributeId.damage_multiplier)
        self.ch.attr(attribute_id=AttributeId.em_damage)
        self.ch.attr(attribute_id=AttributeId.thermal_damage)
        self.ch.attr(attribute_id=AttributeId.kinetic_damage)
        self.ch.attr(attribute_id=AttributeId.explosive_damage)
        self.ch.attr(attribute_id=AttributeId.module_reactivation_delay)
        self.cycle_attr = self.ch.attr()
        self.effect = self.ch.effect(
            effect_id=EffectId.projectile_fired,
            category_id=EffectCategoryId.active,
            duration_attribute_id=self.cycle_attr.id)

    def test_effective(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2,
            AttributeId.em_damage: 5.2,
            AttributeId.thermal_damage: 6.3,
            AttributeId.kinetic_damage: 7.4,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        profile = ResistanceProfile(
            em=0.2, thermal=0.2, kinetic=0.8, explosive=1)
        dps = item.get_nominal_dps(target_resistances=profile)
        self.assertAlmostEqual(dps.em, 20.8)
        self.assertAlmostEqual(dps.thermal, 25.2)
        self.assertAlmostEqual(dps.kinetic, 7.4)
        self.assertAlmostEqual(dps.explosive, 0)
        self.assertAlmostEqual(dps.total, 53.4)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_reactivation_shorter_than_reload(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 6500,
                    AttributeId.module_reactivation_delay: 1500},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2,
            AttributeId.em_damage: 5.2,
            AttributeId.thermal_damage: 6.3,
            AttributeId.kinetic_damage: 7.4,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 5.2)
        self.assertAlmostEqual(dps.thermal, 6.3)
        self.assertAlmostEqual(dps.kinetic, 7.4)
        self.assertAlmostEqual(dps.explosive, 8.5)
        self.assertAlmostEqual(dps.total, 27.4)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_reactivation_longer_than_reload(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 6500,
                    AttributeId.module_reactivation_delay: 19500},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2,
            AttributeId.em_damage: 5.2,
            AttributeId.thermal_damage: 6.3,
            AttributeId.kinetic_damage: 7.4,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 0.65)
        self.assertAlmostEqual(dps.thermal, 0.7875)
        self.assertAlmostEqual(dps.kinetic, 0.925)
        self.assertAlmostEqual(dps.explosive, 1.0625)
        self.assertAlmostEqual(dps.total, 3.425)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        fit = Fit()
        item = ModuleHigh(
            self.ch.type(
                attributes={
                    AttributeId.damage_multiplier: 2.5,
                    AttributeId.capacity: 2.0,
                    self.cycle_attr.id: 500,
                    AttributeId.charge_rate: 1.0,
                    AttributeId.reload_time: 5000},
                effects=[self.effect], default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            AttributeId.volume: 0.2,
            AttributeId.em_damage: 5.2,
            AttributeId.thermal_damage: 6.3,
            AttributeId.kinetic_damage: 7.4,
            AttributeId.explosive_damage: 8.5}).id)
        fit.modules.high.append(item)
        fit.source = None
        # Verification
        dps = item.get_nominal_dps()
        self.assertIsNone(dps.em)
        self.assertIsNone(dps.thermal)
        self.assertIsNone(dps.kinetic)
        self.assertIsNone(dps.explosive)
        self.assertIsNone(dps.total)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
