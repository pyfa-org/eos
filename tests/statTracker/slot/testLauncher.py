from unittest.mock import Mock

from eos.const.eos import Location, Slot, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Module, Ship
from eos.tests.statTracker.statTestCase import StatTestCase


class TestLauncherSlot(StatTestCase):

    def testTotal(self):
        # Check that modified attribute of ship is used
        shipItem = self.ch.type_(typeId=1, attributes={Attribute.launcherSlotsLeft: 2})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.launcherSlotsLeft: 6}
        self.setShip(shipHolder)
        self.assertEqual(self.st.launcherSlots.total, 6)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoShip(self):
        # None for slot amount when no ship
        self.assertIsNone(self.st.launcherSlots.total)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoAttr(self):
        # None for slot amount when no attribute on ship
        shipItem = self.ch.type_(typeId=1)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {}
        self.setShip(shipHolder)
        self.assertIsNone(self.st.launcherSlots.total)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseEmpty(self):
        self.assertEqual(self.st.launcherSlots.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseSingle(self):
        item = self.ch.type_(typeId=1, attributes={})
        item.slots = {Slot.launcher}
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        self.assertEqual(self.st.launcherSlots.used, 1)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseOtherSlot(self):
        item = self.ch.type_(typeId=1, attributes={})
        item.slots = {Slot.turret}
        holder = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder)
        self.assertEqual(self.st.launcherSlots.used, 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseMultiple(self):
        item = self.ch.type_(typeId=1, attributes={})
        item.slots = {Slot.launcher}
        holder1 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        holder2 = Mock(state=State.offline, item=item, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        self.trackHolder(holder2)
        self.assertEqual(self.st.launcherSlots.used, 2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseMixed(self):
        item1 = self.ch.type_(typeId=1, attributes={})
        item1.slots = {Slot.launcher}
        holder1 = Mock(state=State.offline, item=item1, _location=Location.ship, spec_set=Module)
        item2 = self.ch.type_(typeId=2, attributes={})
        item2.slots = {Slot.turret}
        holder2 = Mock(state=State.offline, item=item2, _location=Location.ship, spec_set=Module)
        self.trackHolder(holder1)
        self.trackHolder(holder2)
        self.assertEqual(self.st.launcherSlots.used, 1)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()
