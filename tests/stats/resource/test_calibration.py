from unittest.mock import Mock

from eos.const.eos import Domain, State
from eos.const.eve import Attribute
from eos.fit.holder.item import ModuleHigh, Ship, Implant
from tests.stat_tracker.stat_testcase import StatTestCase


class TestCalibration(StatTestCase):
    """Check functionality of calibration stats"""

    def test_output(self):
        # Check that modified attribute of ship is used
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_capacity: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.upgrade_capacity: 50}
        self.set_ship(ship_holder)
        self.assertEqual(self.st.calibration.output, 50)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_ship(self):
        # None for output when no ship
        self.assertIsNone(self.st.calibration.output)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_output_no_attr(self):
        # None for output when no attribute on ship
        ship_item = self.ch.type_(type_id=1)
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {}
        self.set_ship(ship_holder)
        self.assertIsNone(self.st.calibration.output)
        self.set_ship(None)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_single_no_rounding(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder.attributes = {Attribute.upgrade_cost: 55.5555555555}
        self.track_holder(holder)
        self.assertEqual(self.st.calibration.used, 55.5555555555)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_multiple(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.upgrade_cost: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.upgrade_cost: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.calibration.used, 80)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_negative(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.upgrade_cost: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.upgrade_cost: -30}
        self.track_holder(holder2)
        self.assertEqual(self.st.calibration.used, 20)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_none(self):
        self.assertEqual(self.st.calibration.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_use_other_class_domain(self):
        item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_cost: 0})
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.upgrade_cost: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.character, spec_set=Implant(1))
        holder2.attributes = {Attribute.upgrade_cost: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.calibration.used, 80)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_cache(self):
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_capacity: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.upgrade_capacity: 50}
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=2, attributes={Attribute.upgrade_cost: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.upgrade_cost: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.upgrade_cost: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.calibration.used, 80)
        self.assertEqual(self.st.calibration.output, 50)
        holder1.attributes[Attribute.upgrade_cost] = 10
        ship_holder.attributes[Attribute.upgrade_capacity] = 60
        self.assertEqual(self.st.calibration.used, 80)
        self.assertEqual(self.st.calibration.output, 50)
        self.set_ship(None)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()

    def test_volatility(self):
        ship_item = self.ch.type_(type_id=1, attributes={Attribute.upgrade_capacity: 10})
        ship_holder = Mock(state=State.offline, item=ship_item, _domain=None, spec_set=Ship(1))
        ship_holder.attributes = {Attribute.upgrade_capacity: 50}
        self.set_ship(ship_holder)
        item = self.ch.type_(type_id=2, attributes={Attribute.upgrade_cost: 0})
        holder1 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder1.attributes = {Attribute.upgrade_cost: 50}
        self.track_holder(holder1)
        holder2 = Mock(state=State.online, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2.attributes = {Attribute.upgrade_cost: 30}
        self.track_holder(holder2)
        self.assertEqual(self.st.calibration.used, 80)
        self.assertEqual(self.st.calibration.output, 50)
        holder1.attributes[Attribute.upgrade_cost] = 10
        ship_holder.attributes[Attribute.upgrade_capacity] = 60
        self.st._clear_volatile_attrs()
        self.assertEqual(self.st.calibration.used, 40)
        self.assertEqual(self.st.calibration.output, 60)
        self.set_ship(None)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_stat_buffers_empty()
