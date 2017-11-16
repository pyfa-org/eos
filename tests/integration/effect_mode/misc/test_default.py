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


class TestDefaultMode(EffectModeTestCase):

    def test_offline(self):
        # Offline effects should be running by default in full compliance mode
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[self.modifier])
        item = ModuleHigh(
            self.mktype(
                attrs={self.tgt_attr.id: 10, self.src_attr.id: 2},
                effects=[effect]).id,
            state=State.offline)
        # Action
        self.fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 12)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_offline_chance_based(self):
        # Chance-based offline effects should be stopped in full compliance mode
        chance_attr = self.mkattr()
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            fitting_usage_chance_attr_id=chance_attr.id,
            modifiers=[self.modifier])
        item = ModuleHigh(
            self.mktype(
                attrs={
                    self.tgt_attr.id: 10,
                    self.src_attr.id: 2,
                    chance_attr.id: 1},
                effects=[effect]).id,
            state=State.offline)
        # Action
        self.fit.modules.high.append(item)
        # Verification
        self.assertAlmostEqual(item.attrs[self.tgt_attr.id], 10)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
