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


import math

from eos import Charge
from eos import Fit
from eos import ModuleHigh
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemModuleChargeCycles(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.capacity)
        self.mkattr(attr_id=AttrId.volume)
        self.mkattr(attr_id=AttrId.crystals_get_damaged)

    def test_effect_relay(self):
        fit = Fit()
        effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.target)
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.capacity: 1.0},
                effects=[effect],
                default_effect=effect).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 1.0,
            AttrId.em_dmg: 1.0,
            AttrId.therm_dmg: 1.0,
            AttrId.kin_dmg: 1.0,
            AttrId.expl_dmg: 1.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertEqual(item.cycles_until_reload, math.inf)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_no_default_effect(self):
        fit = Fit()
        effect = self.mkeffect(
            effect_id=EffectId.target_attack,
            category_id=EffectCategoryId.target)
        item = ModuleHigh(
            self.mktype(
                attrs={AttrId.capacity: 1.0},
                effects=[effect]).id,
            state=State.active)
        item.charge = Charge(self.mktype(attrs={
            AttrId.volume: 1.0,
            AttrId.em_dmg: 1.0,
            AttrId.therm_dmg: 1.0,
            AttrId.kin_dmg: 1.0,
            AttrId.expl_dmg: 1.0}).id)
        fit.modules.high.append(item)
        # Verification
        self.assertIsNone(item.cycles_until_reload)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_source_none(self):
        fit = Fit()
        item = ModuleHigh(self.mktype(attrs={
            AttrId.capacity: 100.0,
            AttrId.charge_rate: 2.0}).id)
        item.charge = Charge(self.mktype(attrs={AttrId.volume: 2.0}).id)
        fit.modules.high.append(item)
        fit.source = None
        # Verification
        self.assertIsNone(item.cycles_until_reload)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
