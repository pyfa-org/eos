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
from eos.fit.holder.container import HolderList
from tests.fit.environment import BaseHolder, CachingHolder, OtherCachingHolder
from tests.fit.fit_testcase import FitTestCase


class TestContainerOrderedEquip(FitTestCase):

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.container = HolderList(fit, BaseHolder)
        return fit

    def custom_membership_check(self, fit, holder):
        self.assertIn(holder, fit.container)

    def test_detached_none_to_empty(self):
        fit = self.make_fit()
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, fit.container.equip, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        # Misc
        self.assert_object_buffers_empty(fit.container)

    def test_detached_holder_to_empty(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.equip(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder)
        self.assertIs(holder._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        fit.container.remove(holder)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_holder_to_empty_type_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.offline, spec_set=OtherCachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, fit.container.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        self.assert_object_buffers_empty(fit.container)

    def test_detached_holder_to_empty_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=CachingHolder(1))
        fit_other.container.equip(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(ValueError, fit.container.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIs(len(fit_other.container), 1)
        self.assertIs(fit_other.container[0], holder)
        self.assertIs(holder._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        # Misc
        fit_other.container.remove(holder)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_holder_solid(self):
        # Check case when all slots of list are filled
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        holder3 = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        fit.container.append(holder1)
        fit.container.append(holder2)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        holder3_cleans_before = len(holder3._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.equip(holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[2], holder3)
        self.assertIs(holder3._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        holder3_cleans_after = len(holder3._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 0)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 0)
        self.assertEqual(holder3_cleans_after - holder3_cleans_before, 0)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_holder_first_hole(self):
        # Check that leftmost empty slot is taken
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, state=State.online, spec_set=CachingHolder(1))
        holder3 = Mock(_fit=None, state=State.overload, spec_set=CachingHolder(1))
        holder4 = Mock(_fit=None, state=State.online, spec_set=CachingHolder(1))
        fit.container.append(holder1)
        fit.container.insert(3, holder2)
        fit.container.insert(6, holder3)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        holder3_cleans_before = len(holder3._clear_volatile_attrs.mock_calls)
        holder4_cleans_before = len(holder4._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.equip(holder4)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 7)
        self.assertIs(fit.container[1], holder4)
        self.assertIs(holder4._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        holder3_cleans_after = len(holder3._clear_volatile_attrs.mock_calls)
        holder4_cleans_after = len(holder4._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 0)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 0)
        self.assertEqual(holder3_cleans_after - holder3_cleans_before, 0)
        self.assertEqual(holder4_cleans_after - holder4_cleans_before, 0)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        fit.container.remove(holder4)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_none_to_empty(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, fit.container.equip, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        # Misc
        self.assert_object_buffers_empty(fit.container)

    def test_attached_holder_to_empty(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, state=State.overload, spec_set=CachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.equip(holder)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder, fit.st)
        self.assertEqual(fit.st[holder], {State.offline, State.online, State.active, State.overload})
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder)
        self.assertIs(holder._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 1)
        # Misc
        fit.container.remove(holder)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_holder_to_empty_type_failure(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, state=State.offline, spec_set=OtherCachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, fit.container.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        self.assert_object_buffers_empty(fit.container)

    def test_attached_holder_to_empty_value_failure(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        fit_other = self.make_fit(source=source)
        holder = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        fit_other.container.equip(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(ValueError, fit.container.equip, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertEqual(len(fit_other.lt), 1)
        self.assertIn(holder, fit_other.lt)
        self.assertEqual(fit_other.lt[holder], {State.offline})
        self.assertEqual(len(fit_other.rt), 1)
        self.assertIn(holder, fit_other.rt)
        self.assertEqual(fit_other.rt[holder], {State.offline})
        self.assertEqual(len(fit_other.st), 1)
        self.assertIn(holder, fit_other.st)
        self.assertEqual(fit_other.st[holder], {State.offline})
        self.assertIs(len(fit_other.container), 1)
        self.assertIs(fit_other.container[0], holder)
        self.assertIs(holder._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        # Misc
        fit_other.container.remove(holder)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_holder_solid(self):
        # Check case when all slots of list are filled
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder1 = Mock(_fit=None, state=State.active, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        holder3 = Mock(_fit=None, state=State.overload, spec_set=CachingHolder(1))
        fit.container.append(holder1)
        fit.container.append(holder2)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        holder3_cleans_before = len(holder3._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.equip(holder3)
        # Checks
        self.assertEqual(len(fit.lt), 3)
        self.assertIn(holder3, fit.lt)
        self.assertEqual(fit.lt[holder3], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.rt), 3)
        self.assertIn(holder3, fit.rt)
        self.assertEqual(fit.rt[holder3], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.st), 3)
        self.assertIn(holder3, fit.st)
        self.assertEqual(fit.st[holder3], {State.offline, State.online, State.active, State.overload})
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[2], holder3)
        self.assertIs(holder3._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        holder3_cleans_after = len(holder3._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 1)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 1)
        self.assertEqual(holder3_cleans_after - holder3_cleans_before, 1)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_holder_first_hole(self):
        # Check that leftmost empty slot is taken
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder1 = Mock(_fit=None, state=State.active, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        holder3 = Mock(_fit=None, state=State.online, spec_set=CachingHolder(1))
        holder4 = Mock(_fit=None, state=State.active, spec_set=CachingHolder(1))
        fit.container.append(holder1)
        fit.container.insert(3, holder2)
        fit.container.insert(6, holder3)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        holder3_cleans_before = len(holder3._clear_volatile_attrs.mock_calls)
        holder4_cleans_before = len(holder4._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.equip(holder4)
        # Checks
        self.assertEqual(len(fit.lt), 4)
        self.assertIn(holder4, fit.lt)
        self.assertEqual(fit.lt[holder4], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 4)
        self.assertIn(holder4, fit.rt)
        self.assertEqual(fit.rt[holder4], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 4)
        self.assertIn(holder4, fit.st)
        self.assertEqual(fit.st[holder4], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 7)
        self.assertIs(fit.container[1], holder4)
        self.assertIs(holder4._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        holder3_cleans_after = len(holder3._clear_volatile_attrs.mock_calls)
        holder4_cleans_after = len(holder4._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 1)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 1)
        self.assertEqual(holder3_cleans_after - holder3_cleans_before, 1)
        self.assertEqual(holder4_cleans_after - holder4_cleans_before, 1)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        fit.container.remove(holder4)
        self.assert_object_buffers_empty(fit.container)
