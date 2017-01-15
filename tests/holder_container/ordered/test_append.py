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
from eos.fit.holder.container import HolderList
from tests.holder_container.environment import Holder, OtherHolder
from tests.holder_container.container_testcase import ContainerTestCase


class TestContainerOrderedAppend(ContainerTestCase):

    def make_fit(self):
        fit = super().make_fit()
        fit.container = HolderList(fit, Holder)
        return fit

    def assert_fit_buffers_empty(self, fit):
        super().assert_fit_buffers_empty(fit)
        super().assert_object_buffers_empty(fit.container)

    def custom_membership_check(self, fit, holder):
        self.assertIn(holder, fit.container)

    def test_none(self):
        fit = self.make_fit()
        # Action
        self.assertRaises(TypeError, fit.container.append, None)
        # Checks
        self.assertIs(len(fit.container), 0)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_holder(self):
        fit = self.make_fit()
        holder1 = Mock(_fit=None, state=State.active, spec_set=Holder(1))
        holder2 = Mock(_fit=None, state=State.offline, spec_set=Holder(1))
        # Action
        fit.container.append(holder1)
        # Checks
        self.assertIs(len(fit.container), 1)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(holder1._fit, fit)
        self.assertIsNone(holder2._fit)
        # Action
        fit.container.append(holder2)
        # Checks
        self.assertIs(len(fit.container), 2)
        self.assertIs(fit.container[0], holder1)
        self.assertIs(fit.container[1], holder2)
        self.assertIs(holder1._fit, fit)
        self.assertIs(holder2._fit, fit)
        # Misc
        fit.container.remove(holder1)
        fit.container.remove(holder2)
        self.assert_fit_buffers_empty(fit)

    def test_holder_type_failure(self):
        fit = self.make_fit()
        holder = Mock(_fit=None, state=State.overload, spec_set=OtherHolder(1))
        # Action
        self.assertRaises(TypeError, fit.container.append, holder)
        # Checks
        self.assertIs(len(fit.container), 0)
        self.assertIsNone(holder._fit)
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_holder_value_failure(self):
        fit = self.make_fit()
        fit_other = self.make_fit()
        holder = Mock(_fit=None, state=State.overload, spec_set=Holder(1))
        fit_other.container.append(holder)
        # Action
        self.assertRaises(ValueError, fit.container.append, holder)
        # Checks
        self.assertIs(len(fit.container), 0)
        self.assertIs(len(fit_other.container), 1)
        self.assertIs(fit_other.container[0], holder)
        self.assertIs(holder._fit, fit_other)
        # Misc
        fit_other.container.remove(holder)
        self.assert_fit_buffers_empty(fit)
        self.assert_fit_buffers_empty(fit_other)