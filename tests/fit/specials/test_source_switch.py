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


from unittest.mock import Mock, call, patch

from eos.const.eos import State
from eos.data.source import Source
from eos.fit.holder.container import HolderSet
from tests.fit.environment import BaseHolder, CachingHolder
from tests.fit.fit_testcase import FitTestCase

@patch('eos.fit.fit.SourceManager')
class TestFitSourceSwitch(FitTestCase):

    def make_fit(self, *args, **kwargs):
        fit = super().make_fit(*args, **kwargs)
        fit.container = HolderSet(fit, BaseHolder)
        return fit

    def test_none_to_none(self, source_mgr):
        source_mgr.default = None
        holder = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        fit = self.make_fit(source=None)
        fit.container.add(holder)
        holder_calls_before = len(holder.mock_calls)
        lt_calls_before = len(fit._link_tracker.mock_calls)
        rt_calls_before = len(fit._restriction_tracker.mock_calls)
        st_calls_before = len(fit.stats.mock_calls)
        sm_calls_before = len(source_mgr.mock_calls)
        # Action
        fit.source = None
        # Checks
        holder_calls_after = len(holder.mock_calls)
        lt_calls_after = len(fit._link_tracker.mock_calls)
        rt_calls_after = len(fit._restriction_tracker.mock_calls)
        st_calls_after = len(fit.stats.mock_calls)
        sm_calls_after = len(source_mgr.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 0)
        self.assertEqual(lt_calls_after - lt_calls_before, 0)
        self.assertEqual(rt_calls_after - rt_calls_before, 0)
        self.assertEqual(st_calls_after - st_calls_before, 0)
        self.assertEqual(sm_calls_after - sm_calls_before, 0)

    def test_none_to_source(self, source_mgr):
        source_mgr.default = None
        source = Mock(spec_set=Source)
        holder = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        fit = self.make_fit(source=None)
        fit.container.add(holder)
        holder_calls_before = len(holder.mock_calls)
        lt_calls_before = len(fit._link_tracker.mock_calls)
        rt_calls_before = len(fit._restriction_tracker.mock_calls)
        st_calls_before = len(fit.stats.mock_calls)
        sm_calls_before = len(source_mgr.mock_calls)
        fit._link_tracker.add_holder.side_effect = lambda h: self.assertIs(h._fit.source, source)
        fit._link_tracker.enable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source)
        fit._restriction_tracker.enable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source)
        fit.stats.enable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source)
        holder._refresh_source.side_effect = lambda: self.assertIs(holder._fit.source, source)
        # Action
        fit.source = source
        # Checks
        holder_calls_after = len(holder.mock_calls)
        lt_calls_after = len(fit._link_tracker.mock_calls)
        rt_calls_after = len(fit._restriction_tracker.mock_calls)
        st_calls_after = len(fit.stats.mock_calls)
        sm_calls_after = len(source_mgr.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 2)
        holder_calls = holder.mock_calls[-2:]
        self.assertIn(call._refresh_source(), holder_calls)
        self.assertIn(call._clear_volatile_attrs(), holder_calls)
        self.assertEqual(lt_calls_after - lt_calls_before, 2)
        self.assertEqual(fit._link_tracker.mock_calls[-2], call.add_holder(holder))
        self.assertEqual(fit._link_tracker.mock_calls[-1], call.enable_states(holder, {State.offline}))
        self.assertEqual(rt_calls_after - rt_calls_before, 1)
        self.assertEqual(fit._restriction_tracker.mock_calls[-1], call.enable_states(holder, {State.offline}))
        self.assertEqual(st_calls_after - st_calls_before, 2)
        self.assertEqual(fit.stats.mock_calls[-2], call._clear_volatile_attrs())
        self.assertEqual(fit.stats.mock_calls[-1], call._enable_states(holder, {State.offline}))
        self.assertEqual(sm_calls_after - sm_calls_before, 0)

    def test_source_to_none(self, source_mgr):
        source_mgr.default = None
        source = Mock(spec_set=Source)
        holder = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        fit = self.make_fit(source=source)
        fit.container.add(holder)
        holder_calls_before = len(holder.mock_calls)
        lt_calls_before = len(fit._link_tracker.mock_calls)
        rt_calls_before = len(fit._restriction_tracker.mock_calls)
        st_calls_before = len(fit.stats.mock_calls)
        sm_calls_before = len(source_mgr.mock_calls)
        fit._link_tracker.disable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source)
        fit._link_tracker.remove_holder.side_effect = lambda h: self.assertIs(h._fit.source, source)
        fit._restriction_tracker.disable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source)
        fit.stats.disable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source)
        # Action
        fit.source = None
        # Checks
        holder_calls_after = len(holder.mock_calls)
        lt_calls_after = len(fit._link_tracker.mock_calls)
        rt_calls_after = len(fit._restriction_tracker.mock_calls)
        st_calls_after = len(fit.stats.mock_calls)
        sm_calls_after = len(source_mgr.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 2)
        holder_calls = holder.mock_calls[-2:]
        self.assertIn(call._refresh_source(), holder_calls)
        self.assertIn(call._clear_volatile_attrs(), holder_calls)
        self.assertEqual(lt_calls_after - lt_calls_before, 2)
        self.assertEqual(fit._link_tracker.mock_calls[-2], call.disable_states(holder, {State.offline}))
        self.assertEqual(fit._link_tracker.mock_calls[-1], call.remove_holder(holder))
        self.assertEqual(rt_calls_after - rt_calls_before, 1)
        self.assertEqual(fit._restriction_tracker.mock_calls[-1], call.disable_states(holder, {State.offline}))
        self.assertEqual(st_calls_after - st_calls_before, 2)
        self.assertEqual(fit.stats.mock_calls[-2], call._disable_states(holder, {State.offline}))
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(sm_calls_after - sm_calls_before, 0)

    def test_source_to_source(self, source_mgr):
        source_mgr.default = None
        source1 = Mock(spec_set=Source)
        source2 = Mock(spec_set=Source)
        holder = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        fit = self.make_fit(source=source1)
        fit.container.add(holder)
        holder_calls_before = len(holder.mock_calls)
        lt_calls_before = len(fit._link_tracker.mock_calls)
        rt_calls_before = len(fit._restriction_tracker.mock_calls)
        st_calls_before = len(fit.stats.mock_calls)
        sm_calls_before = len(source_mgr.mock_calls)
        fit._link_tracker.disable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source1)
        fit._link_tracker.remove_holder.side_effect = lambda h: self.assertIs(h._fit.source, source1)
        fit._link_tracker.add_holder.side_effect = lambda h: self.assertIs(h._fit.source, source2)
        fit._link_tracker.enable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source2)
        fit._restriction_tracker.disable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source1)
        fit._restriction_tracker.enable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source2)
        fit.stats.disable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source1)
        fit.stats.enable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source2)
        holder._refresh_source.side_effect = lambda: self.assertIs(holder._fit.source, source2)
        # Action
        fit.source = source2
        # Checks
        holder_calls_after = len(holder.mock_calls)
        lt_calls_after = len(fit._link_tracker.mock_calls)
        rt_calls_after = len(fit._restriction_tracker.mock_calls)
        st_calls_after = len(fit.stats.mock_calls)
        sm_calls_after = len(source_mgr.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 2)
        holder_calls = holder.mock_calls[-2:]
        self.assertIn(call._refresh_source(), holder_calls)
        self.assertIn(call._clear_volatile_attrs(), holder_calls)
        self.assertEqual(lt_calls_after - lt_calls_before, 4)
        self.assertEqual(fit._link_tracker.mock_calls[-4], call.disable_states(holder, {State.offline}))
        self.assertEqual(fit._link_tracker.mock_calls[-3], call.remove_holder(holder))
        self.assertEqual(fit._link_tracker.mock_calls[-2], call.add_holder(holder))
        self.assertEqual(fit._link_tracker.mock_calls[-1], call.enable_states(holder, {State.offline}))
        self.assertEqual(rt_calls_after - rt_calls_before, 2)
        self.assertEqual(fit._restriction_tracker.mock_calls[-2], call.disable_states(holder, {State.offline}))
        self.assertEqual(fit._restriction_tracker.mock_calls[-1], call.enable_states(holder, {State.offline}))
        self.assertEqual(st_calls_after - st_calls_before, 3)
        self.assertEqual(fit.stats.mock_calls[-3], call._disable_states(holder, {State.offline}))
        self.assertEqual(fit.stats.mock_calls[-2], call._clear_volatile_attrs())
        self.assertEqual(fit.stats.mock_calls[-1], call._enable_states(holder, {State.offline}))
        self.assertEqual(sm_calls_after - sm_calls_before, 0)

    def test_source_to_source_same(self, source_mgr):
        source_mgr.default = None
        source = Mock(spec_set=Source)
        holder = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        fit = self.make_fit(source=source)
        fit.container.add(holder)
        holder_calls_before = len(holder.mock_calls)
        lt_calls_before = len(fit._link_tracker.mock_calls)
        rt_calls_before = len(fit._restriction_tracker.mock_calls)
        st_calls_before = len(fit.stats.mock_calls)
        sm_calls_before = len(source_mgr.mock_calls)
        # Action
        fit.source = source
        # Checks
        holder_calls_after = len(holder.mock_calls)
        lt_calls_after = len(fit._link_tracker.mock_calls)
        rt_calls_after = len(fit._restriction_tracker.mock_calls)
        st_calls_after = len(fit.stats.mock_calls)
        sm_calls_after = len(source_mgr.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 0)
        self.assertEqual(lt_calls_after - lt_calls_before, 0)
        self.assertEqual(rt_calls_after - rt_calls_before, 0)
        self.assertEqual(st_calls_after - st_calls_before, 0)
        self.assertEqual(sm_calls_after - sm_calls_before, 0)

    def test_none_to_literal_source(self, source_mgr):
        source = Mock(spec_set=Source)
        source_mgr.get.side_effect = lambda alias: source if alias == 'src_alias' else None
        source_mgr.default = None
        holder = Mock(_fit=None, state=State.offline, spec_set=CachingHolder(1))
        fit = self.make_fit(source=None)
        fit.container.add(holder)
        holder_calls_before = len(holder.mock_calls)
        lt_calls_before = len(fit._link_tracker.mock_calls)
        rt_calls_before = len(fit._restriction_tracker.mock_calls)
        st_calls_before = len(fit.stats.mock_calls)
        sm_calls_before = len(source_mgr.mock_calls)
        fit._link_tracker.add_holder.side_effect = lambda h: self.assertIs(h._fit.source, source)
        fit._link_tracker.enable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source)
        fit._restriction_tracker.enable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source)
        fit.stats.enable_states.side_effect = lambda h, s: self.assertIs(h._fit.source, source)
        holder._refresh_source.side_effect = lambda: self.assertIs(holder._fit.source, source)
        # Action
        fit.source = 'src_alias'
        # Checks
        holder_calls_after = len(holder.mock_calls)
        lt_calls_after = len(fit._link_tracker.mock_calls)
        rt_calls_after = len(fit._restriction_tracker.mock_calls)
        st_calls_after = len(fit.stats.mock_calls)
        sm_calls_after = len(source_mgr.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 2)
        holder_calls = holder.mock_calls[-2:]
        self.assertIn(call._refresh_source(), holder_calls)
        self.assertIn(call._clear_volatile_attrs(), holder_calls)
        self.assertEqual(lt_calls_after - lt_calls_before, 2)
        self.assertEqual(fit._link_tracker.mock_calls[-2], call.add_holder(holder))
        self.assertEqual(fit._link_tracker.mock_calls[-1], call.enable_states(holder, {State.offline}))
        self.assertEqual(rt_calls_after - rt_calls_before, 1)
        self.assertEqual(fit._restriction_tracker.mock_calls[-1], call.enable_states(holder, {State.offline}))
        self.assertEqual(st_calls_after - st_calls_before, 2)
        self.assertEqual(fit.stats.mock_calls[-2], call._clear_volatile_attrs())
        self.assertEqual(fit.stats.mock_calls[-1], call._enable_states(holder, {State.offline}))
        self.assertEqual(sm_calls_after - sm_calls_before, 1)
        self.assertEqual(source_mgr.mock_calls[-1], call.get('src_alias'))
