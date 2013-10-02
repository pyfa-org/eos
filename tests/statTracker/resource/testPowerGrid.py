from unittest.mock import Mock

from eos.const.eos import Location, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Module, Ship, Implant
from eos.tests.statTracker.statTestCase import StatTestCase


class TestPowergrid(StatTestCase):
    """Check functionality of powergrid stats"""

    def testOutput(self):
        # Check that modified attribute of ship is used
        shipItem = self.ch.type_(typeId=1, attributes={Attribute.powerOutput: 10})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.powerOutput: 50}
        self.setShip(shipHolder)
        self.assertEqual(self.st.powerGrid.output, 50)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoShip(self):
        # None for output when no ship
        self.assertIsNone(self.st.powerGrid.output)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoAttr(self):
        # None for output when no attribute on ship
        shipItem = self.ch.type_(typeId=1)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {}
        self.setShip(shipHolder)
        self.assertIsNone(self.st.powerGrid.output)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseSingle(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder.attributes = {Attribute.power: 50}
        self.trackHolder(holder)
        self.assertEqual(self.st.powerGrid.used, 50)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseMultiple(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.power: 30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.powerGrid.used, 80)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseNegative(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.power: -30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.powerGrid.used, 20)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseNone(self):
        self.assertEqual(self.st.powerGrid.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseState(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2.attributes = {Attribute.power: 30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.powerGrid.used, 50)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseOtherClassLocation(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.power: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.ship, spec_set=Module)
        holder1.attributes = {Attribute.power: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.character, spec_set=Implant)
        holder2.attributes = {Attribute.power: 30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.powerGrid.used, 80)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()
