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
from tests.integration.restriction.restriction_testcase import (
    RestrictionTestCase)


class TestChargeGroup(RestrictionTestCase):
    """Check functionality of charge group restriction."""

    def test_fail_group1(self):
        charge_item = Charge(self.ch.type(group=1008).id)
        container_item = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_group_1: 3}).id,
            state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.charge_group, 1008)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group2(self):
        charge_item = Charge(self.ch.type(group=1008).id)
        container_item = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_group_2: 3}).id,
            state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.charge_group, 1008)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group3(self):
        charge_item = Charge(self.ch.type(group=1008).id)
        container_item = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_group_3: 3}).id,
            state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.charge_group, 1008)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group4(self):
        charge_item = Charge(self.ch.type(group=1008).id)
        container_item = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_group_4: 3}).id,
            state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.charge_group, 1008)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group5(self):
        charge_item = Charge(self.ch.type(group=1008).id)
        container_item = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_group_5: 3}).id,
            state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.charge_group, 1008)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_charge_none(self):
        charge_item = Charge(self.ch.type(group=None).id)
        container_item = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_group_1: 3}).id,
            state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.charge_group, None)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_multiple_same(self):
        charge_item = Charge(self.ch.type(group=1008).id)
        container_item = ModuleHigh(
            self.ch.type(attributes={
                AttributeId.charge_group_3: 3,
                AttributeId.charge_group_5: 3}).id,
            state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.charge_group, 1008)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_multiple_different(self):
        charge_item = Charge(self.ch.type(group=1008).id)
        container_item = ModuleHigh(
            self.ch.type(attributes={
                AttributeId.charge_group_3: 5,
                AttributeId.charge_group_5: 3}).id,
            state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 2)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertIn(5, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.charge_group, 1008)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_match(self):
        charge_item = Charge(self.ch.type(group=3).id)
        container_item = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_group_1: 3}).id,
            state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_multiple(self):
        charge_item = Charge(self.ch.type(group=1008).id)
        container_item = ModuleHigh(
            self.ch.type(attributes={
                AttributeId.charge_group_3: 56,
                AttributeId.charge_group_5: 1008}).id,
            state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_attr(self):
        charge_item = Charge(self.ch.type(group=1008).id)
        container_item = ModuleHigh(self.ch.type().id, state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        charge_item = Charge(self.ch.type(group=1008).id)
        container_item = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_group_1: 3}).id,
            state=State.offline)
        container_item.charge = charge_item
        self.fit.modules.high.append(container_item)
        self.fit.source = None
        # Action
        restriction_error1 = self.get_restriction_error(
            container_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge_item, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
