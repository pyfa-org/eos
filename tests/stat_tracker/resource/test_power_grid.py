from unittest.mock import Mock

from eos.const.eos import Location, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Module, Ship, Implant
from eos.tests.stat_tracker.stat_testcase import StatTestCase


class TestPowergrid(StatTestCase):
    """Check functionality of powergrid stats"""

    def test_output(self):
        # Check that modified attribute of ship is used
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.power_output: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _location=None, spec_set=Ship)
        ship_holder.attributes = {Attribute.power_output: 50}
        self.set_ship(ship_holder)
        self.assertEqual(self.st.powergrid.output, 50)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_ship(self):
        # None for output when no ship
        self.assertIsNone(self.st.powergrid.output)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_attr(self):
        # None for output when no attribute on ship
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _location=None, spec_set=Ship)
        ship_holder.attributes = {}
        self.set_ship(ship_holder)
        self.assertIsNone(self.st.powergrid.output)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder.attributes = {Attribute.power: 50}
        self.track_holder(holder)
        self.assertEqual(self.st.powergrid.used, 50)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.power: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.powergrid.used, 80)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_negative(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.power: -30}
        self.track_holder(holder2)
        self.assertEqual(self.st.powergrid.used, 20)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_none(self):
        self.assertEqual(self.st.powergrid.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_state(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.power: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.powergrid.used, 50)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_other_class_location(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.character, spec_set=Implant)
        holder2.attributes = {Attribute.power: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.powergrid.used, 80)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
