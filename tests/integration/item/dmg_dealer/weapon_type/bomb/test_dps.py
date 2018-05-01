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


from eos import Charge
from eos import Fit
from eos import ModuleHigh
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemDmgBombDps(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.capacity)
        self.mkattr(attr_id=AttrId.volume)
        self.mkattr(attr_id=AttrId.charge_rate)
        self.mkattr(attr_id=AttrId.reload_time)
        self.mkattr(attr_id=AttrId.module_reactivation_delay)
        self.mkattr(attr_id=AttrId.em_dmg)
        self.mkattr(attr_id=AttrId.therm_dmg)
        self.mkattr(attr_id=AttrId.kin_dmg)
        self.mkattr(attr_id=AttrId.expl_dmg)
        self.cycle_attr = self.mkattr()
        self.effect_item = self.mkeffect(
            effect_id=EffectId.use_missiles,
            category_id=EffectCategoryId.active,
            duration_attr_id=self.cycle_attr.id)
        self.effect_charge = self.mkeffect(
            effect_id=EffectId.bomb_launching,
            category_id=EffectCategoryId.active)

    def test_no_reload(self):
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
                AttrId.therm_dmg: 6300,
                AttrId.kin_dmg: 7400,
                AttrId.expl_dmg: 8500},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_dps(reload=False)
        self.assertAlmostEqual(dps.em, 41.6)
        self.assertAlmostEqual(dps.thermal, 50.4)
        self.assertAlmostEqual(dps.kinetic, 59.2)
        self.assertAlmostEqual(dps.explosive, 68)
        self.assertAlmostEqual(dps.total, 219.2)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_reload(self):
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
                AttrId.therm_dmg: 6300,
                AttrId.kin_dmg: 7400,
                AttrId.expl_dmg: 8500},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_dps(reload=True)
        # Reload doesn't affect DPS because reactivation time is higher, item
        # manages to reload during that time
        self.assertAlmostEqual(dps.em, 41.6)
        self.assertAlmostEqual(dps.thermal, 50.4)
        self.assertAlmostEqual(dps.kinetic, 59.2)
        self.assertAlmostEqual(dps.explosive, 68)
        self.assertAlmostEqual(dps.total, 219.2)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_charge_not_loaded(self):
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
        item.charge = Charge(self.allocate_type_id())
        fit.modules.high.append(item)
        # Verification
        dps = item.get_dps()
        self.assertAlmostEqual(dps.em, 0)
        self.assertAlmostEqual(dps.thermal, 0)
        self.assertAlmostEqual(dps.kinetic, 0)
        self.assertAlmostEqual(dps.explosive, 0)
        self.assertAlmostEqual(dps.total, 0)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)
