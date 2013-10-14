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
from eos.fit.holder.container import HolderList
from eos.tests.fit.environment import BaseHolder, OtherHolder, PlainHolder
from eos.tests.fit.fit_testcase import FitTestCase


class TestContainerOrderedInsert(FitTestCase):

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.container = HolderList(fit, BaseHolder)
        return fit

    def custom_membership_check(self, fit, holder):
        self.assertIn(holder, fit.container)

    def test_detached_holder_to_zero(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.offline, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder3 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.insert(0, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[0], holder3)
        self.assertIs(fit.container[1], holder1)
        self.assertIs(fit.container[2], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_holder_to_end(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=PlainHolder)
        holder3 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.insert(2, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(fit.container[2], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_holder_outside(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=PlainHolder)
        fit.container.append(holder1)
        # Action
        fit.container.insert(3, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 4)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIs(fit.container[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_holder_inside_type_failure(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=PlainHolder)
        holder3 = Mock(_fit=None, state=State.overload, spec_set=OtherHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        self.assertRaises(TypeError, fit.container.insert, 1, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_holder_inside_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=PlainHolder)
        holder3 = Mock(_fit=None, state=State.overload, spec_set=PlainHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        fit_other.container.append(holder3)
        # Action
        self.assertRaises(ValueError, fit.container.insert, 1, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(len(fit_other.container), 1)
        self.assertIs(fit_other.container[0], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit_other)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit_other.container.remove(holder3)
        self.assert_object_buffers_empty(fit.container)
        self.assert_object_buffers_empty(fit_other.container)

    def test_detached_holder_outside_type_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.offline, spec_set=OtherHolder)
        # Action
        self.assertRaises(TypeError, fit.container.insert, 4, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_object_buffers_empty(fit.container)

    def test_detached_holder_outside_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder = Mock(_fit=None, state=State.offline, spec_set=PlainHolder)
        fit_other.container.append(holder)
        # Action
        self.assertRaises(ValueError, fit.container.insert, 4, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit_other.lt), 0)
        self.assertEqual(len(fit_other.rt), 0)
        self.assertEqual(len(fit_other.st), 0)
        self.assertIs(len(fit.container), 0)
        self.assertIs(len(fit_other.container), 1)
        self.assertIs(fit_other.container[0], holder)
        self.assertIs(holder._fit, fit_other)
        # Misc
        fit_other.container.remove(holder)
        self.assert_object_buffers_empty(fit.container)
        self.assert_object_buffers_empty(fit_other.container)

    def test_detached_none_inside(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=PlainHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.insert(1, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIs(fit.container[2], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_object_buffers_empty(fit.container)

    def test_detached_none_outside(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.insert(6, None)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_holder_to_zero(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        holder3 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.insert(0, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 3)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertIn(holder3, fit.lt)
        self.assertEqual(fit.lt[holder3], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.rt), 3)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertIn(holder3, fit.rt)
        self.assertEqual(fit.rt[holder3], {State.offline, State.online, State.active})
        self.assertEqual(len(fit.st), 3)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online})
        self.assertIn(holder3, fit.st)
        self.assertEqual(fit.st[holder3], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[0], holder3)
        self.assertIs(fit.container[1], holder1)
        self.assertIs(fit.container[2], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_holder_to_end(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder1 = Mock(_fit=None, state=State.overload, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.offline, spec_set=PlainHolder)
        holder3 = Mock(_fit=None, state=State.offline, spec_set=PlainHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.insert(2, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 3)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active, State.overload})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline})
        self.assertIn(holder3, fit.lt)
        self.assertEqual(fit.lt[holder3], {State.offline})
        self.assertEqual(len(fit.rt), 3)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active, State.overload})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline})
        self.assertIn(holder3, fit.rt)
        self.assertEqual(fit.rt[holder3], {State.offline})
        self.assertEqual(len(fit.rt), 3)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active, State.overload})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline})
        self.assertIn(holder3, fit.st)
        self.assertEqual(fit.st[holder3], {State.offline})
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(fit.container[2], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit.container.remove(holder3)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_holder_outside(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        fit.container.append(holder1)
        # Action
        fit.container.insert(3, holder2)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online})
        self.assertIs(len(fit.container), 4)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIs(fit.container[3], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_holder_inside_type_failure(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        holder3 = Mock(_fit=None, state=State.offline, spec_set=OtherHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        self.assertRaises(TypeError, fit.container.insert, 1, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online})
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_holder_inside_value_failure(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        fit_other = self.make_fit(eos=eos)
        holder1 = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        holder3 = Mock(_fit=None, state=State.offline, spec_set=PlainHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        fit_other.container.append(holder3)
        # Action
        self.assertRaises(ValueError, fit.container.insert, 1, holder3)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online, State.active})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online})
        self.assertEqual(len(fit_other.lt), 1)
        self.assertIn(holder3, fit_other.lt)
        self.assertEqual(fit_other.lt[holder3], {State.offline})
        self.assertEqual(len(fit_other.rt), 1)
        self.assertIn(holder3, fit_other.rt)
        self.assertEqual(fit_other.rt[holder3], {State.offline})
        self.assertEqual(len(fit_other.st), 1)
        self.assertIn(holder3, fit_other.st)
        self.assertEqual(fit_other.st[holder3], {State.offline})
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(len(fit_other.container), 1)
        self.assertIs(fit_other.container[0], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        self.assertIs(holder3._fit, fit_other)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        fit_other.container.remove(holder3)
        self.assert_object_buffers_empty(fit.container)
        self.assert_object_buffers_empty(fit_other.container)

    def test_attached_holder_outside_type_failure(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=OtherHolder)
        # Action
        self.assertRaises(TypeError, fit.container.insert, 4, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_object_buffers_empty(fit.container)

    def test_attached_holder_outside_value_failure(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        fit_other = self.make_fit(eos=eos)
        holder = Mock(_fit=None, state=State.active, spec_set=PlainHolder)
        fit_other.container.append(holder)
        # Action
        self.assertRaises(ValueError, fit.container.insert, 4, holder)
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        self.assertEqual(len(fit_other.lt), 1)
        self.assertIn(holder, fit_other.lt)
        self.assertEqual(fit_other.lt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit_other.rt), 1)
        self.assertIn(holder, fit_other.rt)
        self.assertEqual(fit_other.rt[holder], {State.offline, State.online, State.active})
        self.assertEqual(len(fit_other.st), 1)
        self.assertIn(holder, fit_other.st)
        self.assertEqual(fit_other.st[holder], {State.offline, State.online, State.active})
        self.assertIs(len(fit.container), 0)
        self.assertIs(len(fit_other.container), 1)
        self.assertIs(fit_other.container[0], holder)
        self.assertIs(holder._fit, fit_other)
        # Misc
        fit_other.container.remove(holder)
        self.assert_object_buffers_empty(fit.container)
        self.assert_object_buffers_empty(fit_other.container)

    def test_attached_none_inside(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder1 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.overload, spec_set=PlainHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.insert(1, None)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online, State.active, State.overload})
        self.assertIs(len(fit.container), 3)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIs(fit.container[2], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_object_buffers_empty(fit.container)

    def test_attached_none_outside(self):
        eos = Mock(spec_set=())
        fit = self.make_fit(eos=eos)
        holder1 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        holder2 = Mock(_fit=None, state=State.online, spec_set=PlainHolder)
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        fit.container.insert(6, None)
        # Checks
        self.assertEqual(len(fit.lt), 2)
        self.assertIn(holder1, fit.lt)
        self.assertEqual(fit.lt[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.lt)
        self.assertEqual(fit.lt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.rt), 2)
        self.assertIn(holder1, fit.rt)
        self.assertEqual(fit.rt[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.rt)
        self.assertEqual(fit.rt[holder2], {State.offline, State.online})
        self.assertEqual(len(fit.st), 2)
        self.assertIn(holder1, fit.st)
        self.assertEqual(fit.st[holder1], {State.offline, State.online})
        self.assertIn(holder2, fit.st)
        self.assertEqual(fit.st[holder2], {State.offline, State.online})
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_object_buffers_empty(fit.container)
