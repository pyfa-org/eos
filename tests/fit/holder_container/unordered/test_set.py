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

from eos.const.eos import State
from eos.fit.holder.container import HolderSet
from eos.tests.fit.environment import BaseHolder, CachingHolder, OtherHolder, PlainHolder
from eos.tests.fit.fit_testcase import FitTestCase


class TestContainerSet(FitTestCase):

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.container = HolderSet(fit, BaseHolder)
        return fit

    def custom_membership_check(self, fit, holder):
        self.assertIn(holder, fit.container)

    def test_detached_add_none(self):
        fit = self.make_fit()
        # Action
        self.assertRaises(TypeError, fit.container.add, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        # Misc
        self.assert_fit_buffers_empty(fit.container)

    def test_detached_add_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.offline, spec_set=PlainHolder)
        # Action
        fit.container.add(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 1)
        self.assertIn(holder, fit.container)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit.container)

    def test_detached_add_holder_type_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.offline, spec_set=OtherHolder)
        # Action
        self.assertRaises(TypeError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit.container)

    def test_detached_add_holder_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder = Mock(_fit=None, state=State.overload, spec_set=PlainHolder)
        fit_other.container.add(holder)
        # Action
        self.assertRaises(ValueError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertEqual(len(fit_other.container), 1)
        self.assertIn(holder, fit_other.container)
        self.assertIs(holder._fit, fit_other)
        # Misc
        fit_other.container.remove(holder)
        self.assert_fit_buffers_empty(fit.container)
        self.assert_fit_buffers_empty(fit_other.container)

    def test_detached_remove_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        fit.container.add(holder)
        # Action
        fit.container.remove(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit.container)

    def test_detached_remove_holder_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.overload, spec_set=PlainHolder)
        # Action
        self.assertRaises(KeyError, fit.container.remove, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit.container)

    def test_detached_clear(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        fit.container.add(holder1)
        fit.container.add(holder2)
        # Action
        fit.container.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assert_object_buffers_empty(fit)

    def test_attached_add_none(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        # Action
        self.assertRaises(TypeError, fit.container.add, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        # Misc
        self.assert_fit_buffers_empty(fit.container)

    def test_attached_add_holder(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        # Action
        fit.container.add(holder)
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
        self.assertEqual(len(fit.container), 1)
        self.assertIn(holder, fit.container)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit.container)

    def test_attached_add_holder_caching(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.online, spec_set=CachingHolder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.add(holder)
        # Checks
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder, fit.st)
        self.assertEqual(fit.st[holder], {State.offline, State.online})
        self.assertEqual(len(fit.container), 1)
        self.assertIn(holder, fit.container)
        self.assertIs(holder._fit, fit)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 1)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit.container)

    def test_attached_add_holder_type_failure(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.offline, spec_set=OtherHolder)
        # Action
        self.assertRaises(TypeError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit.container)

    def test_attached_add_holder_value_failure(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        fit_other = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.offline, spec_set=PlainHolder)
        fit_other.container.add(holder)
        # Action
        self.assertRaises(ValueError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertEqual(len(fit_other.lt), 1)
        self.assertIn(holder, fit_other.lt)
        self.assertEqual(fit_other.lt[holder], {State.offline})
        self.assertEqual(len(fit_other.rt), 1)
        self.assertIn(holder, fit_other.rt)
        self.assertEqual(fit_other.rt[holder], {State.offline})
        self.assertEqual(len(fit_other.st), 1)
        self.assertIn(holder, fit_other.st)
        self.assertEqual(fit_other.st[holder], {State.offline})
        self.assertEqual(len(fit_other.container), 1)
        self.assertIn(holder, fit_other.container)
        self.assertIs(holder._fit, fit_other)
        # Misc
        fit_other.container.remove(holder)
        self.assert_fit_buffers_empty(fit.container)
        self.assert_fit_buffers_empty(fit_other.container)

    def test_attached_remove_holder(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.overload, spec_set=PlainHolder)
        fit.container.add(holder)
        # Action
        fit.container.remove(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit.container)

    def test_attached_remove_holder_failure(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        # Action
        self.assertRaises(KeyError, fit.container.remove, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit.container)

    def test_attached_clear(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder1 = Mock(_fit=None, state=State.overload, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        fit.container.add(holder1)
        fit.container.add(holder2)
        # Action
        fit.container.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assert_object_buffers_empty(fit)

    def test_len(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        self.assertEqual(len(fit.container), 0)
        fit.container.add(holder1)
        self.assertEqual(len(fit.container), 1)
        fit.container.add(holder2)
        self.assertEqual(len(fit.container), 2)
        fit.container.remove(holder1)
        self.assertEqual(len(fit.container), 1)
        fit.container.remove(holder2)
        self.assertEqual(len(fit.container), 0)
        self.assert_object_buffers_empty(fit)

    def test_contains(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=PlainHolder)
        self.assertFalse(holder1 in fit.container)
        self.assertFalse(holder2 in fit.container)
        fit.container.add(holder1)
        self.assertTrue(holder1 in fit.container)
        self.assertFalse(holder2 in fit.container)
        fit.container.add(holder2)
        self.assertTrue(holder1 in fit.container)
        self.assertTrue(holder2 in fit.container)
        fit.container.remove(holder1)
        self.assertFalse(holder1 in fit.container)
        self.assertTrue(holder2 in fit.container)
        fit.container.remove(holder2)
        self.assertFalse(holder1 in fit.container)
        self.assertFalse(holder2 in fit.container)
        self.assert_object_buffers_empty(fit)

    def test_iter(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=PlainHolder)
        self.assertEqual(set(holder for holder in fit.container), set())
        fit.container.add(holder1)
        self.assertEqual(set(holder for holder in fit.container), {holder1})
        fit.container.add(holder2)
        self.assertEqual(set(holder for holder in fit.container), {holder1, holder2})
        fit.container.remove(holder1)
        self.assertEqual(set(holder for holder in fit.container), {holder2})
        fit.container.remove(holder2)
        self.assertEqual(set(holder for holder in fit.container), set())
        self.assert_object_buffers_empty(fit)
