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
from eos.fit.holder.item import ModuleHigh
from tests.restriction_tracker.restriction_testcase import RestrictionTestCase


class TestState(RestrictionTestCase):
    """Check functionality of holder state restriction"""

    def test_state_lower(self):
        item = self.ch.type_(type_id=1)
        item.max_state = State.active
        holder = Mock(state=State.online, item=item, _domain=Domain.character, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.state)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_state_equal(self):
        item = self.ch.type_(type_id=1)
        item.max_state = State.active
        holder = Mock(state=State.active, item=item, _domain=Domain.character, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.state)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_state_higher(self):
        item = self.ch.type_(type_id=1)
        item.max_state = State.active
        holder = Mock(state=State.overload, item=item, _domain=Domain.character, spec_set=ModuleHigh(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.state)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.current_state, State.overload)
        self.assertCountEqual(restriction_error.allowed_states, (State.offline, State.online, State.active))
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
