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


from eos import Fit
from eos import Ship
from eos.const.eve import AttrId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemMixinTankingHp(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.hp)
        self.mkattr(attr_id=AttrId.armor_hp)
        self.mkattr(attr_id=AttrId.shield_capacity)

    def test_generic(self):
        fit = Fit()
        item = Ship(self.mktype(attrs={
            AttrId.hp: 8,
            AttrId.armor_hp: 10,
            AttrId.shield_capacity: 12}).id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.hp.hull, 8)
        self.assertAlmostEqual(item.hp.armor, 10)
        self.assertAlmostEqual(item.hp.shield, 12)
        self.assertAlmostEqual(item.hp.total, 30)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_attr_all_absent(self):
        fit = Fit()
        item = Ship(self.mktype().id)
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.hp.hull, 0)
        self.assertAlmostEqual(item.hp.armor, 0)
        self.assertAlmostEqual(item.hp.shield, 0)
        self.assertAlmostEqual(item.hp.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_not_loaded(self):
        fit = Fit()
        item = Ship(self.allocate_type_id())
        fit.ship = item
        # Verification
        self.assertAlmostEqual(item.hp.hull, 0)
        self.assertAlmostEqual(item.hp.armor, 0)
        self.assertAlmostEqual(item.hp.shield, 0)
        self.assertAlmostEqual(item.hp.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
