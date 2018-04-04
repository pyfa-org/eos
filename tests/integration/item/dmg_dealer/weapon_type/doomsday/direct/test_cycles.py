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


import math

from eos import Fit
from eos import ModuleHigh
from eos import State
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemDmgDoomsdayDirectCycles(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.cycle_attr = self.mkattr()
        self.effect_amarr = self.mkeffect(
            effect_id=EffectId.super_weapon_amarr,
            category_id=EffectCategoryId.target,
            duration_attr_id=self.cycle_attr.id)

    def test_generic(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                effects=[self.effect_amarr],
                default_effect=self.effect_amarr).id,
            state=State.active)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.cycles_until_reload, math.inf)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
