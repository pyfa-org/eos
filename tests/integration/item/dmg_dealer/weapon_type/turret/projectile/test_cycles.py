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


class TestItemDmgTurretProjectileCycles(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.capacity)
        self.mkattr(attr_id=AttrId.volume)
        self.mkattr(attr_id=AttrId.charge_rate)
        self.cycle_attr = self.mkattr()
        self.effect = self.mkeffect(
            effect_id=EffectId.projectile_fired,
            category_id=EffectCategoryId.target,
            duration_attr_id=self.cycle_attr.id)

    def test_generic(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    AttrId.charge_rate: 1.0},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 30.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.cycles_until_reload, 2)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_round_down(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 85.0,
                    AttrId.charge_rate: 1.0},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 30.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.cycles_until_reload, 2)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_charge_quantity_none(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.charge_rate: 1.0},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 30.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.cycles_until_reload)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_attr_charge_rate_zero(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    AttrId.charge_rate: 0.0},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 30.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.cycles_until_reload)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_item_attr_charge_rate_absent(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.capacity: 60.0},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 30.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.cycles_until_reload)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_charge_not_loaded(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 60.0,
                    AttrId.charge_rate: 1.0},
                effects=[self.effect],
                default_effect=self.effect).id,
            state=State.active)
        item.charge = Charge(self.allocate_type_id())
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.cycles_until_reload)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)
