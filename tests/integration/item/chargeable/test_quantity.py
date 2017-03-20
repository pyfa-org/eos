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


from eos.const.eve import Attribute
from eos.fit.container import ItemSet
from eos.fit.item import ModuleHigh, Charge
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemMixinChargeQuantity(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.item = ModuleHigh(type_id=None)
        self.item.attributes = {}
        self.charge = Charge(type_id=None)
        self.charge.attributes = {}
        self.item.charge = self.charge

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.container = ItemSet(fit, ModuleHigh)
        return fit

    def test_generic(self):
        self.item.attributes[Attribute.capacity] = 20.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.assertEqual(self.item.charge_quantity, 10)

    def test_float_error(self):
        self.item.attributes[Attribute.capacity] = 2.3
        self.charge.attributes[Attribute.volume] = 0.1
        self.assertEqual(self.item.charge_quantity, 23)

    def test_round_down(self):
        self.item.attributes[Attribute.capacity] = 19.7
        self.charge.attributes[Attribute.volume] = 2.0
        self.assertEqual(self.item.charge_quantity, 9)

    def test_no_volume(self):
        self.item.attributes[Attribute.capacity] = 20.0
        self.assertIsNone(self.item.charge_quantity)

    def test_no_capacity(self):
        self.charge.attributes[Attribute.volume] = 2.0
        self.assertIsNone(self.item.charge_quantity)

    def test_no_charge(self):
        self.item.attributes[Attribute.capacity] = 20.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.item.charge = None
        self.assertIsNone(self.item.charge_quantity)

    def test_cache(self):
        self.item.attributes[Attribute.capacity] = 20.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.assertEqual(self.item.charge_quantity, 10)
        self.item.attributes[Attribute.capacity] = 200.0
        self.charge.attributes[Attribute.volume] = 1.0
        self.assertEqual(self.item.charge_quantity, 10)

    def test_volatility(self):
        self.item.attributes[Attribute.capacity] = 20.0
        self.charge.attributes[Attribute.volume] = 2.0
        self.assertEqual(self.item.charge_quantity, 10)
        self.item._clear_volatile_attrs()
        self.item.attributes[Attribute.capacity] = 200.0
        self.charge.attributes[Attribute.volume] = 1.0
        self.assertEqual(self.item.charge_quantity, 200)
