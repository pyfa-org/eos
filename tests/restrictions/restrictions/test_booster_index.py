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
from eos.fit.holder.item import Booster, ModuleHigh
from tests.restriction_tracker.restriction_testcase import RestrictionTestCase


class TestBoosterIndex(RestrictionTestCase):
    """Check functionality of booster slot index restriction"""

    def test_fail(self):
        # Check that if 2 or more holders are put into single slot
        # index, error is raised
        item = self.ch.type_(type_id=1, attributes={Attribute.boosterness: 120})
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.character, spec_set=Booster(1))
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.character, spec_set=Booster(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        restriction_error1 = self.get_restriction_error(holder1, Restriction.booster_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.holder_slot_index, 120)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.booster_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.holder_slot_index, 120)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_other_holder_class(self):
        # Make sure holders of all classes are affected
        item = self.ch.type_(type_id=1, attributes={Attribute.boosterness: 120})
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.ship, spec_set=ModuleHigh(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        restriction_error1 = self.get_restriction_error(holder1, Restriction.booster_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.holder_slot_index, 120)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.booster_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.holder_slot_index, 120)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_fail_original(self):
        # Make sure that original attributes are used
        item = self.ch.type_(type_id=1, attributes={Attribute.boosterness: 120})
        holder1 = Mock(state=State.offline, item=item, _domain=Domain.character, spec_set=Booster(1))
        holder2 = Mock(state=State.offline, item=item, _domain=Domain.character, spec_set=Booster(1))
        holder1.attributes = {Attribute.boosterness: 119}
        holder2.attributes = {Attribute.boosterness: 121}
        self.track_holder(holder1)
        self.track_holder(holder2)
        restriction_error1 = self.get_restriction_error(holder1, Restriction.booster_index)
        self.assertIsNotNone(restriction_error1)
        self.assertEqual(restriction_error1.holder_slot_index, 120)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.booster_index)
        self.assertIsNotNone(restriction_error2)
        self.assertEqual(restriction_error2.holder_slot_index, 120)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass(self):
        # Single holder which takes some slot shouldn't
        # trigger any errors
        item = self.ch.type_(type_id=1, attributes={Attribute.boosterness: 120})
        holder = Mock(state=State.offline, item=item, _domain=Domain.character, spec_set=Booster(1))
        self.track_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.booster_index)
        self.assertIsNone(restriction_error)
        self.untrack_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_different(self):
        # Holders taking different slots shouldn't trigger any errors
        item1 = self.ch.type_(type_id=1, attributes={Attribute.boosterness: 120})
        item2 = self.ch.type_(type_id=2, attributes={Attribute.boosterness: 121})
        holder1 = Mock(state=State.offline, item=item1, _domain=Domain.character, spec_set=Booster(1))
        holder2 = Mock(state=State.offline, item=item2, _domain=Domain.character, spec_set=Booster(1))
        self.track_holder(holder1)
        self.track_holder(holder2)
        restriction_error1 = self.get_restriction_error(holder1, Restriction.booster_index)
        self.assertIsNone(restriction_error1)
        restriction_error2 = self.get_restriction_error(holder2, Restriction.booster_index)
        self.assertIsNone(restriction_error2)
        self.untrack_holder(holder1)
        self.untrack_holder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
