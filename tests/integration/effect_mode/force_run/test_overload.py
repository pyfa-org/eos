# ==============================================================================
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
# ==============================================================================


from eos import *
from eos.const.eve import EffectCategoryId
from tests.integration.effect_mode.effect_mode_testcase import (
    EffectModeTestCase)


class TestForceRunOverload(EffectModeTestCase):

    def test_started_on_add(self):
        effect = self.mkeffect(
            category_id=EffectCategoryId.overload,
            modifiers=[self.modifier])
        item = ModuleHigh(
            self.mktype(
                attrs={self.tgt_attr.id: 10, self.src_attr.id: 2},
                effects=[effect]).id,
            state=State.overload)
        item.set_effect_mode(effect.id, EffectMode.force_run)
        # Action
        self.fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 12)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_started_on_state_switch(self):
        effect = self.mkeffect(
            category_id=EffectCategoryId.overload,
            modifiers=[self.modifier])
        item = ModuleHigh(
            self.mktype(
                attrs={self.tgt_attr.id: 10, self.src_attr.id: 2},
                effects=[effect]).id,
            state=State.active)
        item.set_effect_mode(effect.id, EffectMode.force_run)
        self.fit.modules.high.append(item)
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 12)
        # Action
        item.state = State.overload
        # Verification
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 12)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_started_on_mode_switch(self):
        effect = self.mkeffect(
            category_id=EffectCategoryId.overload,
            modifiers=[self.modifier])
        item = ModuleHigh(
            self.mktype(
                attrs={self.tgt_attr.id: 10, self.src_attr.id: 2},
                effects=[effect]).id,
            state=State.overload)
        item.set_effect_mode(effect.id, EffectMode.force_stop)
        self.fit.modules.high.append(item)
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 10)
        # Action
        item.set_effect_mode(effect.id, EffectMode.force_run)
        # Verification
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 12)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_started_insufficient_state(self):
        effect = self.mkeffect(
            category_id=EffectCategoryId.overload,
            modifiers=[self.modifier])
        item = ModuleHigh(
            self.mktype(
                attrs={self.tgt_attr.id: 10, self.src_attr.id: 2},
                effects=[effect]).id,
            state=State.active)
        item.set_effect_mode(effect.id, EffectMode.force_run)
        # Action
        self.fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 12)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
