# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from unittest.mock import Mock

from eos.const.eve import Attribute
from eos.data.source import Source
from eos.fit.holder.container import HolderSet
from eos.fit.holder.item import Ship
from tests.fit.fit_testcase import FitTestCase


class TestHolderMixinTankingHp(FitTestCase):

    def setUp(self):
        super().setUp()
        self.holder = Ship(type_id=None)
        self.holder._clear_volatile_attrs = Mock()
        self.holder.attributes = {}

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.container = HolderSet(fit, Ship)
        return fit

    def test_generic(self):
        self.holder.attributes[Attribute.hp] = 8
        self.holder.attributes[Attribute.armor_hp] = 10
        self.holder.attributes[Attribute.shield_capacity] = 12
        self.assertAlmostEqual(self.holder.hp.hull, 8)
        self.assertAlmostEqual(self.holder.hp.armor, 10)
        self.assertAlmostEqual(self.holder.hp.shield, 12)
        self.assertAlmostEqual(self.holder.hp.hull_max, 8)
        self.assertAlmostEqual(self.holder.hp.armor_max, 10)
        self.assertAlmostEqual(self.holder.hp.shield_max, 12)
        self.assertAlmostEqual(self.holder.hp.total, 30)

    def test_unspecified(self):
        self.assertIsNone(self.holder.hp.hull)
        self.assertIsNone(self.holder.hp.armor)
        self.assertIsNone(self.holder.hp.shield)
        self.assertIsNone(self.holder.hp.hull_max)
        self.assertIsNone(self.holder.hp.armor_max)
        self.assertIsNone(self.holder.hp.shield_max)
        self.assertIsNone(self.holder.hp.total)

    def test_override_set_int(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = self.holder
        fit.container.add(holder)
        holder.attributes[Attribute.hp] = 8
        holder.attributes[Attribute.armor_hp] = 10
        holder.attributes[Attribute.shield_capacity] = 12
        self.assertAlmostEqual(holder.hp.hull, 8)
        self.assertAlmostEqual(holder.hp.armor, 10)
        self.assertAlmostEqual(holder.hp.shield, 12)
        self.assertAlmostEqual(holder.hp.hull_max, 8)
        self.assertAlmostEqual(holder.hp.armor_max, 10)
        self.assertAlmostEqual(holder.hp.shield_max, 12)
        self.assertAlmostEqual(holder.hp.total, 30)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        holder.hp.hull = 100
        st_cleans_between1 = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_between1 = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between1 - st_cleans_before, 1)
        self.assertEqual(holder_cleans_between1 - holder_cleans_before, 1)
        holder.hp.armor = 200
        st_cleans_between2 = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_between2 = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between2 - st_cleans_between1, 1)
        self.assertEqual(holder_cleans_between2 - holder_cleans_between1, 1)
        holder.hp.shield = 300
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_between2, 1)
        self.assertEqual(holder_cleans_after - holder_cleans_between2, 1)
        self.assertAlmostEqual(holder.hp.hull, 100)
        self.assertAlmostEqual(holder.hp.armor, 200)
        self.assertAlmostEqual(holder.hp.shield, 300)
        self.assertAlmostEqual(holder.hp.hull_max, 8)
        self.assertAlmostEqual(holder.hp.armor_max, 10)
        self.assertAlmostEqual(holder.hp.shield_max, 12)
        self.assertAlmostEqual(holder.hp.total, 600)

    def test_override_set_float(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = self.holder
        fit.container.add(holder)
        holder.attributes[Attribute.hp] = 8
        holder.attributes[Attribute.armor_hp] = 10
        holder.attributes[Attribute.shield_capacity] = 12
        self.assertAlmostEqual(holder.hp.hull, 8)
        self.assertAlmostEqual(holder.hp.armor, 10)
        self.assertAlmostEqual(holder.hp.shield, 12)
        self.assertAlmostEqual(holder.hp.hull_max, 8)
        self.assertAlmostEqual(holder.hp.armor_max, 10)
        self.assertAlmostEqual(holder.hp.shield_max, 12)
        self.assertAlmostEqual(holder.hp.total, 30)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        holder.hp.hull = 100.5
        st_cleans_between1 = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_between1 = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between1 - st_cleans_before, 1)
        self.assertEqual(holder_cleans_between1 - holder_cleans_before, 1)
        holder.hp.armor = 200.5
        st_cleans_between2 = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_between2 = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between2 - st_cleans_between1, 1)
        self.assertEqual(holder_cleans_between2 - holder_cleans_between1, 1)
        holder.hp.shield = 300.5
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_between2, 1)
        self.assertEqual(holder_cleans_after - holder_cleans_between2, 1)
        self.assertAlmostEqual(holder.hp.hull, 100.5)
        self.assertAlmostEqual(holder.hp.armor, 200.5)
        self.assertAlmostEqual(holder.hp.shield, 300.5)
        self.assertAlmostEqual(holder.hp.hull_max, 8)
        self.assertAlmostEqual(holder.hp.armor_max, 10)
        self.assertAlmostEqual(holder.hp.shield_max, 12)
        self.assertAlmostEqual(holder.hp.total, 601.5)

    def test_override_set_other(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = self.holder
        fit.container.add(holder)
        holder.attributes[Attribute.hp] = 8
        holder.attributes[Attribute.armor_hp] = 10
        holder.attributes[Attribute.shield_capacity] = 12
        self.assertAlmostEqual(holder.hp.hull, 8)
        self.assertAlmostEqual(holder.hp.armor, 10)
        self.assertAlmostEqual(holder.hp.shield, 12)
        self.assertAlmostEqual(holder.hp.hull_max, 8)
        self.assertAlmostEqual(holder.hp.armor_max, 10)
        self.assertAlmostEqual(holder.hp.shield_max, 12)
        self.assertAlmostEqual(holder.hp.total, 30)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        self.assertRaises(TypeError, holder.hp.__setattr__, 'hull', 'a')
        st_cleans_between1 = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_between1 = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between1 - st_cleans_before, 0)
        self.assertEqual(holder_cleans_between1 - holder_cleans_before, 0)
        self.assertRaises(TypeError, holder.hp.__setattr__, 'armor', 'b')
        st_cleans_between2 = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_between2 = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between2 - st_cleans_between1, 0)
        self.assertEqual(holder_cleans_between2 - holder_cleans_between1, 0)
        self.assertRaises(TypeError, holder.hp.__setattr__, 'shield', 'c')
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_between2, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_between2, 0)
        self.assertAlmostEqual(holder.hp.hull, 8)
        self.assertAlmostEqual(holder.hp.armor, 10)
        self.assertAlmostEqual(holder.hp.shield, 12)
        self.assertAlmostEqual(holder.hp.hull_max, 8)
        self.assertAlmostEqual(holder.hp.armor_max, 10)
        self.assertAlmostEqual(holder.hp.shield_max, 12)
        self.assertAlmostEqual(holder.hp.total, 30)

    def test_override_del(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = self.holder
        fit.container.add(holder)
        holder.attributes[Attribute.hp] = 8
        holder.attributes[Attribute.armor_hp] = 10
        holder.attributes[Attribute.shield_capacity] = 12
        self.assertAlmostEqual(holder.hp.hull, 8)
        self.assertAlmostEqual(holder.hp.armor, 10)
        self.assertAlmostEqual(holder.hp.shield, 12)
        self.assertAlmostEqual(holder.hp.hull_max, 8)
        self.assertAlmostEqual(holder.hp.armor_max, 10)
        self.assertAlmostEqual(holder.hp.shield_max, 12)
        self.assertAlmostEqual(holder.hp.total, 30)
        holder.hp.hull = 100
        holder.hp.armor = 200
        holder.hp.shield = 300
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        del holder.hp.hull
        st_cleans_between1 = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_between1 = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between1 - st_cleans_before, 1)
        self.assertEqual(holder_cleans_between1 - holder_cleans_before, 1)
        del holder.hp.armor
        st_cleans_between2 = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_between2 = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between2 - st_cleans_between1, 1)
        self.assertEqual(holder_cleans_between2 - holder_cleans_between1, 1)
        del holder.hp.shield
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_between2, 1)
        self.assertEqual(holder_cleans_after - holder_cleans_between2, 1)
        self.assertAlmostEqual(holder.hp.hull, 8)
        self.assertAlmostEqual(holder.hp.armor, 10)
        self.assertAlmostEqual(holder.hp.shield, 12)
        self.assertAlmostEqual(holder.hp.hull_max, 8)
        self.assertAlmostEqual(holder.hp.armor_max, 10)
        self.assertAlmostEqual(holder.hp.shield_max, 12)
        self.assertAlmostEqual(holder.hp.total, 30)
