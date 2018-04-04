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


from eos import Charge
from eos import Fit
from eos import ModuleHigh
from eos import State
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemDmgMissileAutotargetingVolley(ItemMixinTestCase):

    def setUp(self):
        ItemMixinTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.capacity)
        self.mkattr(attr_id=AttrId.volume)
        self.mkattr(attr_id=AttrId.charge_rate)
        self.mkattr(attr_id=AttrId.reload_time)
        self.mkattr(attr_id=AttrId.em_dmg)
        self.mkattr(attr_id=AttrId.therm_dmg)
        self.mkattr(attr_id=AttrId.kin_dmg)
        self.mkattr(attr_id=AttrId.expl_dmg)
        self.cycle_attr = self.mkattr()
        self.effect_item = self.mkeffect(
            effect_id=EffectId.use_missiles,
            category_id=EffectCategoryId.active,
            duration_attr_id=self.cycle_attr.id)
        self.effect_charge = self.mkeffect(
            effect_id=EffectId.fof_missile_launching,
            category_id=EffectCategoryId.active)

    def test_generic(self):
        fit = Fit()
        item = ModuleHigh(
            self.mktype(
                attrs={
                    AttrId.capacity: 2.0,
                    self.cycle_attr.id: 2000,
                    AttrId.charge_rate: 1.0,
                    AttrId.reload_time: 10000},
                effects=[self.effect_item],
                default_effect=self.effect_item).id,
            state=State.active)
        item.charge = Charge(self.mktype(
            attrs={
                AttrId.volume: 0.1,
                AttrId.em_dmg: 5.2,
                AttrId.therm_dmg: 6.3,
                AttrId.kin_dmg: 7.4,
                AttrId.expl_dmg: 8.5},
            effects=[self.effect_charge],
            default_effect=self.effect_charge).id)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_volley()
        self.assertAlmostEqual(volley.em, 5.2)
        self.assertAlmostEqual(volley.thermal, 6.3)
        self.assertAlmostEqual(volley.kinetic, 7.4)
        self.assertAlmostEqual(volley.explosive, 8.5)
        self.assertAlmostEqual(volley.total, 27.4)
        # Cleanup
        self.assert_fit_buffers_empty(fit)
        self.assertEqual(len(self.get_log()), 0)
