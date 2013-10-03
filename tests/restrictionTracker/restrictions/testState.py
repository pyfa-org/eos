#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
#===============================================================================


from unittest.mock import Mock

from eos.const.eos import Location, Restriction, State
from eos.fit.holder.item import Module
from eos.tests.restrictionTracker.restrictionTestCase import RestrictionTestCase


class TestState(RestrictionTestCase):
    """Check functionality of holder state restriction"""

    def testStateLower(self):
        item = self.ch.type_(typeId=1)
        item.maxState = State.active
        holder = Mock(state=State.online, item=item, _location=Location.character, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.state)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testStateEqual(self):
        item = self.ch.type_(typeId=1)
        item.maxState = State.active
        holder = Mock(state=State.active, item=item, _location=Location.character, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.state)
        self.assertIsNone(restrictionError)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()

    def testStateHigher(self):
        item = self.ch.type_(typeId=1)
        item.maxState = State.active
        holder = Mock(state=State.overload, item=item, _location=Location.character, spec_set=Module)
        self.trackHolder(holder)
        restrictionError = self.getRestrictionError(holder, Restriction.state)
        self.assertIsNotNone(restrictionError)
        self.assertEqual(restrictionError.currentState, State.overload)
        self.assertCountEqual(restrictionError.allowedStates, (State.offline, State.online, State.active))
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertRestrictionBuffersEmpty()
