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

from eos.const.eos import State
from eos.data.source import Source
from eos.fit.holder.item import Ship
from tests.fit.environment import OtherCachingHolder
from tests.fit.fit_testcase import FitTestCase


class TestDirectHolderShip(FitTestCase):

    def custom_membership_check(self, fit, holder):
        self.assertIs(fit.ship, holder)

    def test_detached_none_to_none(self):
        fit = self.make_fit()
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        # Action
        fit.ship = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.ship)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_detached_none_to_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        fit.ship = holder
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(fit.ship, holder)
        self.assertIs(holder._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        fit.ship = None
        self.assert_fit_buffers_empty(fit)

    def test_detached_none_to_holder_type_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=OtherCachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, fit.__setattr__, 'ship', holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.ship)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_detached_none_to_holder_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        fit_other.ship = holder
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(ValueError, fit.__setattr__, 'ship', holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIsNone(fit.ship)
        self.assertIs(fit_other.ship, holder)
        self.assertIs(holder._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        # Misc
        fit_other.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_holder_to_holder(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Ship(1))
        holder2 = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        fit.ship = holder1
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        # Action
        fit.ship = holder2
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(fit.ship, holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 0)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 0)
        # Misc
        fit.ship = None
        self.assert_fit_buffers_empty(fit)

    def test_detached_holder_to_holder_type_failure(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Ship(1))
        holder2 = Mock(_fit=None, state=State.overload, spec_set=OtherCachingHolder(1))
        fit.ship = holder1
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, fit.__setattr__, 'ship', holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(fit.ship, holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 0)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 0)
        # Misc
        fit.ship = None
        self.assert_fit_buffers_empty(fit)

    def test_detached_holder_to_holder_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Ship(1))
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Ship(1))
        fit.ship = holder1
        fit_other.ship = holder2
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(ValueError, fit.__setattr__, 'ship', holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIs(fit.ship, holder1)
        self.assertIs(fit_other.ship, holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 0)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        # Misc
        fit.ship = None
        fit_other.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_detached_holder_to_none(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        fit.ship = holder
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        fit.ship = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.ship)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_attached_none_to_none(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        # Action
        fit.ship = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.ship)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_attached_none_to_holder(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, state=State.online, spec_set=Ship(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        fit.ship = holder
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder, fit.st)
        self.assertEqual(fit.st[holder], {State.offline, State.online})
        self.assertIs(fit.ship, holder)
        self.assertIs(holder._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 1)
        # Misc
        fit.ship = None
        self.assert_fit_buffers_empty(fit)

    def test_attached_none_to_holder_type_failure(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, state=State.offline, spec_set=OtherCachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, fit.__setattr__, 'ship', holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.ship)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_attached_none_to_holder_value_failure(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        fit_other = self.make_fit(source=source)
        holder = Mock(_fit=None, state=State.offline, spec_set=Ship(1))
        fit_other.ship = holder
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(ValueError, fit.__setattr__, 'ship', holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit_other.lt), 1)
        self.assertIn(holder, fit_other.lt)
        self.assertEqual(fit_other.lt[holder], {State.offline})
        self.assertEqual(len(fit_other.rt), 1)
        self.assertIn(holder, fit_other.rt)
        self.assertEqual(fit_other.rt[holder], {State.offline})
        self.assertIsNone(fit.ship)
        self.assertIs(fit_other.ship, holder)
        self.assertIs(holder._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        # Misc
        fit_other.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_attached_holder_to_holder(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder1 = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Ship(1))
        fit.ship = holder1
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        # Action
        fit.ship = holder2
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertIs(fit.ship, holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 2)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 1)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 1)
        # Misc
        fit.ship = None
        self.assert_fit_buffers_empty(fit)

    def test_attached_holder_to_holder_type_failure(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Ship(1))
        holder2 = Mock(_fit=None, state=State.online, spec_set=OtherCachingHolder(1))
        fit.ship = holder1
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, fit.__setattr__, 'ship', holder2)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline})
        self.assertIs(fit.ship, holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 0)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 0)
        # Misc
        fit.ship = None
        self.assert_fit_buffers_empty(fit)

    def test_attached_holder_to_holder_value_failure(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        fit_other = self.make_fit(source=source)
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Ship(1))
        holder2 = Mock(_fit=None, state=State.online, spec_set=Ship(1))
        fit.ship = holder1
        fit_other.ship = holder2
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(ValueError, fit.__setattr__, 'ship', holder2)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline})
        self.assertEqual(len(fit_other.lt), 1)
        self.assertIn(holder2, fit_other.lt)
        self.assertEqual(fit_other.lt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit_other.rt), 1)
        self.assertIn(holder2, fit_other.rt)
        self.assertEqual(fit_other.rt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit_other.st), 1)
        self.assertIn(holder2, fit_other.st)
        self.assertEqual(fit_other.st[holder2], {State.offline, State.online})
        self.assertIs(fit.ship, holder1)
        self.assertIs(fit_other.ship, holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 1)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        # Misc
        fit.ship = None
        fit_other.ship = None
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_attached_holder_to_none(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, state=State.active, spec_set=Ship(1))
        fit.ship = holder
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        fit.ship = None
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(fit.ship)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 1)
        # Misc
        self.assert_fit_buffers_empty(fit)
