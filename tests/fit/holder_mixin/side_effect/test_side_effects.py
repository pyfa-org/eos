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


from unittest.mock import Mock, call

from eos.fit.holder.mixin.side_effect import SideEffectMixin
from tests.fit.fit_testcase import FitTestCase


class TestHolderMixinSideEffect(FitTestCase):

    def setUp(self):
        super().setUp()
        self.mixin = SideEffectMixin(type_id=None)
        self.mixin.item = Mock()
        self.mixin.item.effects = ()

    def test_data_attached(self):
        pass

    def test_data_detached(self):
        pass

    def test_disabling_attached(self):
        # Setup
        fit_mock = Mock()
        self.mixin._HolderBase__fit = fit_mock
        fit_calls_before = len(fit_mock.mock_calls)
        # Action
        self.mixin.set_side_effect_status(5, False)
        # Verification
        fit_calls_after = len(fit_mock.mock_calls)
        self.assertEqual(fit_calls_after - fit_calls_before, 2)
        fit_calls = fit_mock.mock_calls[-2:]
        self.assertIn(call._request_volatile_cleanup(), fit_calls)
        self.assertIn(call._link_tracker.disable_effects(self.mixin, {5}), fit_calls)

    def test_disabling_detached(self):
        # Setup
        self.mixin._HolderBase__fit = None
        # Action & verification - we just make sure it doesn't crash
        self.mixin.set_side_effect_status(16, False)

    def test_enabling_attached(self):
        # Setup
        fit_mock = Mock()
        self.mixin._HolderBase__fit = fit_mock
        self.mixin.set_side_effect_status(11, False)
        fit_calls_before = len(fit_mock.mock_calls)
        # Action
        self.mixin.set_side_effect_status(11, True)
        # Verification
        fit_calls_after = len(fit_mock.mock_calls)
        self.assertEqual(fit_calls_after - fit_calls_before, 2)
        fit_calls = fit_mock.mock_calls[-2:]
        self.assertIn(call._request_volatile_cleanup(), fit_calls)
        self.assertIn(call._link_tracker.enable_effects(self.mixin, {11}), fit_calls)

    def test_enabling_detached(self):
        # Setup
        self.mixin._HolderBase__fit = None
        self.mixin.set_side_effect_status(99, False)
        # Action & verification - we just make sure it doesn't crash
        self.mixin.set_side_effect_status(99, True)
