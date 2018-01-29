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


from eos import Charge
from eos import EffectMode
from eos import Fit
from eos import ModuleHigh
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemDmgBombVolley(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.capacity)
        self.mkattr(attr_id=AttrId.volume)
        self.mkattr(attr_id=AttrId.charge_rate)
        self.mkattr(attr_id=AttrId.reload_time)
        self.mkattr(attr_id=AttrId.module_reactivation_delay)
        self.mkattr(attr_id=AttrId.em_dmg)
        self.mkattr(attr_id=AttrId.thermal_dmg)
        self.mkattr(attr_id=AttrId.kinetic_dmg)
        self.mkattr(attr_id=AttrId.explosive_dmg)
        self.cycle_attr = self.mkattr()
        self.effect_item = self.mkeffect(
            effect_id=EffectId.use_missiles,
            category_id=EffectCategoryId.active,
            duration_attr_id=self.cycle_attr.id)
        self.effect_charge = self.mkeffect(
            effect_id=EffectId.bomb_launching,
            category_id=EffectCategoryId.active)

    def test_generic(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    self.cycle_attr.id: 5000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000,
                    AttrId.module_reactivation_delay: 120000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={
                AttrId.volume: 30.0,
                AttrId.em_dmg: 5200,
                AttrId.thermal_dmg: 6300,
                AttrId.kinetic_dmg: 7400,
                AttrId.explosive_dmg: 8500},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 5200)
        self.assertAlmostEqual(volley.thermal, 6300)
        self.assertAlmostEqual(volley.kinetic, 7400)
        self.assertAlmostEqual(volley.explosive, 8500)
        self.assertAlmostEqual(volley.total, 27400)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_em(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    self.cycle_attr.id: 5000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000,
                    AttrId.module_reactivation_delay: 120000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={
                AttrId.volume: 30.0,
                AttrId.thermal_dmg: 6300,
                AttrId.kinetic_dmg: 7400,
                AttrId.explosive_dmg: 8500},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 6300)
        self.assertAlmostEqual(volley.kinetic, 7400)
        self.assertAlmostEqual(volley.explosive, 8500)
        self.assertAlmostEqual(volley.total, 22200)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_therm(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    self.cycle_attr.id: 5000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000,
                    AttrId.module_reactivation_delay: 120000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={
                AttrId.volume: 30.0,
                AttrId.em_dmg: 5200,
                AttrId.kinetic_dmg: 7400,
                AttrId.explosive_dmg: 8500},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 5200)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 7400)
        self.assertAlmostEqual(volley.explosive, 8500)
        self.assertAlmostEqual(volley.total, 21100)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_kin(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    self.cycle_attr.id: 5000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000,
                    AttrId.module_reactivation_delay: 120000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={
                AttrId.volume: 30.0,
                AttrId.em_dmg: 5200,
                AttrId.thermal_dmg: 6300,
                AttrId.explosive_dmg: 8500},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 5200)
        self.assertAlmostEqual(volley.thermal, 6300)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 8500)
        self.assertAlmostEqual(volley.total, 20000)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_attr_expl(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    self.cycle_attr.id: 5000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000,
                    AttrId.module_reactivation_delay: 120000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={
                AttrId.volume: 30.0,
                AttrId.em_dmg: 5200,
                AttrId.thermal_dmg: 6300,
                AttrId.kinetic_dmg: 7400},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 5200)
        self.assertAlmostEqual(volley.thermal, 6300)
        self.assertAlmostEqual(volley.kinetic, 7400)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 18900)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_insufficient_state(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    self.cycle_attr.id: 5000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000,
                    AttrId.module_reactivation_delay: 120000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.online)
        item.charge = Charge(self.mktype(
            attrs={
                AttrId.volume: 30.0,
                AttrId.em_dmg: 5200,
                AttrId.thermal_dmg: 6300,
                AttrId.kinetic_dmg: 7400,
                AttrId.explosive_dmg: 8500},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_disabled_item_effect(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    self.cycle_attr.id: 5000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000,
                    AttrId.module_reactivation_delay: 120000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.active)
        item.set_effect_mode(self.effect_item.id, EffectMode.force_stop)
        item.charge = Charge(self.mktype(
            attrs={
                AttrId.volume: 30.0,
                AttrId.em_dmg: 5200,
                AttrId.thermal_dmg: 6300,
                AttrId.kinetic_dmg: 7400,
                AttrId.explosive_dmg: 8500},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_disabled_charge_effect(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    self.cycle_attr.id: 5000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000,
                    AttrId.module_reactivation_delay: 120000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={
                AttrId.volume: 30.0,
                AttrId.em_dmg: 5200,
                AttrId.thermal_dmg: 6300,
                AttrId.kinetic_dmg: 7400,
                AttrId.explosive_dmg: 8500},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        item.charge.set_effect_mode(
            self.effect_charge.id, EffectMode.force_stop)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_charge(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    self.cycle_attr.id: 5000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000,
                    AttrId.module_reactivation_delay: 120000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.active)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_cycles_until_reload(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    self.cycle_attr.id: 5000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000,
                    AttrId.module_reactivation_delay: 120000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={
                AttrId.volume: 61.0,
                AttrId.em_dmg: 5200,
                AttrId.thermal_dmg: 6300,
                AttrId.kinetic_dmg: 7400,
                AttrId.explosive_dmg: 8500},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    self.cycle_attr.id: 5000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000,
                    AttrId.module_reactivation_delay: 120000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={
                AttrId.volume: 30.0,
                AttrId.em_dmg: 5200,
                AttrId.thermal_dmg: 6300,
                AttrId.kinetic_dmg: 7400,
                AttrId.explosive_dmg: 8500},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        fit.source = None
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 0)
        self.assertAlmostEqual(volley.thermal, 0)
        self.assertAlmostEqual(volley.kinetic, 0)
        self.assertAlmostEqual(volley.explosive, 0)
        self.assertAlmostEqual(volley.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)