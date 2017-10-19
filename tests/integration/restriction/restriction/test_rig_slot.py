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
from tests.integration.restriction.restriction_testcase import (
    RestrictionTestCase)


class TestRigSlot(RestrictionTestCase):
    """Check functionality of rig slot amount restriction."""

    def setUp(self):
        super().setUp()
        self.ch.attr(attribute_id=AttributeId.rig_slots)
        self.effect = self.ch.effect(
            effect_id=EffectId.rig_slot, category=EffectCategoryId.passive)

    def test_fail_excess_single(self):
        # Check that error is raised when number of used slots exceeds slot
        # amount provided by ship
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.rig_slots: 0}).id)
        item = Rig(self.ch.type(effects=[self.effect]).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.rig_slot)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.slots_max_allowed, 0)
        self.assertEqual(restriction_error.slots_used, 1)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_single_no_ship(self):
        # When stats module does not specify total slot amount, make sure it's
        # assumed to be 0
        item = Rig(self.ch.type(effects=[self.effect]).id)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.rig_slot)
        # Verification
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.slots_max_allowed, 0)
        self.assertEqual(restriction_error.slots_used, 1)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_multiple(self):
        # Check that error works for multiple items
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.rig_slots: 1}).id)
        eve_type = self.ch.type(effects=[self.effect])
        item1 = Rig(eve_type.id)
        item2 = Rig(eve_type.id)
        self.fit.rigs.add(item1)
        self.fit.rigs.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.rig_slot)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.slots_max_allowed, 1)
        self.assertEqual(restriction_error1.slots_used, 2)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.rig_slot)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.slots_max_allowed, 1)
        self.assertEqual(restriction_error2.slots_used, 2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_equal(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.rig_slots: 2}).id)
        eve_type = self.ch.type(effects=[self.effect])
        item1 = Rig(eve_type.id)
        item2 = Rig(eve_type.id)
        self.fit.rigs.add(item1)
        self.fit.rigs.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.rig_slot)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.rig_slot)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_greater(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.rig_slots: 5}).id)
        eve_type = self.ch.type(effects=[self.effect])
        item1 = Rig(eve_type.id)
        item2 = Rig(eve_type.id)
        self.fit.rigs.add(item1)
        self.fit.rigs.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(
            item1, Restriction.rig_slot)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            item2, Restriction.rig_slot)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_disabled_effect(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.rig_slots: 0}).id)
        item = Rig(self.ch.type(effects=[self.effect]).id)
        item.set_effect_run_mode(self.effect.id, EffectRunMode.force_stop)
        self.fit.rigs.add(item)
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.rig_slot)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        self.fit.ship = Ship(self.ch.type(
            attributes={AttributeId.rig_slots: 0}).id)
        item = Rig(self.ch.type(effects=[self.effect]).id)
        self.fit.rigs.add(item)
        self.fit.source = None
        # Action
        restriction_error = self.get_restriction_error(
            item, Restriction.rig_slot)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
