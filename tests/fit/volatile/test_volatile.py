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

from eos.fit.item.mixin.base import BaseItemMixin
from eos.fit.message import (
    ItemAdded, ItemRemoved, ItemStateChanged, EffectsEnabled, EffectsDisabled,
    SkillLevelChanged, RefreshSource
)
from eos.util.volatile_cache import InheritableVolatileMixin, CooperativeVolatileMixin
from tests.fit.environment import Fit
from tests.fit.fit_testcase import FitTestCase


class TestVolatileInheritable(BaseItemMixin, InheritableVolatileMixin):

    _parent_modifier_domain = None
    _owner_modifiable = None


class TestVolatileCooperative(BaseItemMixin, CooperativeVolatileMixin):

    _parent_modifier_domain = None
    _owner_modifiable = None


class ItemOther(BaseItemMixin):

    _parent_modifier_domain = None
    _owner_modifiable = None


class TestVolatileData(FitTestCase):

    def test_carrier_builtin(self):
        # Setup
        fit = Fit()
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(RefreshSource())
        # Verification
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Cleanup
        self.assert_fit_buffers_empty(fit)

    def test_carrier_inheritable(self):
        # Setup
        item = Mock(spec=TestVolatileInheritable(1))
        fit = Fit()
        fit._publish(ItemAdded(item))
        item_calls_before = len(item.mock_calls)
        # Action
        fit._publish(RefreshSource())
        # Verification
        item_calls_after = len(item.mock_calls)
        self.assertEqual(item_calls_after - item_calls_before, 1)
        self.assertEqual(item.mock_calls[-1], call._clear_volatile_attrs())
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_carrier_cooperative(self):
        # Setup
        item = Mock(spec=TestVolatileCooperative(1))
        fit = Fit()
        fit._publish(ItemAdded(item))
        item_calls_before = len(item.mock_calls)
        # Action
        fit._publish(RefreshSource())
        # Verification
        item_calls_after = len(item.mock_calls)
        self.assertEqual(item_calls_after - item_calls_before, 1)
        self.assertEqual(item.mock_calls[-1], call._clear_volatile_attrs())
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_message_item_added(self):
        # Setup
        item = Mock(spec=TestVolatileInheritable(1))
        item_other = Mock(spec=ItemOther(2))
        fit = Fit()
        fit._publish(ItemAdded(item))
        item_calls_before = len(item.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(ItemAdded(item_other))
        # Verification
        item_calls_after = len(item.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(item_calls_after - item_calls_before, 1)
        self.assertEqual(item.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Cleanup
        fit._publish(ItemRemoved(item))
        fit._publish(ItemRemoved(item_other))
        self.assert_fit_buffers_empty(fit)

    def test_message_item_removed(self):
        # Setup
        item = Mock(spec=TestVolatileInheritable(1))
        item_other = Mock(spec=ItemOther(2))
        fit = Fit()
        fit._publish(ItemAdded(item))
        fit._publish(ItemAdded(item_other))
        item_calls_before = len(item.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(ItemRemoved(item_other))
        # Verification
        item_calls_after = len(item.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(item_calls_after - item_calls_before, 1)
        self.assertEqual(item.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_message_item_state_changed(self):
        # Setup
        item = Mock(spec=TestVolatileInheritable(1))
        fit = Fit()
        fit._publish(ItemAdded(item))
        item_calls_before = len(item.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(ItemStateChanged(None, None, None))
        # Verification
        item_calls_after = len(item.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(item_calls_after - item_calls_before, 1)
        self.assertEqual(item.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_message_effects_enabled(self):
        # Setup
        item = Mock(spec=TestVolatileInheritable(1))
        fit = Fit()
        fit._publish(ItemAdded(item))
        item_calls_before = len(item.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(EffectsEnabled(None, None))
        # Verification
        item_calls_after = len(item.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(item_calls_after - item_calls_before, 1)
        self.assertEqual(item.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_message_effects_disabled(self):
        # Setup
        item = Mock(spec=TestVolatileInheritable(1))
        fit = Fit()
        fit._publish(ItemAdded(item))
        item_calls_before = len(item.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(EffectsDisabled(None, None))
        # Verification
        item_calls_after = len(item.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(item_calls_after - item_calls_before, 1)
        self.assertEqual(item.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_message_skill_level(self):
        # Setup
        item = Mock(spec=TestVolatileInheritable(1))
        fit = Fit()
        fit._publish(ItemAdded(item))
        item_calls_before = len(item.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(SkillLevelChanged(None))
        # Verification
        item_calls_after = len(item.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(item_calls_after - item_calls_before, 1)
        self.assertEqual(item.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)

    def test_message_refresh_source(self):
        # Setup
        item = Mock(spec=TestVolatileInheritable(1))
        fit = Fit()
        fit._publish(ItemAdded(item))
        item_calls_before = len(item.mock_calls)
        ss_calls_before = len(fit.stats.mock_calls)
        # Action
        fit._publish(RefreshSource())
        # Verification
        item_calls_after = len(item.mock_calls)
        ss_calls_after = len(fit.stats.mock_calls)
        self.assertEqual(item_calls_after - item_calls_before, 1)
        self.assertEqual(item.mock_calls[-1], call._clear_volatile_attrs())
        self.assertEqual(ss_calls_after - ss_calls_before, 1)
        self.assertEqual(fit.stats.mock_calls[-1], call._clear_volatile_attrs())
        # Cleanup
        fit._publish(ItemRemoved(item))
        self.assert_fit_buffers_empty(fit)
