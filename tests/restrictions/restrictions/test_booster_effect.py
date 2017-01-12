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
from eos.fit.holder.item import Booster, Implant
from tests.restrictions.restriction_testcase import RestrictionTestCase


class TestBoosterEffect(RestrictionTestCase):
    """Check functionality of booster's hidden effects restriction"""

    def test_fail(self):
        # Check if error is raised when there's disabled effect
        item = self.ch.type_(type_id=1)
        holder = Mock(state=State.offline, item=item, _domain=Domain.character, spec_set=Booster(1))
        holder.side_effects = {55, 66}
        holder._disabled_effects = {77, 99}
        self.add_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.booster_effect)
        self.assertIsNotNone(restriction_error)
        self.assertEqual(restriction_error.illegally_disabled, {77, 99})
        self.assertEqual(restriction_error.disablable, {55, 66})
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_disabled_side_effect(self):
        item = self.ch.type_(type_id=1)
        holder = Mock(state=State.offline, item=item, _domain=Domain.character, spec_set=Booster(1))
        holder.side_effects = {55, 66}
        holder._disabled_effects = {55, 66}
        self.add_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.booster_effect)
        self.assertIsNone(restriction_error)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_enabled_regular_effect(self):
        item = self.ch.type_(type_id=1)
        holder = Mock(state=State.offline, item=item, _domain=Domain.character, spec_set=Booster(1))
        # Enabled regular effects are not listed in any of
        # these containers
        holder.side_effects = {}
        holder._disabled_effects = set()
        self.add_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.booster_effect)
        self.assertIsNone(restriction_error)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()

    def test_pass_non_booster(self):
        item = self.ch.type_(type_id=1)
        holder = Mock(state=State.offline, item=item, _domain=Domain.character, spec=Implant(1))
        holder.side_effects = {55, 66}
        holder._disabled_effects = {77, 99}
        self.add_holder(holder)
        restriction_error = self.get_restriction_error(holder, Restriction.booster_effect)
        self.assertIsNone(restriction_error)
        self.remove_holder(holder)
        self.assertEqual(len(self.log), 0)
        self.assert_restriction_buffers_empty()
