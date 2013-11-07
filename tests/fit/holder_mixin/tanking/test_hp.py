#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from eos.const.eve import Attribute
from eos.fit.holder.mixin.tanking import BufferTankingMixin
from eos.tests.fit.fit_testcase import FitTestCase


class TestHolderMixinTankingHp(FitTestCase):

    def setUp(self):
        FitTestCase.setUp(self)
        self.mixin = BufferTankingMixin(type_id=None)
        self.mixin.attributes = {}

    def test_generic(self):
        self.mixin.attributes[Attribute.hp] = 8
        self.mixin.attributes[Attribute.armor_hp] = 10
        self.mixin.attributes[Attribute.shield_capacity] = 12
        self.assertAlmostEqual(self.mixin.hp.hull, 8)
        self.assertAlmostEqual(self.mixin.hp.armor, 10)
        self.assertAlmostEqual(self.mixin.hp.shield, 12)
        self.assertAlmostEqual(self.mixin.hp.total, 30)

    def test_unspecified(self):
        self.assertIsNone(self.mixin.hp.hull)
        self.assertIsNone(self.mixin.hp.armor)
        self.assertIsNone(self.mixin.hp.shield)
        self.assertEqual(self.mixin.hp.total, 0)

    def test_cache(self):
        self.mixin.attributes[Attribute.hp] = 8
        self.mixin.attributes[Attribute.armor_hp] = 10
        self.mixin.attributes[Attribute.shield_capacity] = 12
        self.assertAlmostEqual(self.mixin.hp.hull, 8)
        self.assertAlmostEqual(self.mixin.hp.armor, 10)
        self.assertAlmostEqual(self.mixin.hp.shield, 12)
        self.assertAlmostEqual(self.mixin.hp.total, 30)
        self.mixin.attributes[Attribute.hp] = 18
        self.mixin.attributes[Attribute.armor_hp] = 110
        self.mixin.attributes[Attribute.shield_capacity] = 112
        self.assertAlmostEqual(self.mixin.hp.hull, 8)
        self.assertAlmostEqual(self.mixin.hp.armor, 10)
        self.assertAlmostEqual(self.mixin.hp.shield, 12)
        self.assertAlmostEqual(self.mixin.hp.total, 30)

    def test_volatility(self):
        self.mixin.attributes[Attribute.hp] = 8
        self.mixin.attributes[Attribute.armor_hp] = 10
        self.mixin.attributes[Attribute.shield_capacity] = 12
        self.assertAlmostEqual(self.mixin.hp.hull, 8)
        self.assertAlmostEqual(self.mixin.hp.armor, 10)
        self.assertAlmostEqual(self.mixin.hp.shield, 12)
        self.assertAlmostEqual(self.mixin.hp.total, 30)
        self.mixin._clear_volatile_attrs()
        self.mixin.attributes[Attribute.hp] = 18
        self.mixin.attributes[Attribute.armor_hp] = 110
        self.mixin.attributes[Attribute.shield_capacity] = 112
        self.assertAlmostEqual(self.mixin.hp.hull, 18)
        self.assertAlmostEqual(self.mixin.hp.armor, 110)
        self.assertAlmostEqual(self.mixin.hp.shield, 112)
        self.assertAlmostEqual(self.mixin.hp.total, 240)
