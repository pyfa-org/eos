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


class TestChargeSize(RestrictionTestCase):
    """Check functionality of charge size restriction"""

    def test_fail_lesser(self):
        fit = Fit()
        charge_item = Charge(self.ch.type(attributes={Attribute.charge_size: 2}).id)
        container_item = ModuleHigh(self.ch.type(attributes={Attribute.charge_size: 3}).id, state=State.offline)
        container_item.charge = charge_item
        fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(fit, container_item, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, charge_item, Restriction.charge_size)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.allowed_size, 3)
        self.assertEqual(restriction_error2.item_size, 2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_greater(self):
        fit = Fit()
        charge_item = Charge(self.ch.type(attributes={Attribute.charge_size: 2}).id)
        container_item = ModuleHigh(self.ch.type(attributes={Attribute.charge_size: 1}).id, state=State.offline)
        container_item.charge = charge_item
        fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(fit, container_item, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, charge_item, Restriction.charge_size)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.allowed_size, 1)
        self.assertEqual(restriction_error2.item_size, 2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_fail_charge_no_attrib(self):
        fit = Fit()
        charge_item = Charge(self.ch.type().id)
        container_item = ModuleHigh(self.ch.type(attributes={Attribute.charge_size: 3}).id, state=State.offline)
        container_item.charge = charge_item
        fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(fit, container_item, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, charge_item, Restriction.charge_size)
        # Verification
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.allowed_size, 3)
        self.assertEqual(restriction_error2.item_size, None)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_equal(self):
        fit = Fit()
        charge_item = Charge(self.ch.type(attributes={Attribute.charge_size: 2}).id)
        container_item = ModuleHigh(self.ch.type(attributes={Attribute.charge_size: 2}).id, state=State.offline)
        container_item.charge = charge_item
        fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(fit, container_item, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, charge_item, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_no_container_attrib(self):
        fit = Fit()
        charge_item = Charge(self.ch.type(attributes={Attribute.charge_size: 2}).id)
        container_item = ModuleHigh(self.ch.type().id, state=State.offline)
        container_item.charge = charge_item
        fit.modules.high.append(container_item)
        # Action
        restriction_error1 = self.get_restriction_error(fit, container_item, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, charge_item, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_pass_no_source(self):
        fit = Fit()
        charge_item = Charge(self.ch.type(attributes={Attribute.charge_size: 2}).id)
        container_item = ModuleHigh(self.ch.type(attributes={Attribute.charge_size: 3}).id, state=State.offline)
        container_item.charge = charge_item
        fit.modules.high.append(container_item)
        fit.source = None
        # Action
        restriction_error1 = self.get_restriction_error(fit, container_item, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error1)
        # Action
        restriction_error2 = self.get_restriction_error(fit, charge_item, Restriction.charge_size)
        # Verification
        self.assertIsNone(restriction_error2)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)
