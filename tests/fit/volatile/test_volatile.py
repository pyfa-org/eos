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


from unittest.mock import Mock, call

from eos.fit.messages import (
    HolderAdded, HolderRemoved, HolderStateChanged, EffectsEnabled, EffectsDisabled,
    AttrValueChangedOverride, RefreshSource
)
from eos.util.volatile_cache import InheritableVolatileMixin, CooperativeVolatileMixin
from tests.fit.environment import Fit
from tests.fit.fit_testcase import FitTestCase


class TestVolatileData(FitTestCase):

    def test_carrier_builtin(self):
        # Setup
        fit = Fit()
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(RefreshSource())
        # Checks
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Misc
        self.assert_fit_buffers_empty(fit)

    def test_carrier_inheritable(self):
        # Setup
        holder = Mock(spec=InheritableVolatileMixin)
        fit = Fit()
        fit._publish(HolderAdded(holder))
        holder_calls_before = len(holder.mock_calls)
        # Action
        fit._publish(RefreshSource())
        # Checks
        holder_calls_after = len(holder.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 1)
        self.assertEqual(holder.mock_calls[-1], call._clear_volatile_attrs())
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_carrier_cooperative(self):
        # Setup
        holder = Mock(spec=CooperativeVolatileMixin)
        fit = Fit()
        fit._publish(HolderAdded(holder))
        holder_calls_before = len(holder.mock_calls)
        # Action
        fit._publish(RefreshSource())
        # Checks
        holder_calls_after = len(holder.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 1)
        self.assertEqual(holder.mock_calls[-1], call._clear_volatile_attrs())
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_message_holder_added(self):
        # Setup
        holder = Mock(spec=InheritableVolatileMixin)
        holder_other = Mock()
        fit = Fit()
        fit._publish(HolderAdded(holder))
        holder_calls_before = len(holder.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(HolderAdded(holder_other))
        # Checks
        holder_calls_after = len(holder.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 1)
        self.assertEqual(holder.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Misc
        fit._publish(HolderRemoved(holder))
        fit._publish(HolderRemoved(holder_other))
        self.assert_fit_buffers_empty(fit)

    def test_message_holder_removed(self):
        # Setup
        holder = Mock(spec=InheritableVolatileMixin)
        holder_other = Mock()
        fit = Fit()
        fit._publish(HolderAdded(holder))
        fit._publish(HolderAdded(holder_other))
        holder_calls_before = len(holder.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(HolderRemoved(holder_other))
        # Checks
        holder_calls_after = len(holder.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 1)
        self.assertEqual(holder.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_message_holder_state_changed(self):
        # Setup
        holder = Mock(spec=InheritableVolatileMixin)
        fit = Fit()
        fit._publish(HolderAdded(holder))
        holder_calls_before = len(holder.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(HolderStateChanged(None, None, None))
        # Checks
        holder_calls_after = len(holder.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 1)
        self.assertEqual(holder.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_message_effects_enabled(self):
        # Setup
        holder = Mock(spec=InheritableVolatileMixin)
        fit = Fit()
        fit._publish(HolderAdded(holder))
        holder_calls_before = len(holder.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(EffectsEnabled(None, None))
        # Checks
        holder_calls_after = len(holder.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 1)
        self.assertEqual(holder.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_message_effects_disabled(self):
        # Setup
        holder = Mock(spec=InheritableVolatileMixin)
        fit = Fit()
        fit._publish(HolderAdded(holder))
        holder_calls_before = len(holder.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(EffectsDisabled(None, None))
        # Checks
        holder_calls_after = len(holder.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 1)
        self.assertEqual(holder.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_message_override(self):
        # Setup
        holder = Mock(spec=InheritableVolatileMixin)
        fit = Fit()
        fit._publish(HolderAdded(holder))
        holder_calls_before = len(holder.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(AttrValueChangedOverride(None, None))
        # Checks
        holder_calls_after = len(holder.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 1)
        self.assertEqual(holder.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)

    def test_message_refresh_source(self):
        # Setup
        holder = Mock(spec=InheritableVolatileMixin)
        fit = Fit()
        fit._publish(HolderAdded(holder))
        holder_calls_before = len(holder.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(RefreshSource())
        # Checks
        holder_calls_after = len(holder.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(holder_calls_after - holder_calls_before, 1)
        self.assertEqual(holder.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Misc
        fit._publish(HolderRemoved(holder))
        self.assert_fit_buffers_empty(fit)
