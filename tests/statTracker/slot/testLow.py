from unittest.mock import Mock

from eos.const.eos import Location, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Module, Ship
from eos.tests.statTracker.statTestCase import StatTestCase


class TestLowSlot(StatTestCase):

    def testTotal(self):
        # Check that modified attribute of ship is used
        shipItem = self.ch.type_(typeId=1, attributes={Attribute.lowSlots: 2})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.lowSlots: 6}
        self.setShip(shipHolder)
        self.assertEqual(self.st.lowSlots.total, 6)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoShip(self):
        # None for slot amount when no ship
        self.assertIsNone(self.st.lowSlots.total)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoAttr(self):
        # None for slot amount when no attribute on ship
        shipItem = self.ch.type_(typeId=1)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {}
        self.setShip(shipHolder)
        self.assertIsNone(self.st.lowSlots.total)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseEmpty(self):
        self.assertEqual(self.st.lowSlots.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseMultiple(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.upgradeCost: 0})
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.low.append(holder1)
        self.fit.modules.low.append(holder2)
        self.assertEqual(self.st.lowSlots.used, 2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseMultipleWithNone(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.upgradeCost: 0})
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.low.append(None)
        self.fit.modules.low.append(holder1)
        self.fit.modules.low.append(None)
        self.fit.modules.low.append(holder2)
        self.assertEqual(self.st.lowSlots.used, 4)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseOtherContainer(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.upgradeCost: 0})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.high.append(holder)
        self.assertEqual(self.st.lowSlots.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()
