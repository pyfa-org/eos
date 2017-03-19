# ===============================================================================
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
# ===============================================================================


from eos import *
from eos.const.eve import Attribute
from tests.integration.restriction.restriction_testcase import RestrictionTestCase


class TestSubsystemIndex(RestrictionTestCase):
    """Check functionality of subsystem slot index restriction"""

    def setUp(self):
        super().setUp()
        self.index_attr = self.ch.attribute(attribute_id=Attribute.subsystem_slot)

    def test_fail(self):
        # Check that if 2 or more items are put into single slot
        # index, error is raised
        fit = Fit()
        item_eve_type = self.ch.type(attributes={self.index_attr.id: 120})
        item1 = Subsystem(item_eve_type.id)
        item2 = Subsystem(item_eve_type.id)
        fit.subsystems.add(item1)
        fit.subsystems.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.subsystem_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.item_slot_index, 120)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.subsystem_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.item_slot_index, 120)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_other_item_class(self):
        # Make sure items of all classes are affected
        fit = Fit()
        item_eve_type = self.ch.type(attributes={self.index_attr.id: 120})
        item1 = ModuleHigh(item_eve_type.id)
        item2 = ModuleHigh(item_eve_type.id)
        fit.modules.high.append(item1)
        fit.modules.high.append(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.subsystem_index)
        # Verification
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.item_slot_index, 120)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.subsystem_index)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.item_slot_index, 120)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass(self):
        # Single item which takes some slot shouldn't
        # trigger any errors
        fit = Fit()
        item = Subsystem(self.ch.type(attributes={self.index_attr.id: 120}).id)
        fit.subsystems.add(item)
        # Action
        restriction_error = self.get_restriction_error(fit, item, Restriction.subsystem_index)
        # Verification
        self.assertIsNone(restriction_error)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_different(self):
        # Items taking different slots shouldn't trigger any errors
        fit = Fit()
        item1 = Subsystem(self.ch.type(attributes={self.index_attr.id: 120}).id)
        item2 = Subsystem(self.ch.type(attributes={self.index_attr.id: 121}).id)
        fit.subsystems.add(item1)
        fit.subsystems.add(item2)
        # Action
        restriction_error1 = self.get_restriction_error(fit, item1, Restriction.subsystem_index)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, item2, Restriction.subsystem_index)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
