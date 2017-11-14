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
from eos.const.eos import ModDomain, ModOperator, ModTgtFilter
from eos.const.eve import AttrId, EffectCategoryId
from tests.integration.stats.stats_testcase import StatsTestCase


class TestDroneBayVolume(StatsTestCase):

    def setUp(self):
        StatsTestCase.setUp(self)
        self.ch.attr(attr_id=AttrId.drone_capacity)
        self.ch.attr(attr_id=AttrId.volume)

    def test_output(self):
        # Check that modified attribute of ship is used
        src_attr = self.ch.attr()
        modifier = self.mod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=AttrId.drone_capacity,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        mod_effect = self.ch.effect(
            category_id=EffectCategoryId.passive, modifiers=[modifier])
        self.fit.ship = Ship(self.ch.type(
            attrs={AttrId.drone_capacity: 200, src_attr.id: 2},
            effects=[mod_effect]).id)
        # Verification
        self.assertAlmostEqual(self.fit.stats.dronebay.output, 400)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_output_no_ship(self):
        # None for output when no ship
        # Verification
        self.assertIsNone(self.fit.stats.dronebay.output)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_output_no_attr(self):
        # None for output when no attribute on ship
        self.fit.ship = Ship(self.ch.type().id)
        # Verification
        self.assertIsNone(self.fit.stats.dronebay.output)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_single_no_rounding(self):
        self.fit.drones.add(Drone(self.ch.type(
            attrs={AttrId.volume: 55.5555555555}).id))
        # Verification
        self.assertAlmostEqual(self.fit.stats.dronebay.used, 55.5555555555)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_multiple(self):
        self.fit.drones.add(Drone(self.ch.type(
            attrs={AttrId.volume: 50}).id))
        self.fit.drones.add(Drone(self.ch.type(
            attrs={AttrId.volume: 30}).id))
        # Verification
        self.assertAlmostEqual(self.fit.stats.dronebay.used, 80)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_use_none(self):
        # Verification
        self.assertAlmostEqual(self.fit.stats.dronebay.used, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_source(self):
        self.fit.ship = Ship(self.ch.type(
            attrs={AttrId.drone_capacity: 200}).id)
        self.fit.drones.add(Drone(self.ch.type(
            attrs={AttrId.volume: 50}).id))
        self.fit.drones.add(Drone(self.ch.type(
            attrs={AttrId.volume: 30}).id))
        self.fit.source = None
        # Verification
        self.assertAlmostEqual(self.fit.stats.dronebay.used, 0)
        self.assertIsNone(self.fit.stats.dronebay.output)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
