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
from eos.fit.holder.container import HolderRestrictedSet
from tests.fit.environment import BaseHolder, CachingHolder, OtherCachingHolder
from tests.fit.fit_testcase import FitTestCase


class TestContainerRestrictedSet(FitTestCase):

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.container = HolderRestrictedSet(fit, BaseHolder)
        return fit

    def custom_membership_check(self, fit, holder):
        self.assertIn(holder, fit.container)

    def test_detached_add_none(self):
        fit = self.make_fit()
        # Action
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        self.assertRaises(TypeError, fit.container.add, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_add_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=CachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.add(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[1], holder)
        self.assertIn(holder, fit.container)
        self.assertIs(holder._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_add_holder_type_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=OtherCachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_add_holder_value_failure_has_fit(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.overload, spec_set=CachingHolder(1))
        fit_other.container.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
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
        self.assertIs(fit_other.container[1], holder)
        self.assertIn(holder, fit_other.container)
        self.assertIs(holder._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        # Misc
        fit_other.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)
        self.assert_object_buffers_empty(fit.container)
        self.assert_object_buffers_empty(fit_other.container)

    def test_detached_add_holder_value_failure_existing_type_id(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=CachingHolder(1))
        fit.container.add(holder1)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(ValueError, fit.container.add, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[1], holder1)
        self.assertIn(holder1, fit.container)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 0)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 0)
        # Misc
        fit.container.remove(holder1)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_remove_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.active, spec_set=CachingHolder(1))
        fit.container.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.remove(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_remove_holder_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.overload, spec_set=CachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(KeyError, fit.container.remove, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_delitem_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.active, spec_set=CachingHolder(1))
        fit.container.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        del fit.container[1]
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_delitem_holder_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.active, spec_set=CachingHolder(1))
        fit.container.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(KeyError, fit.container.__delitem__, 3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 1)
        self.assertIs(holder._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_clear(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, _type_id=1, state=State.active, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, _type_id=2, state=State.online, spec_set=CachingHolder(1))
        fit.container.add(holder1)
        fit.container.add(holder2)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertGreaterEqual(holder1_cleans_after - holder1_cleans_before, 0)
        self.assertGreaterEqual(holder2_cleans_after - holder2_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_add_none(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, fit.container.add, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_add_holder(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, _type_id=1, state=State.online, spec_set=CachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
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
        self.assertIs(fit.container[1], holder)
        self.assertIn(holder, fit.container)
        self.assertIs(holder._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 1)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_add_holder_type_failure(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=OtherCachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(TypeError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_add_holder_value_failure_has_fit(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        fit_other = self.make_fit(source=source)
        holder = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=CachingHolder(1))
        fit_other.container.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_before = len(fit_other.stats._clear_volatile_attrs.mock_calls)
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
        self.assertIs(fit_other.container[1], holder)
        self.assertIn(holder, fit_other.container)
        self.assertIs(holder._fit, fit_other)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        st_other_cleans_after = len(fit_other.stats._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        self.assertEqual(st_other_cleans_after - st_other_cleans_before, 0)
        # Misc
        fit_other.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)
        self.assert_object_buffers_empty(fit.container)
        self.assert_object_buffers_empty(fit_other.container)

    def test_attached_add_holder_value_failure_existing_type_id(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder1 = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=CachingHolder(1))
        fit.container.add(holder1)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(ValueError, fit.container.add, holder2)
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
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[1], holder1)
        self.assertIn(holder1, fit.container)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(fit.container[1], holder1)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder1_cleans_after - holder1_cleans_before, 0)
        self.assertEqual(holder2_cleans_after - holder2_cleans_before, 0)
        # Misc
        fit.container.remove(holder1)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_remove_holder(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, _type_id=1, state=State.overload, spec_set=CachingHolder(1))
        fit.container.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.remove(holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 1)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_remove_holder_failure(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, _type_id=1, state=State.online, spec_set=CachingHolder(1))
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(KeyError, fit.container.remove, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_delitem_holder(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, _type_id=1, state=State.active, spec_set=CachingHolder(1))
        fit.container.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        del fit.container[1]
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 1)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_delitem_holder_failure(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, _type_id=1, state=State.active, spec_set=CachingHolder(1))
        fit.container.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        self.assertRaises(KeyError, fit.container.__delitem__, 3)
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder, fit.st)
        self.assertEqual(fit.st[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.container), 1)
        self.assertIs(holder._fit, fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 0)
        self.assertEqual(holder_cleans_after - holder_cleans_before, 0)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_clear(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder1 = Mock(_fit=None, _type_id=1, state=State.overload, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, _type_id=2, state=State.active, spec_set=CachingHolder(1))
        fit.container.add(holder1)
        fit.container.add(holder2)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_before = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_before = len(holder2._clear_volatile_attrs.mock_calls)
        # Action
        fit.container.clear()
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        holder1_cleans_after = len(holder1._clear_volatile_attrs.mock_calls)
        holder2_cleans_after = len(holder2._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_before, 1)
        self.assertGreaterEqual(holder1_cleans_after - holder1_cleans_before, 1)
        self.assertGreaterEqual(holder2_cleans_after - holder2_cleans_before, 1)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_get_item(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = Mock(_fit=None, _type_id=5, state=State.online, spec_set=CachingHolder(1))
        fit.container.add(holder)
        self.assertIs(fit.container[5], holder)
        self.assertRaises(KeyError, fit.container.__getitem__, 0)
        self.assertRaises(KeyError, fit.container.__getitem__, 6)
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_len(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, _type_id=1, state=State.active, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, _type_id=2, state=State.online, spec_set=CachingHolder(1))
        self.assertEqual(len(fit.container), 0)
        fit.container.add(holder1)
        self.assertEqual(len(fit.container), 1)
        fit.container.add(holder2)
        self.assertEqual(len(fit.container), 2)
        fit.container.remove(holder1)
        self.assertEqual(len(fit.container), 1)
        fit.container.remove(holder2)
        self.assertEqual(len(fit.container), 0)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_contains(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, _type_id=1, state=State.active, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, _type_id=2, state=State.offline, spec_set=CachingHolder(1))
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
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_iter(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, _type_id=1, state=State.active, spec_set=CachingHolder(1))
        holder2 = Mock(_fit=None, _type_id=2, state=State.offline, spec_set=CachingHolder(1))
        self.assertEqual(set(holder for holder in fit.container), set())
        fit.container.add(holder1)
        self.assertEqual(set(holder for holder in fit.container), {holder1})
        fit.container.add(holder2)
        self.assertEqual(set(holder for holder in fit.container), {holder1, holder2})
        fit.container.remove(holder1)
        self.assertEqual(set(holder for holder in fit.container), {holder2})
        fit.container.remove(holder2)
        self.assertEqual(set(holder for holder in fit.container), set())
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
