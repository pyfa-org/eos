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
from eos.const.eve import AttrId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemModuleChargeQuantity(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.capacity)
        self.mkattr(attr_id=AttrId.volume)

    def test_generic(self):
        fit = Fit()
        item = ModuleHigh(self.mktype(attrs={AttrId.capacity: 20.0}).id)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 2.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.charge_quantity, 10)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_float_error(self):
        fit = Fit()
        item = ModuleHigh(self.mktype(attrs={AttrId.capacity: 2.3}).id)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 0.1}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.charge_quantity, 23)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_round_down(self):
        fit = Fit()
        item = ModuleHigh(self.mktype(attrs={AttrId.capacity: 19.7}).id)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 2.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.charge_quantity, 9)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_attr_capacity_absent(self):
        fit = Fit()
        item = ModuleHigh(self.mktype().id)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 2.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charge_quantity)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge_attr_volume_absent(self):
        fit = Fit()
        item = ModuleHigh(self.mktype(attrs={AttrId.capacity: 20.0}).id)
        item.charge = Charge(self.mktype().id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charge_quantity)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge_absent(self):
        fit = Fit()
        item = ModuleHigh(self.mktype(attrs={AttrId.capacity: 20.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charge_quantity)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_not_loaded(self):
        fit = Fit()
        item = ModuleHigh(self.allocate_type_id())
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 2.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charge_quantity)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)

    def test_charge_not_loaded(self):
        fit = Fit()
        item = ModuleHigh(self.mktype(attrs={AttrId.capacity: 20.0}).id)
        item.charge = Charge(self.allocate_type_id())
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.charge_quantity)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assertEqual(len(self.get_log()), 0)
