# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
from eos.fit.container import HolderList
from eos.fit.messages import HolderAdded, HolderRemoved
from tests.container.environment import Fit, Holder
from tests.container.container_testcase import ContainerTestCase


class TestContainerOrderedFree(ContainerTestCase):

    def make_fit(self):
        assertions = {
            HolderAdded: lambda f, m: self.assertIn(m.holder, f.container),
            HolderRemoved: lambda f, m: self.assertIn(m.holder, f.container)
        }
        fit = Fit(self, message_assertions=assertions)
        fit.container = HolderList(fit, Holder)
        return fit

    def test_none(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.free, None)
        # Checks
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.free(holder1)
        # Action
        with self.fit_assertions(fit):
            fit.container.free(None)
        # Checks
        self.assertIs(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.free(holder2)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_holder(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        with self.fit_assertions(fit):
            fit.container.free(holder1)
        # Checks
        self.assertIs(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Action
        with self.fit_assertions(fit):
            fit.container.free(holder2)
        # Checks
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_holder_failure(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.overload, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Holder(1))
        fit.container.append(holder1)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.free, holder2)
        # Checks
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.container.free(holder1)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.free, holder1)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_holder_after_nones(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.offline, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.overload, spec_set=Holder(1))
        holder3 = Mock(_fit=None, state=State.offline, spec_set=Holder(1))
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        fit.container.place(6, holder3)
        # Action
        with self.fit_assertions(fit):
            fit.container.free(holder2)
        # Checks
        self.assertEqual(len(fit.container), 7)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIsNone(fit.container[3])
        self.assertIsNone(fit.container[4])
        self.assertIsNone(fit.container[5])
        self.assertIs(fit.container[6], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(holder3._fit, fit)
        # Action
        with self.fit_assertions(fit):
            fit.container.free(holder3)
        # Checks
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.container.free(holder1)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_holder(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.online, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder(1))
        fit.container.append(holder1)
        fit.container.append(holder2)
        # Action
        with self.fit_assertions(fit):
            fit.container.free(0)
        # Checks
        self.assertEqual(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], holder2)
        self.assertIsNone(holder1._fit)
        self.assertIs(holder2._fit, fit)
        # Action
        with self.fit_assertions(fit):
            fit.container.free(1)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_none(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.offline, spec_set=Holder(1))
        fit.container.place(1, holder)
        # Action
        with self.fit_assertions(fit):
            fit.container.free(0)
        # Checks
        self.assertEqual(len(fit.container), 2)
        self.assertIsNone(fit.container[0])
        self.assertIs(fit.container[1], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.free(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_after_nones(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder(1))
        holder3 = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        fit.container.append(holder1)
        fit.container.place(3, holder2)
        fit.container.place(6, holder3)
        # Action
        with self.fit_assertions(fit):
            fit.container.free(3)
        # Checks
        self.assertEqual(len(fit.container), 7)
        self.assertIs(fit.container[0], holder1)
        self.assertIsNone(fit.container[1])
        self.assertIsNone(fit.container[2])
        self.assertIsNone(fit.container[3])
        self.assertIsNone(fit.container[4])
        self.assertIsNone(fit.container[5])
        self.assertIs(fit.container[6], holder3)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIs(holder3._fit, fit)
        # Action
        with self.fit_assertions(fit):
            fit.container.free(6)
        # Checks
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        self.assertIsNone(holder3._fit)
        # Misc
        fit.container.free(holder1)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_index_outside(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.online, spec_set=Holder(1))
        fit.container.append(holder)
        # Action
        with self.fit_assertions(fit):
            self.assertRaises(IndexError, fit.container.free, 5)
        # Checks
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[0], holder)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.free(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
