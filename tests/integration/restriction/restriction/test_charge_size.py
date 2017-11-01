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


class TestChargeSize(RestrictionTestCase):
    """Check functionality of charge size restriction."""

    def test_fail_lesser(self):
        charge = Charge(self.ch.type(
            attributes={AttributeId.charge_size: 2}).id)
        container = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_size: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_size)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.allowed_size, 3)
        self.assertEqual(restriction_error2.size, 2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_greater(self):
        charge = Charge(self.ch.type(
            attributes={AttributeId.charge_size: 2}).id)
        container = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_size: 1}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_size)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.allowed_size, 1)
        self.assertEqual(restriction_error2.size, 2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_charge_no_attrib(self):
        charge = Charge(self.ch.type().id)
        container = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_size: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_size)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.allowed_size, 3)
        self.assertEqual(restriction_error2.size, None)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_equal(self):
        charge = Charge(self.ch.type(
            attributes={AttributeId.charge_size: 2}).id)
        container = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_size: 2}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_container_attrib(self):
        charge = Charge(self.ch.type(
            attributes={AttributeId.charge_size: 2}).id)
        container = ModuleHigh(self.ch.type().id, state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        charge = Charge(self.ch.type(
            attributes={AttributeId.charge_size: 2}).id)
        container = ModuleHigh(
            self.ch.type(attributes={AttributeId.charge_size: 3}).id,
            state=State.offline)
        container.charge = charge
        self.fit.modules.high.append(container)
        self.fit.source = None
        # Action
        restriction_error1 = self.get_restriction_error(
            container, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(
            charge, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
