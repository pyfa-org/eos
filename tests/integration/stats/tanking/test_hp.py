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


from eos import *
from eos.const.eve import AttributeId
from tests.integration.stats.stat_testcase import StatTestCase


class TestHp(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=AttributeId.hp)
        self.ch.attribute(attribute_id=AttributeId.armor_hp)
        self.ch.attribute(attribute_id=AttributeId.shield_capacity)

    def test_relay(self):
        # Check that stats service relays hp stats properly
        fit = Fit()
        fit.ship = Ship(self.ch.type(
            attributes={AttributeId.hp: 10, AttributeId.armor_hp: 15, AttributeId.shield_capacity: 20}
        ).id)
        # Action
        hp_stats = fit.stats.hp
        # Verification
        self.assertAlmostEqual(hp_stats.hull, 10)
        self.assertAlmostEqual(hp_stats.armor, 15)
        self.assertAlmostEqual(hp_stats.shield, 20)
        self.assertAlmostEqual(hp_stats.total, 45)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_no_ship(self):
        # Check that something sane is returned in case of no ship
        fit = Fit()
        # Action
        hp_stats = fit.stats.hp
        # Verification
        self.assertIsNone(hp_stats.hull)
        self.assertIsNone(hp_stats.armor)
        self.assertIsNone(hp_stats.shield)
        self.assertIsNone(hp_stats.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_no_source(self):
        # Check that stats service relays hp stats properly
        fit = Fit()
        fit.ship = Ship(self.ch.type(
            attributes={AttributeId.hp: 10, AttributeId.armor_hp: 15, AttributeId.shield_capacity: 20}
        ).id)
        fit.source = None
        # Action
        hp_stats = fit.stats.hp
        # Verification
        self.assertIsNone(hp_stats.hull)
        self.assertIsNone(hp_stats.armor)
        self.assertIsNone(hp_stats.shield)
        self.assertIsNone(hp_stats.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
