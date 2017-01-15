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
from eos.fit.holder.container import HolderSet
from eos.fit.messages import HolderAdded, HolderRemoved
from tests.holder_container.environment import Fit, Holder, OtherHolder
from tests.holder_container.container_testcase import ContainerTestCase


class TestContainerSet(ContainerTestCase):

    def make_fit(self):
        assertions = {
            HolderAdded: lambda f, m: self.assertIn(m.holder, f.container),
            HolderRemoved: lambda f, m: self.assertIn(m.holder, f.container)
        }
        fit = Fit(self, message_assertions=assertions)
        fit.container = HolderSet(fit, Holder)
        return fit

    def test_add_none(self):
        fit = self.make_fit()
        # Action
        with self.run_fit_assertions(fit):
            self.assertRaises(TypeError, fit.container.add, None)
        # Checks
        self.assertEqual(len(fit.container), 0)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_add_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.offline, spec_set=Holder(1))
        # Action
        with self.run_fit_assertions(fit):
            fit.container.add(holder)
        # Checks
        self.assertEqual(len(fit.container), 1)
        self.assertIn(holder, fit.container)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_add_holder_type_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.offline, spec_set=OtherHolder(1))
        # Action
        with self.run_fit_assertions(fit):
            self.assertRaises(TypeError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_add_holder_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder = Mock(_fit=None, state=State.overload, spec_set=Holder(1))
        fit_other.container.add(holder)
        # Action
        with self.run_fit_assertions(fit):
            self.assertRaises(ValueError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertEqual(len(fit_other.container), 1)
        self.assertIn(holder, fit_other.container)
        self.assertIs(holder._fit, fit_other)
        # Misc
        fit_other.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
        self.assert_fit_buffers_empty(fit_other)
        self.assert_object_buffers_empty(fit_other.container)

    def test_remove_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        fit.container.add(holder)
        # Action
        with self.run_fit_assertions(fit):
            fit.container.remove(holder)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_remove_holder_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.overload, spec_set=Holder(1))
        # Action
        with self.run_fit_assertions(fit):
            self.assertRaises(KeyError, fit.container.remove, holder)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)

    def test_clear(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.online, spec_set=Holder(1))
        fit.container.add(holder1)
        fit.container.add(holder2)
        # Action
        with self.run_fit_assertions(fit):
            fit.container.clear()
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
        self.assert_object_buffers_empty(fit.container)
