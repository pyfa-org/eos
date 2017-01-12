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

from eos.fit.holder.mixin.side_effect import SideEffectMixin
from tests.fit.fit_testcase import FitTestCase


class TestHolderMixinSideEffect(FitTestCase):

    def setUp(self):
        super().setUp()
        self.mixin = SideEffectMixin(type_id=None)
        self.mixin.item = Mock()

    def test_data(self):
        # Setup
        effect1 = Mock()
        effect1.id = 22
        effect1.fitting_usage_chance_attribute = 2
        effect2 = Mock()
        effect2.id = 555
        effect2.fitting_usage_chance_attribute = 55
        effect3 = Mock()
        effect3.id = 999
        effect3.fitting_usage_chance_attribute = None
        self.mixin.set_side_effect_status(555, False)
        self.mixin.item.effects = (effect1, effect2, effect3)
        self.mixin.attributes = {2: 0.5, 55: 0.1}
        # Verification
        side_effects = self.mixin.side_effects
        self.assertEqual(len(side_effects), 2)
        self.assertIn(22, side_effects)
        side_effect1 = side_effects[22]
        self.assertEqual(side_effect1.effect, effect1)
        self.assertEqual(side_effect1.chance, 0.5)
        self.assertEqual(side_effect1.status, True)
        self.assertIn(555, side_effects)
        side_effect2 = side_effects[555]
        self.assertEqual(side_effect2.effect, effect2)
        self.assertEqual(side_effect2.chance, 0.1)
        self.assertEqual(side_effect2.status, False)

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
        fit_calls_before = len(fit_mock.mock_calls)
        # Action
        self.mixin.set_side_effect_status(5, False)
        # Verification
        fit_calls_after = len(fit_mock.mock_calls)
        self.assertEqual(fit_calls_after - fit_calls_before, 0)

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
        fit_calls_before = len(fit_mock.mock_calls)
        # Action
        self.mixin.set_side_effect_status(11, True)
        # Verification
        fit_calls_after = len(fit_mock.mock_calls)
        self.assertEqual(fit_calls_after - fit_calls_before, 0)

    def test_enabling_detached(self):
        # Setup
        self.mixin._HolderBase__fit = None
        self.mixin.set_side_effect_status(99, False)
        # Action & verification - we just make sure it doesn't crash
        self.mixin.set_side_effect_status(99, True)
