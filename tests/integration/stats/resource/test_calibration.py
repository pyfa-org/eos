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
from eos.const.eve import AttributeId, EffectId, EffectCategoryId
from tests.integration.stats.stat_testcase import StatTestCase


class TestCalibration(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=AttributeId.upgrade_capacity)
        self.ch.attribute(attribute_id=AttributeId.upgrade_cost)
        self.effect = self.ch.effect(
            effect_id=EffectId.rig_slot, category=EffectCategoryId.passive)

    def test_output(self):
        # Check that modified attribute of ship is used
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.upgrade_capacity: 350}).id)
        # Verification
        self.assertAlmostEqual(self.fit.stats.calibration.output, 350)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_output_no_ship(self):
        # None for output when no ship
        # Verification
        self.assertIsNone(self.fit.stats.calibration.output)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_output_no_attr(self):
        # None for output when no attribute on ship
        self.fit.ship = Ship(self.ch.type().id)
        # Verification
        self.assertIsNone(self.fit.stats.calibration.output)
        # Cleanup
        # Log entry is due to inability to calculate requested attribute
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_single_no_rounding(self):
        self.fit.rigs.add(Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 55.5555555555},
            effects=[self.effect]).id))
        # Verification
        self.assertAlmostEqual(self.fit.stats.calibration.used, 55.5555555555)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_multiple(self):
        self.fit.rigs.add(Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 50},
            effects=[self.effect]).id))
        self.fit.rigs.add(Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 30},
            effects=[self.effect]).id))
        # Verification
        self.assertAlmostEqual(self.fit.stats.calibration.used, 80)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_disabled_effect(self):
        item1 = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 50},
            effects=[self.effect]).id)
        item2 = Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 30},
            effects=[self.effect]).id)
        item2.set_effect_run_mode(self.effect.id, EffectRunMode.force_stop)
        self.fit.rigs.add(item1)
        self.fit.rigs.add(item2)
        # Verification
        self.assertAlmostEqual(self.fit.stats.calibration.used, 50)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_use_none(self):
        # Verification
        self.assertAlmostEqual(self.fit.stats.calibration.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_no_source(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.upgrade_capacity: 350}).id)
        self.fit.rigs.add(Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 50},
            effects=[self.effect]).id))
        self.fit.rigs.add(Rig(self.ch.type(
            attributes={AttributeId.upgrade_cost: 30},
            effects=[self.effect]).id))
        self.fit.source = None
        # Verification
        self.assertAlmostEqual(self.fit.stats.calibration.used, 0)
        self.assertIsNone(self.fit.stats.calibration.output)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
