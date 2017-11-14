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
from eos.const.eve import AttrId
from tests.integration.restriction.restriction_testcase import (
    RestrictionTestCase)


class TestChargeGroup(RestrictionTestCase):
    """Check functionality of charge group restriction."""

    def test_fail_group1(self):
        charge = Charge(self.ch.type(group_id=1008).id)
        container = ModuleHigh(
            self.ch.type(attrs={AttrId.charge_group_1: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.group_id, 1008)
        self.assertCountEqual(restriction_error2.allowed_group_ids, [3])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group2(self):
        charge = Charge(self.ch.type(group_id=1008).id)
        container = ModuleHigh(
            self.ch.type(attrs={AttrId.charge_group_2: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.group_id, 1008)
        self.assertCountEqual(restriction_error2.allowed_group_ids, [3])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group3(self):
        charge = Charge(self.ch.type(group_id=1008).id)
        container = ModuleHigh(
            self.ch.type(attrs={AttrId.charge_group_3: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.group_id, 1008)
        self.assertCountEqual(restriction_error2.allowed_group_ids, [3])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group4(self):
        charge = Charge(self.ch.type(group_id=1008).id)
        container = ModuleHigh(
            self.ch.type(attrs={AttrId.charge_group_4: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.group_id, 1008)
        self.assertCountEqual(restriction_error2.allowed_group_ids, [3])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_group5(self):
        charge = Charge(self.ch.type(group_id=1008).id)
        container = ModuleHigh(
            self.ch.type(attrs={AttrId.charge_group_5: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.group_id, 1008)
        self.assertCountEqual(restriction_error2.allowed_group_ids, [3])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_charge_none(self):
        charge = Charge(self.ch.type(group_id=None).id)
        container = ModuleHigh(
            self.ch.type(attrs={AttrId.charge_group_1: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.group_id, None)
        self.assertCountEqual(restriction_error2.allowed_group_ids, [3])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_multiple_same(self):
        charge = Charge(self.ch.type(group_id=1008).id)
        container = ModuleHigh(
            self.ch.type(attrs={
                AttrId.charge_group_3: 3,
                AttrId.charge_group_5: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.group_id, 1008)
        self.assertCountEqual(restriction_error2.allowed_group_ids, [3])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_multiple_different(self):
        charge = Charge(self.ch.type(group_id=1008).id)
        container = ModuleHigh(
            self.ch.type(attrs={
                AttrId.charge_group_3: 5,
                AttrId.charge_group_5: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.group_id, 1008)
        self.assertCountEqual(restriction_error2.allowed_group_ids, [3, 5])
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_match(self):
        charge = Charge(self.ch.type(group_id=3).id)
        container = ModuleHigh(
            self.ch.type(attrs={AttrId.charge_group_1: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_multiple(self):
        charge = Charge(self.ch.type(group_id=1008).id)
        container = ModuleHigh(
            self.ch.type(attrs={
                AttrId.charge_group_3: 56,
                AttrId.charge_group_5: 1008}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_attr(self):
        charge = Charge(self.ch.type(group_id=1008).id)
        container = ModuleHigh(self.ch.type().id, state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        charge = Charge(self.ch.type(group_id=1008).id)
        container = ModuleHigh(
            self.ch.type(attrs={AttrId.charge_group_1: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        self.fit.source = None
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_group)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
