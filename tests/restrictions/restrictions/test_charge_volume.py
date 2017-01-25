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


from eos.const.eos import Restriction, State
from eos.const.eve import Attribute
from eos.fit.item import ModuleHigh, Charge
from tests.restrictions.restriction_testcase import RestrictionTestCase


class TestChargeVolume(RestrictionTestCase):
    """Check functionality of charge volume restriction"""

    def test_fail_greater(self):
        charge_eve_type = self.ch.type_(type_id=1, attributes={Attribute.volume: 2})
        charge_holder = self.make_item_mock(Charge, charge_eve_type)
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.capacity: 1})
        container_holder = self.make_item_mock(ModuleHigh, container_eve_type, state=State.offline)
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_volume)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_volume)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.max_allowed_volume, 1)
        self.assertEqual(restriction_error2.holder_volume, 2)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_no_capacity(self):
        charge_eve_type = self.ch.type_(type_id=1, attributes={Attribute.volume: 2})
        charge_holder = self.make_item_mock(Charge, charge_eve_type)
        container_eve_type = self.ch.type_(type_id=2, attributes={})
        container_holder = self.make_item_mock(ModuleHigh, container_eve_type, state=State.offline)
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_volume)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_volume)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.max_allowed_volume, 0)
        self.assertEqual(restriction_error2.holder_volume, 2)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_no_volume(self):
        charge_eve_type = self.ch.type_(type_id=1, attributes={})
        charge_holder = self.make_item_mock(Charge, charge_eve_type)
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.volume: 3})
        container_holder = self.make_item_mock(ModuleHigh, container_eve_type, state=State.offline)
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_volume)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_volume)
        self.assertIsNone(restriction_error2)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_equal(self):
        charge_eve_type = self.ch.type_(type_id=1, attributes={Attribute.capacity: 2})
        charge_holder = self.make_item_mock(Charge, charge_eve_type)
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.volume: 2})
        container_holder = self.make_item_mock(ModuleHigh, container_eve_type, state=State.offline)
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_volume)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_volume)
        self.assertIsNone(restriction_error2)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_lesser(self):
        charge_eve_type = self.ch.type_(type_id=1, attributes={Attribute.volume: 2})
        charge_holder = self.make_item_mock(Charge, charge_eve_type)
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.capacity: 3})
        container_holder = self.make_item_mock(ModuleHigh, container_eve_type, state=State.offline)
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_volume)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_volume)
        self.assertIsNone(restriction_error2)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_attrs_eve_type(self):
        # Make sure EVE type attributes are used
        charge_eve_type = self.ch.type_(type_id=1, attributes={Attribute.volume: 2})
        charge_holder = self.make_item_mock(Charge, charge_eve_type)
        charge_holder.attributes = {Attribute.volume: 3}
        container_eve_type = self.ch.type_(type_id=2, attributes={Attribute.capacity: 2})
        container_holder = self.make_item_mock(ModuleHigh, container_eve_type, state=State.offline)
        container_holder.attributes = {Attribute.capacity: 1}
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.add_holder(container_holder)
        self.add_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_volume)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_volume)
        self.assertIsNone(restriction_error2)
        self.remove_holder(container_holder)
        self.remove_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
