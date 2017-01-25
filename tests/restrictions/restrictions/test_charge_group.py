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


from unittest.mock import Mock

from eos.const.eos import ModifierDomain, Restriction, State
from eos.const.eve import Attribute
from eos.fit.item import ModuleHigh, Charge
from tests.restrictions.restriction_testcase import RestrictionTestCase


class TestChargeGroup(RestrictionTestCase):
    """Check functionality of charge group restriction"""

    def test_fail_group1(self):
        charge_eve_type = self.ch.type_(type_id=1, group=1008)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.charge_group_1: 3})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.holder_group, 1008)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group2(self):
        charge_eve_type = self.ch.type_(type_id=1, group=1008)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.charge_group_2: 3})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.holder_group, 1008)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group3(self):
        charge_eve_type = self.ch.type_(type_id=1, group=1008)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.charge_group_3: 3})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.holder_group, 1008)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group4(self):
        charge_eve_type = self.ch.type_(type_id=1, group=1008)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.charge_group_4: 3})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.holder_group, 1008)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_group5(self):
        charge_eve_type = self.ch.type_(type_id=1, group=1008)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.charge_group_5: 3})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.holder_group, 1008)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_charge_none(self):
        charge_eve_type = self.ch.type_(type_id=1, group=None)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.charge_group_1: 3})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.holder_group, None)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_multiple_same(self):
        charge_eve_type = self.ch.type_(type_id=1, group=1008)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(
            type_id=2, attributes={Attribute.charge_group_3: 3, Attribute.charge_group_5: 3})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.holder_group, 1008)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_multiple_different(self):
        charge_eve_type = self.ch.type_(type_id=1, group=1008)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(
            type_id=2, attributes={Attribute.charge_group_3: 5, Attribute.charge_group_5: 3})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 2)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertIn(5, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.holder_group, 1008)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_attr_eve_type(self):
        charge_eve_type = self.ch.type_(type_id=1, group=1008)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.charge_group_1: 3})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.attributes = {Attribute.charge_group_1: 1008}
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(len(restriction_error2.allowed_groups), 1)
        self.assertIn(3, restriction_error2.allowed_groups)
        self.assertEqual(restriction_error2.holder_group, 1008)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_match(self):
        charge_eve_type = self.ch.type_(type_id=1, group=3)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.charge_group_1: 3})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error2)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_multiple(self):
        charge_eve_type = self.ch.type_(type_id=1, group=1008)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(
            type_id=2, attributes={Attribute.charge_group_3: 56, Attribute.charge_group_5: 1008})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error2)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_no_attr(self):
        charge_eve_type = self.ch.type_(type_id=1, group=1008)
        charge_holder = Mock(state=State.offline, _eve_type=charge_eve_type, _domain=None, spec_set=Charge(1))
        container_eve_type = self.ch.type_(type_id=2, attributes={})
        container_holder = Mock(
            state=State.offline, _eve_type=container_eve_type, _domain=ModifierDomain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_group)
        self.assertIsNone(restriction_error2)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
