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


class TestHolderMixinTankingEhp(FitTestCase):

    def setUp(self):
        super().setUp()
        self.mixin = BufferTankingMixin()
        self.mixin.hp = Mock()
        self.mixin.resistances = Mock()
        self.mixin.attributes = {}

    def test_uniform(self):
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
        profile = Mock(em=1, thermal=1, kinetic=1, explosive=1)
        results = mixin.get_ehp(profile)
        self.assertAlmostEqual(results.hull, 1.25)
        self.assertAlmostEqual(results.armor, 25)
        self.assertAlmostEqual(results.shield, 500)
        self.assertAlmostEqual(results.total, 526.25)

    def test_non_uniform(self):
        mixin = self.mixin
        mixin.hp.hull = 10
        mixin.hp.armor = 50
        mixin.hp.shield = 600
        mixin.resistances.hull.em = 0.1
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.4
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.1
        mixin.resistances.shield.em = 0
        mixin.resistances.shield.thermal = 0.2
        mixin.resistances.shield.kinetic = 0.4
        mixin.resistances.shield.explosive = 0.5
        profile = Mock(em=25, thermal=6, kinetic=8.333, explosive=1)
        results = mixin.get_ehp(profile)
        self.assertAlmostEqual(results.hull, 11.956505628)
        self.assertAlmostEqual(results.armor, 95.2760034772)
        self.assertAlmostEqual(results.shield, 685.5506263491)
        self.assertAlmostEqual(results.total, 792.7831354543)

    def test_corrupted_all_zero(self):
        mixin = self.mixin
        mixin.hp.hull = 10
        mixin.hp.armor = 50
        mixin.hp.shield = 600
        mixin.resistances.hull.em = 0.1
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.4
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.1
        mixin.resistances.shield.em = 0
        mixin.resistances.shield.thermal = 0.2
        mixin.resistances.shield.kinetic = 0.4
        mixin.resistances.shield.explosive = 0.5
        profile = Mock(em=0, thermal=0, kinetic=0, explosive=0)
        self.assertRaises(ValueError, mixin.get_ehp, profile)

    def test_none_hp_hull(self):
        mixin = self.mixin
        mixin.hp.hull = None
        mixin.hp.armor = 50
        mixin.hp.shield = 600
        mixin.resistances.hull.em = 0.1
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.4
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.1
        mixin.resistances.shield.em = 0
        mixin.resistances.shield.thermal = 0.2
        mixin.resistances.shield.kinetic = 0.4
        mixin.resistances.shield.explosive = 0.5
        profile = Mock(em=25, thermal=6, kinetic=8.333, explosive=1)
        results = mixin.get_ehp(profile)
        self.assertIsNone(results.hull)
        self.assertAlmostEqual(results.armor, 95.2760034772)
        self.assertAlmostEqual(results.shield, 685.5506263491)
        self.assertAlmostEqual(results.total, 780.8266298263)

    def test_none_hp_armor(self):
        mixin = self.mixin
        mixin.hp.hull = 10
        mixin.hp.armor = None
        mixin.hp.shield = 600
        mixin.resistances.hull.em = 0.1
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.4
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.1
        mixin.resistances.shield.em = 0
        mixin.resistances.shield.thermal = 0.2
        mixin.resistances.shield.kinetic = 0.4
        mixin.resistances.shield.explosive = 0.5
        profile = Mock(em=25, thermal=6, kinetic=8.333, explosive=1)
        results = mixin.get_ehp(profile)
        self.assertAlmostEqual(results.hull, 11.956505628)
        self.assertIsNone(results.armor, 95.2760034772)
        self.assertAlmostEqual(results.shield, 685.5506263491)
        self.assertAlmostEqual(results.total, 697.5071319771)

    def test_none_hp_shield(self):
        mixin = self.mixin
        mixin.hp.hull = 10
        mixin.hp.armor = 50
        mixin.hp.shield = None
        mixin.resistances.hull.em = 0.1
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.4
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.1
        mixin.resistances.shield.em = 0
        mixin.resistances.shield.thermal = 0.2
        mixin.resistances.shield.kinetic = 0.4
        mixin.resistances.shield.explosive = 0.5
        profile = Mock(em=25, thermal=6, kinetic=8.333, explosive=1)
        results = mixin.get_ehp(profile)
        self.assertAlmostEqual(results.hull, 11.956505628)
        self.assertAlmostEqual(results.armor, 95.2760034772)
        self.assertIsNone(results.shield)
        self.assertAlmostEqual(results.total, 107.2325091052)

    def test_none_hp_all(self):
        mixin = self.mixin
        mixin.hp.hull = None
        mixin.hp.armor = None
        mixin.hp.shield = None
        mixin.resistances.hull.em = 0.1
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.4
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.1
        mixin.resistances.shield.em = 0
        mixin.resistances.shield.thermal = 0.2
        mixin.resistances.shield.kinetic = 0.4
        mixin.resistances.shield.explosive = 0.5
        profile = Mock(em=25, thermal=6, kinetic=8.333, explosive=1)
        results = mixin.get_ehp(profile)
        self.assertIsNone(results.hull)
        self.assertIsNone(results.armor)
        self.assertIsNone(results.shield)
        self.assertIsNone(results.total)

    def test_none_resistance_em(self):
        mixin = self.mixin
        mixin.hp.hull = 10
        mixin.hp.armor = 50
        mixin.hp.shield = 600
        mixin.resistances.hull.em = 0.1
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.4
        mixin.resistances.armor.em = None
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.1
        mixin.resistances.shield.em = 0
        mixin.resistances.shield.thermal = 0.2
        mixin.resistances.shield.kinetic = 0.4
        mixin.resistances.shield.explosive = 0.5
        profile = Mock(em=25, thermal=6, kinetic=8.333, explosive=1)
        results = mixin.get_ehp(profile)
        self.assertAlmostEqual(results.hull, 11.956505628)
        self.assertAlmostEqual(results.armor, 55.76031897)
        self.assertAlmostEqual(results.shield, 685.5506263491)
        self.assertAlmostEqual(results.total, 753.2674509472)

    def test_none_resistance_thermal(self):
        mixin = self.mixin
        mixin.hp.hull = 10
        mixin.hp.armor = 50
        mixin.hp.shield = 600
        mixin.resistances.hull.em = 0.1
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.4
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.1
        mixin.resistances.shield.em = 0
        mixin.resistances.shield.thermal = None
        mixin.resistances.shield.kinetic = 0.4
        mixin.resistances.shield.explosive = 0.5
        profile = Mock(em=25, thermal=6, kinetic=8.333, explosive=1)
        results = mixin.get_ehp(profile)
        self.assertAlmostEqual(results.hull, 11.956505628)
        self.assertAlmostEqual(results.armor, 95.2760034772)
        self.assertAlmostEqual(results.shield, 663.0118521197)
        self.assertAlmostEqual(results.total, 770.2443612249)

    def test_none_resistance_kinetic(self):
        mixin = self.mixin
        mixin.hp.hull = 10
        mixin.hp.armor = 50
        mixin.hp.shield = 600
        mixin.resistances.hull.em = 0.1
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.9
        mixin.resistances.hull.explosive = 0.4
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.1
        mixin.resistances.shield.em = 0
        mixin.resistances.shield.thermal = 0.2
        mixin.resistances.shield.kinetic = 0.4
        mixin.resistances.shield.explosive = 0.5
        profile = Mock(em=25, thermal=6, kinetic=8.333, explosive=1)
        results = mixin.get_ehp(profile)
        self.assertAlmostEqual(results.hull, 14.0370232448)
        self.assertAlmostEqual(results.armor, 95.2760034772)
        self.assertAlmostEqual(results.shield, 685.5506263491)
        self.assertAlmostEqual(results.total, 794.8636530711)

    def test_none_resistance_explosive(self):
        mixin = self.mixin
        mixin.hp.hull = 10
        mixin.hp.armor = 50
        mixin.hp.shield = 600
        mixin.resistances.hull.em = 0.1
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.67
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.1
        mixin.resistances.shield.em = 0
        mixin.resistances.shield.thermal = 0.2
        mixin.resistances.shield.kinetic = 0.4
        mixin.resistances.shield.explosive = 0.5
        profile = Mock(em=25, thermal=6, kinetic=8.333, explosive=1)
        results = mixin.get_ehp(profile)
        self.assertAlmostEqual(results.hull, 12.0529777575)
        self.assertAlmostEqual(results.armor, 95.2760034772)
        self.assertAlmostEqual(results.shield, 685.5506263491)
        self.assertAlmostEqual(results.total, 792.8796075839)

    def test_none_resistance_all(self):
        mixin = self.mixin
        mixin.hp.hull = 10
        mixin.hp.armor = 50
        mixin.hp.shield = 600
        mixin.resistances.hull.em = 0.1
        mixin.resistances.hull.thermal = 0.2
        mixin.resistances.hull.kinetic = 0.3
        mixin.resistances.hull.explosive = 0.4
        mixin.resistances.armor.em = 0.6
        mixin.resistances.armor.thermal = 0.4
        mixin.resistances.armor.kinetic = 0.2
        mixin.resistances.armor.explosive = 0.1
        mixin.resistances.shield.em = None
        mixin.resistances.shield.thermal = None
        mixin.resistances.shield.kinetic = None
        mixin.resistances.shield.explosive = None
        profile = Mock(em=25, thermal=6, kinetic=8.333, explosive=1)
        results = mixin.get_ehp(profile)
        self.assertAlmostEqual(results.hull, 11.956505628)
        self.assertAlmostEqual(results.armor, 95.2760034772)
        self.assertAlmostEqual(results.shield, 600)
        self.assertAlmostEqual(results.total, 707.2325091052)
