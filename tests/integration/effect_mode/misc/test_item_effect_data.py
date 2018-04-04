# ==============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2018 Anton Vorobyov
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
# ==============================================================================


from eos import EffectMode
from eos import ModuleHigh
from eos import State
from eos.const.eve import EffectCategoryId
from tests.integration.effect_mode.testcase import EffectModeTestCase


class TestItemEffectData(EffectModeTestCase):

    def test_effect(self):
        effect = self.mkeffect(category_id=EffectCategoryId.passive)
        item = ModuleHigh(self.mktype(effects=[effect]).id, state=State.offline)
        self.fit.modules.high.append(item)
        item.set_effect_mode(effect.id, EffectMode.full_compliance)
        # Verification
        self.assertEqual(len(item.effects), 1)
        self.assertIn(effect.id, item.effects)
        effect_data = item.effects[effect.id]
        self.assertIs(effect_data.effect, effect)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_mode_full_compliance(self):
        effect = self.mkeffect(category_id=EffectCategoryId.passive)
        item = ModuleHigh(self.mktype(effects=[effect]).id, state=State.offline)
        self.fit.modules.high.append(item)
        item.set_effect_mode(effect.id, EffectMode.full_compliance)
        # Verification
        self.assertEqual(len(item.effects), 1)
        self.assertIn(effect.id, item.effects)
        effect_data = item.effects[effect.id]
        self.assertEqual(effect_data.mode, EffectMode.full_compliance)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_mode_force_run(self):
        effect = self.mkeffect(category_id=EffectCategoryId.passive)
        item = ModuleHigh(self.mktype(effects=[effect]).id, state=State.offline)
        self.fit.modules.high.append(item)
        item.set_effect_mode(effect.id, EffectMode.force_run)
        # Verification
        self.assertEqual(len(item.effects), 1)
        self.assertIn(effect.id, item.effects)
        effect_data = item.effects[effect.id]
        self.assertEqual(effect_data.mode, EffectMode.force_run)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_status_running(self):
        effect = self.mkeffect(category_id=EffectCategoryId.passive)
        item = ModuleHigh(self.mktype(effects=[effect]).id, state=State.offline)
        self.fit.modules.high.append(item)
        item.set_effect_mode(effect.id, EffectMode.full_compliance)
        # Verification
        self.assertEqual(len(item.effects), 1)
        self.assertIn(effect.id, item.effects)
        effect_data = item.effects[effect.id]
        self.assertIs(effect_data.status, True)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_status_stopped(self):
        effect = self.mkeffect(category_id=EffectCategoryId.passive)
        item = ModuleHigh(self.mktype(effects=[effect]).id, state=State.offline)
        self.fit.modules.high.append(item)
        item.set_effect_mode(effect.id, EffectMode.force_stop)
        # Verification
        self.assertEqual(len(item.effects), 1)
        self.assertIn(effect.id, item.effects)
        effect_data = item.effects[effect.id]
        self.assertIs(effect_data.status, False)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_multiple(self):
        effect1 = self.mkeffect(category_id=EffectCategoryId.passive)
        effect2 = self.mkeffect(category_id=EffectCategoryId.online)
        effect3 = self.mkeffect(category_id=EffectCategoryId.active)
        item = ModuleHigh(
            self.mktype(
                effects=(effect1, effect2, effect3),
                default_effect=effect3).id,
            state=State.online)
        self.fit.modules.high.append(item)
        item.set_effect_mode(effect1.id, EffectMode.state_compliance)
        item.set_effect_mode(effect2.id, EffectMode.full_compliance)
        item.set_effect_mode(effect3.id, EffectMode.force_run)
        # Verification
        self.assertEqual(len(item.effects), 3)
        self.assertIn(effect1.id, item.effects)
        effect1_data = item.effects[effect1.id]
        self.assertIs(effect1_data.effect, effect1)
        self.assertEqual(effect1_data.mode, EffectMode.state_compliance)
        self.assertIs(effect1_data.status, True)
        effect2_data = item.effects[effect2.id]
        self.assertIs(effect2_data.effect, effect2)
        self.assertEqual(effect2_data.mode, EffectMode.full_compliance)
        self.assertIs(effect2_data.status, False)
        effect3_data = item.effects[effect3.id]
        self.assertIs(effect3_data.effect, effect3)
        self.assertEqual(effect3_data.mode, EffectMode.force_run)
        self.assertIs(effect3_data.status, True)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_item_not_loaded(self):
        item = ModuleHigh(self.allocate_type_id(), state=State.offline)
        self.fit.modules.high.append(item)
        # Verification
        self.assertEqual(len(item.effects), 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
