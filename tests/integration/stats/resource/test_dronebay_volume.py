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
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import AttributeId, EffectCategoryId
from tests.integration.stats.stat_testcase import StatTestCase


class TestDroneBayVolume(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=AttributeId.drone_capacity)
        self.ch.attribute(attribute_id=AttributeId.volume)

    def test_output(self):
        # Check that modified attribute of ship is used
        src_attr = self.ch.attribute()
        modifier = self.mod(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=AttributeId.drone_capacity,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id)
        mod_effect = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier])
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.drone_capacity: 200, src_attr.id: 2},
            effects=[mod_effect]).id)
        # Verification
        self.assertAlmostEqual(self.fit.stats.dronebay.output, 400)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_output_no_ship(self):
        # None for output when no ship
        # Verification
        self.assertIsNone(self.fit.stats.dronebay.output)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_output_no_attr(self):
        # None for output when no attribute on ship
        self.fit.ship = Ship(self.ch.type().id)
        # Verification
        self.assertIsNone(self.fit.stats.dronebay.output)
        # Cleanup
        # Log entry is due to inability to calculate requested attribute
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_single_no_rounding(self):
        self.fit.drones.add(Drone(self.ch.type(
            attributes={AttributeId.volume: 55.5555555555}).id))
        # Verification
        self.assertAlmostEqual(self.fit.stats.dronebay.used, 55.5555555555)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_multiple(self):
        self.fit.drones.add(Drone(self.ch.type(
            attributes={AttributeId.volume: 50}).id))
        self.fit.drones.add(Drone(self.ch.type(
            attributes={AttributeId.volume: 30}).id))
        # Verification
        self.assertAlmostEqual(self.fit.stats.dronebay.used, 80)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_none(self):
        # Verification
        self.assertAlmostEqual(self.fit.stats.dronebay.used, 0)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_no_source(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.drone_capacity: 200}).id)
        self.fit.drones.add(Drone(self.ch.type(
            attributes={AttributeId.volume: 50}).id))
        self.fit.drones.add(Drone(self.ch.type(
            attributes={AttributeId.volume: 30}).id))
        self.fit.source = None
        # Verification
        self.assertAlmostEqual(self.fit.stats.dronebay.used, 0)
        self.assertIsNone(self.fit.stats.dronebay.output)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
