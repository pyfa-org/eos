from unittest.mock import Mock

from eos.const.eos import Location, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Character, Drone, Implant
from eos.tests.statTracker.statTestCase import StatTestCase


class TestLaunchedDrone(StatTestCase):

    def testTotal(self):
        # Check that modified attribute of character is used
        charItem = self.ch.type_(typeId=1, attributes={Attribute.maxActiveDrones: 2})
        charHolder = Mock(state=State.offline, item=charItem, _location=None, spec_set=Character)
        charHolder.attributes = {Attribute.maxActiveDrones: 6}
        self.setCharacter(charHolder)
        self.assertEqual(self.st.launchedDrones.total, 6)
        self.setCharacter(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoShip(self):
        # None for max launched amount when no ship
        self.assertIsNone(self.st.launchedDrones.total)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoAttr(self):
        # None for max launched amount when no attribute on ship
        charItem = self.ch.type_(typeId=1)
        charHolder = Mock(state=State.offline, item=charItem, _location=None, spec_set=Character)
        charHolder.attributes = {}
        self.setCharacter(charHolder)
        self.assertIsNone(self.st.launchedDrones.total)
        self.setCharacter(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseEmpty(self):
        self.assertEqual(self.st.launchedDrones.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseSingle(self):
        item = self.ch.type_(typeId=1, attributes={})
        holder = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        self.assertEqual(self.st.launchedDrones.used, 1)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseMultiple(self):
        item = self.ch.type_(typeId=1, attributes={})
        holder1 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        holder2 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder1)
        self.trackHolder(holder2)
        self.assertEqual(self.st.launchedDrones.used, 2)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseOtherClass(self):
        item = self.ch.type_(typeId=1, attributes={})
        holder = Mock(state=State.online, item=item, _location=Location.space, spec_set=Implant)
        self.trackHolder(holder)
        self.assertEqual(self.st.launchedDrones.used, 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseState(self):
        item = self.ch.type_(typeId=1, attributes={})
        holder = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        self.trackHolder(holder)
        self.assertEqual(self.st.launchedDrones.used, 0)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()
