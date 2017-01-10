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
from eos.fit.holder.item import Drone
from tests.restriction_tracker.restriction_testcase import RestrictionTestCase


class TestDroneBayVolume(RestrictionTestCase):
    """Check functionality of drone bay volume restriction"""

    def test_fail_excess_single(self):
        # When ship provides drone bay volume, but single consumer
        # demands for more, error should be raised
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 0})
        holder = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder.attributes = {Attribute.volume: 50}
        self.fit.drones.add(holder)
        self.track_holder(holder)
        self.fit.stats.dronebay.used = 50
        self.fit.stats.dronebay.output = 40
        restriction_error = self.get_restriction_error(holder, Restriction.dronebay_volume)
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
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 0})
        holder = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder.attributes = {Attribute.volume: 5}
        self.fit.drones.add(holder)
        self.track_holder(holder)
        self.fit.stats.dronebay.used = 5
        self.fit.stats.dronebay.output = None
        restriction_error = self.get_restriction_error(holder, Restriction.dronebay_volume)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 0)
        self.assertEqual(restriction_error.total_use, 5)
        self.assertEqual(restriction_error.holder_use, 5)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_multiple(self):
        # When multiple consumers require less than drone bay volume
        # alone, but in sum want more than total output, it should
        # be erroneous situation
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 0})
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder1.attributes = {Attribute.volume: 25}
        self.fit.drones.add(holder1)
        self.track_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder2.attributes = {Attribute.volume: 20}
        self.fit.drones.add(holder2)
        self.track_holder(holder2)
        self.fit.stats.dronebay.used = 45
        self.fit.stats.dronebay.output = 40
        restriction_error1 = self.get_restriction_error(holder1, Restriction.dronebay_volume)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 40)
        self.assertEqual(restriction_error1.total_use, 45)
        self.assertEqual(restriction_error1.holder_use, 25)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.dronebay_volume)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.output, 40)
        self.assertEqual(restriction_error2.total_use, 45)
        self.assertEqual(restriction_error2.holder_use, 20)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_excess_modified(self):
        # Make sure modified volume values are taken
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 40})
        holder = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder.attributes = {Attribute.volume: 100}
        self.fit.drones.add(holder)
        self.track_holder(holder)
        self.fit.stats.dronebay.used = 100
        self.fit.stats.dronebay.output = 50
        restriction_error = self.get_restriction_error(holder, Restriction.dronebay_volume)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.output, 50)
        self.assertEqual(restriction_error.total_use, 100)
        self.assertEqual(restriction_error.holder_use, 100)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_mix_usage_negative(self):
        # If some holder has negative usage and drone bay error is
        # still raised, check it's not raised for holder with
        # negative usage
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 0})
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder1.attributes = {Attribute.volume: 100}
        self.fit.drones.add(holder1)
        self.track_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder2.attributes = {Attribute.volume: -10}
        self.fit.drones.add(holder2)
        self.track_holder(holder2)
        self.fit.stats.dronebay.used = 90
        self.fit.stats.dronebay.output = 50
        restriction_error1 = self.get_restriction_error(holder1, Restriction.dronebay_volume)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 90)
        self.assertEqual(restriction_error1.holder_use, 100)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.dronebay_volume)
        self.assertIsNone(restriction_error2)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_mix_usage_zero(self):
        # If some holder has zero usage and drone bay error is
        # still raised, check it's not raised for holder with
        # zero usage
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 0})
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder1.attributes = {Attribute.volume: 100}
        self.fit.drones.add(holder1)
        self.track_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder2.attributes = {Attribute.volume: 0}
        self.fit.drones.add(holder2)
        self.track_holder(holder2)
        self.fit.stats.dronebay.used = 100
        self.fit.stats.dronebay.output = 50
        restriction_error1 = self.get_restriction_error(holder1, Restriction.dronebay_volume)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.output, 50)
        self.assertEqual(restriction_error1.total_use, 100)
        self.assertEqual(restriction_error1.holder_use, 100)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.dronebay_volume)
        self.assertIsNone(restriction_error2)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass(self):
        # When total consumption is less than output,
        # no errors should be raised
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 0})
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder1.attributes = {Attribute.volume: 25}
        self.fit.drones.add(holder1)
        self.track_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder2.attributes = {Attribute.volume: 20}
        self.fit.drones.add(holder2)
        self.track_holder(holder2)
        self.fit.stats.dronebay.used = 45
        self.fit.stats.dronebay.output = 50
        restriction_error1 = self.get_restriction_error(holder1, Restriction.dronebay_volume)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.dronebay_volume)
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
        holder = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder.attributes = {Attribute.volume: 100}
        self.fit.drones.add(holder)
        self.track_holder(holder)
        self.fit.stats.dronebay.used = 100
        self.fit.stats.dronebay.output = 50
        restriction_error = self.get_restriction_error(holder, Restriction.dronebay_volume)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_other_container(self):
        # Make sure holders placed to other containers are unaffected
        item = self.ch.type_(type_id=1, attributes={Attribute.volume: 0})
        holder = Mock(state=State.offline, item=item, _domain=Domain.space, spec_set=Drone(1))
        holder.attributes = {Attribute.volume: 50}
        self.fit.rigs.add(holder)
        self.track_holder(holder)
        self.fit.stats.dronebay.used = 50
        self.fit.stats.dronebay.output = 40
        restriction_error = self.get_restriction_error(holder, Restriction.dronebay_volume)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
