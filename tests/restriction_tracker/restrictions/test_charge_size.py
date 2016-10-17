# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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

from eos.const.eos import Domain, Restriction, State
from eos.const.eve import Attribute
from eos.fit.holder.item import ModuleHigh, Charge
from tests.restriction_tracker.restriction_testcase import RestrictionTestCase


class TestChargeSize(RestrictionTestCase):
    """Check functionality of charge size restriction"""

    def test_fail_lesser(self):
        charge_item = self.ch.type_(type_id=1, attributes={Attribute.charge_size: 2})
        charge_holder = Mock(state=State.offline, item=charge_item, _domain=None, spec_set=Charge(1))
        container_item = self.ch.type_(type_id=2, attributes={Attribute.charge_size: 3})
        container_holder = Mock(state=State.offline, item=container_item,
                                _domain=Domain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.track_holder(container_holder)
        self.track_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_size)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_size)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.allowed_size, 3)
        self.assertEqual(restriction_error2.holder_size, 2)
        self.untrack_holder(container_holder)
        self.untrack_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_greater(self):
        charge_item = self.ch.type_(type_id=1, attributes={Attribute.charge_size: 2})
        charge_holder = Mock(state=State.offline, item=charge_item, _domain=None, spec_set=Charge(1))
        container_item = self.ch.type_(type_id=2, attributes={Attribute.charge_size: 1})
        container_holder = Mock(state=State.offline, item=container_item,
                                _domain=Domain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.track_holder(container_holder)
        self.track_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_size)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_size)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.allowed_size, 1)
        self.assertEqual(restriction_error2.holder_size, 2)
        self.untrack_holder(container_holder)
        self.untrack_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_charge_no_attrib(self):
        charge_item = self.ch.type_(type_id=1, attributes={})
        charge_holder = Mock(state=State.offline, item=charge_item, _domain=None, spec_set=Charge(1))
        container_item = self.ch.type_(type_id=2, attributes={Attribute.charge_size: 3})
        container_holder = Mock(state=State.offline, item=container_item,
                                _domain=Domain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.track_holder(container_holder)
        self.track_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_size)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_size)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.allowed_size, 3)
        self.assertEqual(restriction_error2.holder_size, None)
        self.untrack_holder(container_holder)
        self.untrack_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_equal(self):
        charge_item = self.ch.type_(type_id=1, attributes={Attribute.charge_size: 2})
        charge_holder = Mock(state=State.offline, item=charge_item, _domain=None, spec_set=Charge(1))
        container_item = self.ch.type_(type_id=2, attributes={Attribute.charge_size: 2})
        container_holder = Mock(state=State.offline, item=container_item,
                                _domain=Domain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.track_holder(container_holder)
        self.track_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_size)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_size)
        self.assertIsNone(restriction_error2)
        self.untrack_holder(container_holder)
        self.untrack_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_original_attribs(self):
        # Make sure original item attributes are used
        charge_item = self.ch.type_(type_id=1, attributes={Attribute.charge_size: 2})
        charge_holder = Mock(state=State.offline, item=charge_item, _domain=None, spec_set=Charge(1))
        charge_holder.attributes = {Attribute.charge_size: 1}
        container_item = self.ch.type_(type_id=2, attributes={Attribute.charge_size: 2})
        container_holder = Mock(state=State.offline, item=container_item,
                                _domain=Domain.ship, spec_set=ModuleHigh(1))
        container_holder.attributes = {Attribute.charge_size: 3}
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.track_holder(container_holder)
        self.track_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_size)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_size)
        self.assertIsNone(restriction_error2)
        self.untrack_holder(container_holder)
        self.untrack_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_no_container_attrib(self):
        charge_item = self.ch.type_(type_id=1, attributes={Attribute.charge_size: 2})
        charge_holder = Mock(state=State.offline, item=charge_item, _domain=None, spec_set=Charge(1))
        container_item = self.ch.type_(type_id=2, attributes={})
        container_holder = Mock(state=State.offline, item=container_item,
                                _domain=Domain.ship, spec_set=ModuleHigh(1))
        container_holder.charge = charge_holder
        charge_holder.container = container_holder
        self.track_holder(container_holder)
        self.track_holder(charge_holder)
        restriction_error1 = self.get_restriction_error(container_holder, Restriction.charge_size)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(charge_holder, Restriction.charge_size)
        self.assertIsNone(restriction_error2)
        self.untrack_holder(container_holder)
        self.untrack_holder(charge_holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
