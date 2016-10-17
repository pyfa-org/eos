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
from eos.fit.holder.item import Drone, Implant
from tests.restriction_tracker.restriction_testcase import RestrictionTestCase


class TestDroneBandwidth(RestrictionTestCase):
    """Check functionality of drone bandwidth restriction"""

    def test_fail_excess_single(self):
        # When ship provides bandwidth output, but single consumer
        # demands for more, error should be raised
        item = self.ch.type_(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        holder = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder.attributes = {Attribute.drone_bandwidth_used: 50}
        self.track_holder(holder)
        self.fit.stats.drone_bandwidth.used = 50
        self.fit.stats.drone_bandwidth.output = 40
        restriction_error = self.get_restriction_error(holder, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.holder_use, 50)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_single_other_class_domain(self):
        # Make sure holders of all classes are affected
        item = self.ch.type_(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        holder = Mock(state=State.online, item=item, _domain=Domain.character, spec_set=Implant(1))
        holder.attributes = {Attribute.drone_bandwidth_used: 50}
        self.track_holder(holder)
        self.fit.stats.drone_bandwidth.used = 50
        self.fit.stats.drone_bandwidth.output = 40
        restriction_error = self.get_restriction_error(holder, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 40)
        self.assertEqual(restriction_error.total_use, 50)
        self.assertEqual(restriction_error.holder_use, 50)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_single_undefined_output(self):
        # When stats module does not specify output, make sure
        # it's assumed to be 0
        item = self.ch.type_(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        holder = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder.attributes = {Attribute.drone_bandwidth_used: 5}
        self.track_holder(holder)
        self.fit.stats.drone_bandwidth.used = 5
        self.fit.stats.drone_bandwidth.output = None
        restriction_error = self.get_restriction_error(holder, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 0)
        self.assertEqual(restriction_error.total_use, 5)
        self.assertEqual(restriction_error.holder_use, 5)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_multiple(self):
        # When multiple consumers require less than bandwidth output
        # alone, but in sum want more than total output, it should
        # be erroneous situation
        item = self.ch.type_(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder1.attributes = {Attribute.drone_bandwidth_used: 25}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder2.attributes = {Attribute.drone_bandwidth_used: 20}
        self.track_holder(holder2)
        self.fit.stats.drone_bandwidth.used = 45
        self.fit.stats.drone_bandwidth.output = 40
        restriction_error1 = self.get_restriction_error(holder1, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 40)
        self.assertEqual(restriction_error1.total_use, 45)
        self.assertEqual(restriction_error1.holder_use, 25)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.output, 40)
        self.assertEqual(restriction_error2.total_use, 45)
        self.assertEqual(restriction_error2.holder_use, 20)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_modified(self):
        # Make sure modified bandwidth values are taken
        item = self.ch.type_(type_id=1, attributes={Attribute.drone_bandwidth_used: 40})
        holder = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder.attributes = {Attribute.drone_bandwidth_used: 100}
        self.track_holder(holder)
        self.fit.stats.drone_bandwidth.used = 100
        self.fit.stats.drone_bandwidth.output = 50
        restriction_error = self.get_restriction_error(holder, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 50)
        self.assertEqual(restriction_error.total_use, 100)
        self.assertEqual(restriction_error.holder_use, 100)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_mix_usage_negative(self):
        # If some holder has negative usage and bandwidth error is
        # still raised, check it's not raised for holder with
        # negative usage
        item = self.ch.type_(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder1.attributes = {Attribute.drone_bandwidth_used: 100}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder2.attributes = {Attribute.drone_bandwidth_used: -10}
        self.track_holder(holder2)
        self.fit.stats.drone_bandwidth.used = 90
        self.fit.stats.drone_bandwidth.output = 50
        restriction_error1 = self.get_restriction_error(holder1, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 90)
        self.assertEqual(restriction_error1.holder_use, 100)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error2)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_mix_usage_zero(self):
        # If some holder has zero usage and bandwidth error is
        # still raised, check it's not raised for holder with
        # zero usage
        item = self.ch.type_(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder1.attributes = {Attribute.drone_bandwidth_used: 100}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder2.attributes = {Attribute.drone_bandwidth_used: 0}
        self.track_holder(holder2)
        self.fit.stats.drone_bandwidth.used = 100
        self.fit.stats.drone_bandwidth.output = 50
        restriction_error1 = self.get_restriction_error(holder1, Restriction.drone_bandwidth)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 100)
        self.assertEqual(restriction_error1.holder_use, 100)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error2)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass(self):
        # When total consumption is less than output,
        # no errors should be raised
        item = self.ch.type_(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder1.attributes = {Attribute.drone_bandwidth_used: 25}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder2.attributes = {Attribute.drone_bandwidth_used: 20}
        self.track_holder(holder2)
        self.fit.stats.drone_bandwidth.used = 45
        self.fit.stats.drone_bandwidth.output = 50
        restriction_error1 = self.get_restriction_error(holder1, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error2)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_no_original_attr(self):
        # When added holder's item doesn't have original attribute,
        # holder shouldn't be tracked by register, and thus, no
        # errors should be raised
        item = self.ch.type_(type_id=1)
        holder = Mock(state=State.online, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder.attributes = {Attribute.drone_bandwidth_used: 100}
        self.track_holder(holder)
        self.fit.stats.drone_bandwidth.used = 100
        self.fit.stats.drone_bandwidth.output = 50
        restriction_error = self.get_restriction_error(holder, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_state(self):
        # When holder isn't online, it shouldn't consume anything
        item = self.ch.type_(type_id=1, attributes={Attribute.drone_bandwidth_used: 0})
        holder = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder.attributes = {Attribute.drone_bandwidth_used: 50}
        self.track_holder(holder)
        self.fit.stats.drone_bandwidth.used = 50
        self.fit.stats.drone_bandwidth.output = 40
        restriction_error = self.get_restriction_error(holder, Restriction.drone_bandwidth)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
