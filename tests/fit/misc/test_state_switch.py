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
from eos.fit.holder.container import HolderSet
from tests.fit.environment import CachingModule
from tests.fit.fit_testcase import FitTestCase


class TestModuleStateSwitch(FitTestCase):

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.unordered = HolderSet(fit, CachingModule)
        return fit

    def custom_membership_check(self, fit, holder):
        self.assertIn(holder, fit.unordered)

    def test_detached_upwards(self):
        fit = self.make_fit()
        holder = CachingModule(1, State.offline)
        fit.unordered.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        holder.state = State.online
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        st_cleans_between = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_between = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between - st_cleans_before, 0)
        self.assertEqual(module_cleans_between - module_cleans_before, 0)
        # Action
        holder.state = State.overload
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_between, 0)
        self.assertEqual(module_cleans_after - module_cleans_between, 0)
        # Misc
        fit.unordered.remove(holder)
        self.assert_object_buffers_empty(fit)

    def test_detached_downwards(self):
        fit = self.make_fit()
        holder = CachingModule(1, State.overload)
        fit.unordered.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        holder.state = State.active
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        st_cleans_between = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_between = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between - st_cleans_before, 0)
        self.assertEqual(module_cleans_between - module_cleans_before, 0)
        # Action
        holder.state = State.offline
        # Checks
        self.assertEqual(len(fit.lt), 0)
        self.assertEqual(len(fit.rt), 0)
        self.assertEqual(len(fit.st), 0)
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_between, 0)
        self.assertEqual(module_cleans_after - module_cleans_between, 0)
        # Misc
        fit.unordered.remove(holder)
        self.assert_object_buffers_empty(fit)

    def test_attached_upwards(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = CachingModule(1, State.offline)
        fit.unordered.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        holder.state = State.online
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
        st_cleans_between = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_between = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between - st_cleans_before, 1)
        self.assertEqual(module_cleans_between - module_cleans_before, 1)
        # Action
        holder.state = State.overload
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
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_between, 1)
        self.assertEqual(module_cleans_after - module_cleans_between, 1)
        # Misc
        fit.unordered.remove(holder)
        self.assert_object_buffers_empty(fit)

    def test_attached_downwards(self):
        source = Mock(spec_set=Source)
        fit = self.make_fit(source=source)
        holder = CachingModule(1, State.overload)
        fit.unordered.add(holder)
        st_cleans_before = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_before = len(holder._clear_volatile_attrs.mock_calls)
        # Action
        holder.state = State.active
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
        st_cleans_between = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_between = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_between - st_cleans_before, 1)
        self.assertEqual(module_cleans_between - module_cleans_before, 1)
        # Action
        holder.state = State.offline
        # Checks
        self.assertEqual(len(fit.lt), 1)
        self.assertIn(holder, fit.lt)
        self.assertEqual(fit.lt[holder], {State.offline})
        self.assertEqual(len(fit.rt), 1)
        self.assertIn(holder, fit.rt)
        self.assertEqual(fit.rt[holder], {State.offline})
        self.assertEqual(len(fit.st), 1)
        self.assertIn(holder, fit.st)
        self.assertEqual(fit.st[holder], {State.offline})
        st_cleans_after = len(fit.stats._clear_volatile_attrs.mock_calls)
        module_cleans_after = len(holder._clear_volatile_attrs.mock_calls)
        self.assertEqual(st_cleans_after - st_cleans_between, 1)
        self.assertEqual(module_cleans_after - module_cleans_between, 1)
        # Misc
        fit.unordered.remove(holder)
        self.assert_object_buffers_empty(fit)
