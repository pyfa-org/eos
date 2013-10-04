from unittest.mock import Mock

from eos.const.eos import Location, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Module, Ship
from eos.tests.statTracker.statTestCase import StatTestCase


class TestMedSlot(StatTestCase):

    def testTotal(self):
        # Check that modified attribute of ship is used
        shipItem = self.ch.type_(typeId=1, attributes={Attribute.medSlots: 2})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.medSlots: 6}
        self.setShip(shipHolder)
        self.assertEqual(self.st.medSlots.total, 6)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoShip(self):
        # None for slot amount when no ship
        self.assertIsNone(self.st.medSlots.total)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoAttr(self):
        # None for slot amount when no attribute on ship
        shipItem = self.ch.type_(typeId=1)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {}
        self.setShip(shipHolder)
        self.assertIsNone(self.st.medSlots.total)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseEmpty(self):
        self.assertEqual(self.st.medSlots.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseMultiple(self):
        item = self.ch.type_(typeId=1, attributes={})
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.med.append(holder1)
        self.fit.modules.med.append(holder2)
        self.assertEqual(self.st.medSlots.used, 2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseMultipleWithNone(self):
        item = self.ch.type_(typeId=1, attributes={})
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.med.append(None)
        self.fit.modules.med.append(holder1)
        self.fit.modules.med.append(None)
        self.fit.modules.med.append(holder2)
        self.assertEqual(self.st.medSlots.used, 4)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseOtherContainer(self):
        item = self.ch.type_(typeId=1, attributes={})
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.fit.modules.low.append(holder)
        self.assertEqual(self.st.medSlots.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()
