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

from eos.fit.holder.mixin.tanking import BufferTankingMixin
from tests.fit.fit_testcase import FitTestCase


class TestHolderMixinTankingWorstCaseEhp(FitTestCase):

    def setUp(self):
        super().setUp()
        self.mixin = BufferTankingMixin()
        self.mixin.hp = Mock()
        self.mixin.resistances = Mock()
        self.mixin.attributes = {}

    def test_equal(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.8
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 526.25)

    def test_worst_em(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.3
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.3
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.7
        mixin.resistances.armor.kinetic = 0.7
        mixin.resistances.armor.explosive = 0.7
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.9
        mixin.resistances.shield.kinetic = 0.9
        mixin.resistances.shield.explosive = 0.9
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 526.25)

    def test_worst_thermal(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.3
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.3
        mixin.resistances.armor.em = 0.7
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.7
        mixin.resistances.armor.explosive = 0.7
        mixin.resistances.shield.em = 0.9
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.9
        mixin.resistances.shield.explosive = 0.9
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 526.25)

    def test_worst_kinetic(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.3
        mixin.resistances.hull.thermal = 0.3
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.3
        mixin.resistances.armor.em = 0.7
        mixin.resistances.armor.thermal = 0.7
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.7
        mixin.resistances.shield.em = 0.9
        mixin.resistances.shield.thermal = 0.9
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.9
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 526.25)

    def test_worst_explosive(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.3
        mixin.resistances.hull.thermal = 0.3
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.7
        mixin.resistances.armor.thermal = 0.7
        mixin.resistances.armor.kinetic = 0.7
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = 0.9
        mixin.resistances.shield.thermal = 0.9
        mixin.resistances.shield.kinetic = 0.9
        mixin.resistances.shield.explosive = 0.8
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 526.25)

    def test_mixed(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.3
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.7
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.7
        mixin.resistances.shield.em = 0.9
        mixin.resistances.shield.thermal = 0.9
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.99
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 526.25)

    def test_none_hp_hull(self):
        mixin = self.mixin
        mixin.hp.hull = None
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.8
        self.assertIsNone(mixin.worst_case_ehp.hull)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 525)

    def test_none_hp_armor(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = None
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.8
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertIsNone(mixin.worst_case_ehp.armor)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 501.25)

    def test_none_hp_shield(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = None
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.8
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertIsNone(mixin.worst_case_ehp.shield)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 26.25)

    def test_none_hp_all(self):
        mixin = self.mixin
        mixin.hp.hull = None
        mixin.hp.armor = None
        mixin.hp.shield = None
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.8
        self.assertIsNone(mixin.worst_case_ehp.hull)
        self.assertIsNone(mixin.worst_case_ehp.armor)
        self.assertIsNone(mixin.worst_case_ehp.shield)
        self.assertIsNone(mixin.worst_case_ehp.total)

    def test_none_resistance_em(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = None
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.8
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 526)

    def test_none_resistance_thermal(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = None
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.8
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 10)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 511.25)

    def test_none_resistance_kinetic(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = None
        mixin.resistances.shield.explosive = 0.8
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 100)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 126.25)

    def test_none_resistance_explosive(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = None
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.8
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 10)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 511.25)

    def test_none_resistance_all(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = None
        mixin.resistances.shield.thermal = None
        mixin.resistances.shield.kinetic = None
        mixin.resistances.shield.explosive = None
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 100)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 126.25)

    def test_cache(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.8
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 526.25)
        mixin.hp.hull = 10
        mixin.hp.armor = 100
        mixin.hp.shield = 1000
        mixin.resistances.hull.em = 0.3
        mixin.resistances.hull.thermal = 0.3
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.3
        mixin.resistances.armor.em = 0.4
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.4
        mixin.resistances.armor.explosive = 0.4
        mixin.resistances.shield.em = 0.9
        mixin.resistances.shield.thermal = 0.9
        mixin.resistances.shield.kinetic = 0.9
        mixin.resistances.shield.explosive = 0.9
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 526.25)

    def test_volatility(self):
        mixin = self.mixin
        mixin.hp.hull = 1
        mixin.hp.armor = 10
        mixin.hp.shield = 100
        mixin.resistances.hull.em = 0.2
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.2
        mixin.resistances.hull.explosive = 0.2
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.6
        mixin.resistances.armor.kinetic = 0.6
        mixin.resistances.armor.explosive = 0.6
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.8
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 1.25)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 25)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 500)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 526.25)
        mixin._clear_volatile_attrs()
        mixin.hp.hull = 10
        mixin.hp.armor = 100
        mixin.hp.shield = 1000
        mixin.resistances.hull.em = 0.5
        mixin.resistances.hull.thermal = 0.5
        mixin.resistances.hull.kinetic = 0.5
        mixin.resistances.hull.explosive = 0.5
        mixin.resistances.armor.em = 0.2
        mixin.resistances.armor.thermal = 0.2
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.2
        mixin.resistances.shield.em = 0.8
        mixin.resistances.shield.thermal = 0.8
        mixin.resistances.shield.kinetic = 0.8
        mixin.resistances.shield.explosive = 0.8
        self.assertAlmostEqual(mixin.worst_case_ehp.hull, 20)
        self.assertAlmostEqual(mixin.worst_case_ehp.armor, 125)
        self.assertAlmostEqual(mixin.worst_case_ehp.shield, 5000)
        self.assertAlmostEqual(mixin.worst_case_ehp.total, 5145)
