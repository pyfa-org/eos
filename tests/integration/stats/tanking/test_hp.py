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


from eos import Ship
from eos.const.eve import AttrId
from tests.integration.stats.testcase import StatsTestCase


class TestHp(StatsTestCase):

    def setUp(self):
        StatsTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.hp)
        self.mkattr(attr_id=AttrId.armor_hp)
        self.mkattr(attr_id=AttrId.shield_capacity)

    def test_relay(self):
        # Check that stats service relays hp stats properly
        self.fit.ship = Ship(self.mktype(attrs={
            AttrId.hp: 10,
            AttrId.armor_hp: 15,
            AttrId.shield_capacity: 20}).id)
        # Action
        hp_stats = self.fit.stats.hp
        # Verification
        self.assertAlmostEqual(hp_stats.hull, 10)
        self.assertAlmostEqual(hp_stats.armor, 15)
        self.assertAlmostEqual(hp_stats.shield, 20)
        self.assertAlmostEqual(hp_stats.total, 45)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_ship(self):
        # Check that something sane is returned in case of no ship
        # Action
        hp_stats = self.fit.stats.hp
        # Verification
        self.assertAlmostEqual(hp_stats.hull, 0)
        self.assertAlmostEqual(hp_stats.armor, 0)
        self.assertAlmostEqual(hp_stats.shield, 0)
        self.assertAlmostEqual(hp_stats.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        # Check that stats service relays hp stats properly
        self.fit.ship = Ship(self.mktype(attrs={
            AttrId.hp: 10,
            AttrId.armor_hp: 15,
            AttrId.shield_capacity: 20}).id)
        self.fit.source = None
        # Action
        hp_stats = self.fit.stats.hp
        # Verification
        self.assertAlmostEqual(hp_stats.hull, 0)
        self.assertAlmostEqual(hp_stats.armor, 0)
        self.assertAlmostEqual(hp_stats.shield, 0)
        self.assertAlmostEqual(hp_stats.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
