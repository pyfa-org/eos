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
from eos.data.source import Source
from eos.fit.holder.container import HolderRestrictedSet
from tests.holder_container.environment import Holder, OtherHolder
from tests.holder_container.container_testcase import ContainerTestCase


class TestContainerRestrictedSet(ContainerTestCase):

    def make_fit(self):
        fit = super().make_fit()
        fit.container = HolderRestrictedSet(fit, Holder)
        return fit

    def custom_membership_check(self, fit, holder):
        self.assertIn(holder, fit.container)

    def assert_fit_buffers_empty(self, fit):
        super().assert_fit_buffers_empty(fit)
        super().assert_object_buffers_empty(fit.container)

    def test_add_none(self):
        fit = self.make_fit()
        # Action
        self.assertRaises(TypeError, fit.container.add, None)
        # Checks
        self.assertEqual(len(fit.container), 0)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_add_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=Holder(1))
        # Action
        fit.container.add(holder)
        # Checks
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[1], holder)
        self.assertIn(holder, fit.container)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit)

    def test_add_holder_type_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=OtherHolder(1))
        # Action
        self.assertRaises(TypeError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_add_holder_value_failure_has_fit(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.overload, spec_set=Holder(1))
        fit_other.container.add(holder)
        # Action
        self.assertRaises(ValueError, fit.container.add, holder)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertEqual(len(fit_other.container), 1)
        self.assertIs(fit_other.container[1], holder)
        self.assertIn(holder, fit_other.container)
        self.assertIs(holder._fit, fit_other)
        # Misc
        fit_other.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)

    def test_add_holder_value_failure_existing_type_id(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=Holder(1))
        holder2 = Mock(_fit=None, _type_id=1, state=State.offline, spec_set=Holder(1))
        fit.container.add(holder1)
        # Action
        self.assertRaises(ValueError, fit.container.add, holder2)
        # Checks
        self.assertEqual(len(fit.container), 1)
        self.assertIs(fit.container[1], holder1)
        self.assertIn(holder1, fit.container)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Misc
        fit.container.remove(holder1)
        self.assert_fit_buffers_empty(fit)

    def test_remove_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.active, spec_set=Holder(1))
        fit.container.add(holder)
        # Action
        fit.container.remove(holder)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_remove_holder_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.overload, spec_set=Holder(1))
        # Action
        self.assertRaises(KeyError, fit.container.remove, holder)
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_delitem_holder(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.active, spec_set=Holder(1))
        fit.container.add(holder)
        # Action
        del fit.container[1]
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_delitem_holder_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, _type_id=1, state=State.active, spec_set=Holder(1))
        fit.container.add(holder)
        # Action
        self.assertRaises(KeyError, fit.container.__delitem__, 3)
        # Checks
        self.assertEqual(len(fit.container), 1)
        self.assertIs(holder._fit, fit)
        # Misc
        fit.container.remove(holder)
        self.assert_fit_buffers_empty(fit)

    def test_clear(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, _type_id=1, state=State.active, spec_set=Holder(1))
        holder2 = Mock(_fit=None, _type_id=2, state=State.online, spec_set=Holder(1))
        fit.container.add(holder1)
        fit.container.add(holder2)
        # Action
        fit.container.clear()
        # Checks
        self.assertEqual(len(fit.container), 0)
        self.assertIsNone(holder1._fit)
        self.assertIsNone(holder2._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)
