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
from tests.fit.environment import BaseHolder, CachingHolder
from tests.fit.fit_testcase import FitTestCase


class TestContainerOrderedMisc(FitTestCase):

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.container = HolderList(fit, BaseHolder)
        return fit

    def custom_membership_check(self, fit, holder):
        self.assertIn(holder, fit.container)

    def test_len(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        self.assertEqual(len(fit.container), 0)
        fit.container.append(holder1)
        self.assertEqual(len(fit.container), 1)
        fit.container.place(3, holder2)
        self.assertEqual(len(fit.container), 4)
        fit.container.remove(holder1)
        self.assertEqual(len(fit.container), 3)
        fit.container.remove(holder2)
        self.assertEqual(len(fit.container), 0)
        self.assert_object_buffers_empty(fit.container)

    def test_contains(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        self.assertFalse(holder1 in fit.container)
        self.assertFalse(None in fit.container)
        self.assertFalse(holder2 in fit.container)
        fit.container.append(holder1)
        self.assertTrue(holder1 in fit.container)
        self.assertFalse(None in fit.container)
        self.assertFalse(holder2 in fit.container)
        fit.container.place(3, holder2)
        self.assertTrue(holder1 in fit.container)
        self.assertTrue(None in fit.container)
        self.assertTrue(holder2 in fit.container)
        fit.container.remove(holder1)
        self.assertFalse(holder1 in fit.container)
        self.assertTrue(None in fit.container)
        self.assertTrue(holder2 in fit.container)
        fit.container.remove(holder2)
        self.assertFalse(holder1 in fit.container)
        self.assertFalse(None in fit.container)
        self.assertFalse(holder2 in fit.container)
        self.assert_object_buffers_empty(fit.container)

    def test_iter(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, state=State.active, spec_set=CachingHolder(1))
        self.assertEqual(list(holder for holder in fit.container), [])
        fit.container.append(holder1)
        self.assertEqual(list(holder for holder in fit.container), [holder1])
        fit.container.place(3, holder2)
        self.assertEqual(list(holder for holder in fit.container), [holder1, None, None, holder2])
        fit.container.remove(holder1)
        self.assertEqual(list(holder for holder in fit.container), [None, None, holder2])
        fit.container.remove(holder2)
        self.assertEqual(list(holder for holder in fit.container), [])
        self.assert_object_buffers_empty(fit.container)

    def test_detached_clear(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, state=State.online, spec_set=CachingHolder(1))
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertGreaterEqual(holder1_cleans_after - holder1_cleans_before, 0)
        self.assertGreaterEqual(holder2_cleans_after - holder2_cleans_before, 0)
        # Misc
        self.assert_object_buffers_empty(fit.container)

    def test_attached_clear(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder1 = Mock(_fit=None, state=State.overload, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, state=State.overload, spec_set=CachingHolder(1))
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertGreaterEqual(holder1_cleans_after - holder1_cleans_before, 1)
        self.assertGreaterEqual(holder2_cleans_after - holder2_cleans_before, 1)
        # Misc
        self.assert_object_buffers_empty(fit.container)

    def test_slice(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, state=State.active, spec_set=CachingHolder(1))
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        slice_full = fit.container[:]
        self.assertEqual(len(slice_full), 4)
        self.assertIs(slice_full[0], holder1)
        self.assertIsNone(slice_full[1])
        self.assertIsNone(slice_full[2])
        self.assertIs(slice_full[3], holder2)
        slice_positive = fit.container[0:2]
        self.assertEqual(len(slice_positive), 2)
        self.assertIs(slice_positive[0], holder1)
        self.assertIsNone(slice_positive[1])
        slice_negative = fit.container[-2:]
        self.assertEqual(len(slice_negative), 2)
        self.assertIsNone(slice_negative[0])
        self.assertIs(slice_negative[1], holder2)
        slice_step = fit.container[::2]
        self.assertEqual(len(slice_step), 2)
        self.assertIs(slice_step[0], holder1)
        self.assertIsNone(slice_step[1])
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_object_buffers_empty(fit.container)

    def test_holder_view(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        view = fit.container.holders()
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        fit.container.append(holder1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [holder1])
        self.assertTrue(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        fit.container.place(3, holder2)
        self.assertEqual(len(view), 2)
        self.assertEqual(list(view), [holder1, holder2])
        self.assertTrue(holder1 in view)
        self.assertTrue(holder2 in view)
        self.assertFalse(None in view)
        fit.container.free(holder1)
        self.assertEqual(len(view), 1)
        self.assertEqual(list(view), [holder2])
        self.assertFalse(holder1 in view)
        self.assertTrue(holder2 in view)
        self.assertFalse(None in view)
        fit.container.free(holder2)
        self.assertEqual(len(view), 0)
        self.assertEqual(list(view), [])
        self.assertFalse(holder1 in view)
        self.assertFalse(holder2 in view)
        self.assertFalse(None in view)
        self.assert_object_buffers_empty(fit.container)
