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

from eos.fit.item.mixin.side_effect import SideEffectMixin
from eos.fit.messages import EffectsEnabled, EffectsDisabled
from tests.holder_mixin.mixin_testcase import HolderMixinTestCase


class TestHolderMixinSideEffect(HolderMixinTestCase):

    def setUp(self):
        super().setUp()
        self.mixin = self.instantiate_mixin(SideEffectMixin, type_id=None)
        self.mixin._eve_type = Mock()

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
        self.mixin._eve_type.effects = (effect1, effect2, effect3)
        self.mixin.attributes = {2: 0.5, 55: 0.1}
        # Checks
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

    def test_persistence(self):
        # Here we check that when holder._eve_type doesn't have effect
        # which was disabled anymore, everything runs as expected, and
        # when this effect appears again - it's disabled
        # Setup
        effect1 = Mock()
        effect1.id = 22
        effect1.fitting_usage_chance_attribute = 2
        effect2 = Mock()
        effect2.id = 555
        effect2.fitting_usage_chance_attribute = 55
        effect2_repl = Mock()
        effect2_repl.id = 555
        effect2_repl.fitting_usage_chance_attribute = None
        effect3 = Mock()
        effect3.id = 999
        effect3.fitting_usage_chance_attribute = None
        self.mixin.set_side_effect_status(555, False)
        self.mixin.set_side_effect_status(22, False)
        self.mixin._eve_type.effects = (effect1, effect2, effect3)
        self.mixin.attributes = {2: 0.5, 55: 0.1}
        # Action
        self.mixin._eve_type.effects = (effect2_repl, effect3)
        # Checks
        side_effects = self.mixin.side_effects
        # Action
        self.mixin._eve_type.effects = (effect1, effect2, effect3)
        # Checks
        side_effects = self.mixin.side_effects
        self.assertEqual(len(side_effects), 2)
        self.assertIn(22, side_effects)
        side_effect1 = side_effects[22]
        self.assertEqual(side_effect1.effect, effect1)
        self.assertEqual(side_effect1.chance, 0.5)
        self.assertEqual(side_effect1.status, False)
        self.assertIn(555, side_effects)
        side_effect2 = side_effects[555]
        self.assertEqual(side_effect2.effect, effect2)
        self.assertEqual(side_effect2.chance, 0.1)
        self.assertEqual(side_effect2.status, False)

    def test_disabling_attached(self):
        # Setup
        fit_mock = Mock()
        self.mixin._BaseItemMixin__fit = fit_mock
        fit_calls_before = len(fit_mock.mock_calls)
        # Action
        self.mixin.set_side_effect_status(5, False)
        # Checks
        fit_calls_after = len(fit_mock.mock_calls)
        self.assertEqual(fit_calls_after - fit_calls_before, 1)
        fit_call_name, fit_call_args, fit_call_kwargs = fit_mock.mock_calls[-1]
        self.assertEqual(fit_call_name, '_publish')
        self.assertEqual(len(fit_call_args), 1)
        self.assertEqual(len(fit_call_kwargs), 0)
        message = fit_call_args[0]
        self.assertTrue(isinstance(message, EffectsDisabled))
        self.assertIs(message.holder, self.mixin)
        self.assertEqual(message.effects, {5})
        fit_calls_before = len(fit_mock.mock_calls)
        # Action
        self.mixin.set_side_effect_status(5, False)
        # Checks
        fit_calls_after = len(fit_mock.mock_calls)
        self.assertEqual(fit_calls_after - fit_calls_before, 0)

    def test_disabling_detached(self):
        # Setup
        self.mixin._BaseItemMixin__fit = None
        # Action & verification - we just make sure it doesn't crash
        self.mixin.set_side_effect_status(16, False)

    def test_enabling_attached(self):
        # Setup
        fit_mock = Mock()
        self.mixin._BaseItemMixin__fit = fit_mock
        self.mixin.set_side_effect_status(11, False)
        fit_calls_before = len(fit_mock.mock_calls)
        # Action
        self.mixin.set_side_effect_status(11, True)
        # Checks
        fit_calls_after = len(fit_mock.mock_calls)
        self.assertEqual(fit_calls_after - fit_calls_before, 1)
        fit_call_name, fit_call_args, fit_call_kwargs = fit_mock.mock_calls[-1]
        self.assertEqual(fit_call_name, '_publish')
        self.assertEqual(len(fit_call_args), 1)
        self.assertEqual(len(fit_call_kwargs), 0)
        message = fit_call_args[0]
        self.assertTrue(isinstance(message, EffectsEnabled))
        self.assertIs(message.holder, self.mixin)
        self.assertEqual(message.effects, {11})
        fit_calls_before = len(fit_mock.mock_calls)
        # Action
        self.mixin.set_side_effect_status(11, True)
        # Checks
        fit_calls_after = len(fit_mock.mock_calls)
        self.assertEqual(fit_calls_after - fit_calls_before, 0)

    def test_enabling_detached(self):
        # Setup
        self.mixin._BaseItemMixin__fit = None
        self.mixin.set_side_effect_status(99, False)
        # Action & verification - we just make sure it doesn't crash
        self.mixin.set_side_effect_status(99, True)
