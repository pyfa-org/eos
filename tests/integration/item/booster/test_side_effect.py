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


from eos import Booster
from eos import Fit
from eos import NoSuchSideEffectError
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.item.testcase import ItemMixinTestCase


class TestItemBoosterSideEffect(ItemMixinTestCase):

    def test_data(self):
        # Setup
        chance_attr1 = self.mkattr()
        chance_attr2 = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=chance_attr2.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            fitting_usage_chance_attr_id=chance_attr1.id)
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            fitting_usage_chance_attr_id=chance_attr2.id)
        effect3 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        fit = Fit()
        item = Booster(self.mktype(
            attrs={
                chance_attr1.id: 0.5,
                chance_attr2.id: 0.1,
                src_attr.id: -25},
            effects=(effect1, effect2, effect3)).id)
        fit.boosters.add(item)
        item.set_side_effect_status(effect2.id, True)
        # Verification
        side_effects = item.side_effects
        self.assertEqual(len(side_effects), 2)
        self.assertIn(effect1.id, side_effects)
        side_effect1 = side_effects[effect1.id]
        self.assertAlmostEqual(side_effect1.chance, 0.5)
        self.assertIs(side_effect1.status, False)
        self.assertIn(effect2.id, side_effects)
        side_effect2 = side_effects[effect2.id]
        self.assertAlmostEqual(side_effect2.chance, 0.075)
        self.assertIs(side_effect2.status, True)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_data_item_not_loaded(self):
        # Setup
        fit = Fit()
        item = Booster(self.allocate_type_id())
        fit.boosters.add(item)
        # Verification
        self.assertEqual(len(item.side_effects), 0)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_enabling(self):
        # Setup
        chance_attr = self.mkattr()
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            fitting_usage_chance_attr_id=chance_attr.id,
            modifiers=[modifier])
        fit = Fit()
        item = Booster(self.mktype(
            attrs={
                chance_attr.id: 0.5,
                tgt_attr.id: 100,
                src_attr.id: 1.2},
            effects=[effect]).id)
        fit.boosters.add(item)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 100)
        # Action
        item.set_side_effect_status(effect.id, True)
        # Verification
        self.assertIs(item.side_effects[effect.id].status, True)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 120)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_enabling_not_side_effect(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        fit = Fit()
        item = Booster(self.mktype(
            attrs={tgt_attr.id: 100, src_attr.id: 1.2},
            effects=[effect]).id)
        fit.boosters.add(item)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 120)
        # Verification
        with self.assertRaises(NoSuchSideEffectError):
            item.set_side_effect_status(effect.id, True)
        self.assertNotIn(effect.id, item.side_effects)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 120)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_enabling_item_not_loaded(self):
        # Setup
        effect_id = self.allocate_effect_id()
        fit = Fit()
        item = Booster(self.allocate_type_id())
        fit.boosters.add(item)
        # Verification
        with self.assertRaises(NoSuchSideEffectError):
            item.set_side_effect_status(effect_id, True)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_disabling(self):
        # Setup
        chance_attr = self.mkattr()
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            fitting_usage_chance_attr_id=chance_attr.id,
            modifiers=[modifier])
        fit = Fit()
        item = Booster(self.mktype(
            attrs={
                chance_attr.id: 0.5,
                tgt_attr.id: 100,
                src_attr.id: 1.2},
            effects=[effect]).id)
        fit.boosters.add(item)
        item.set_side_effect_status(effect.id, True)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 120)
        # Action
        item.set_side_effect_status(effect.id, False)
        # Verification
        self.assertIs(item.side_effects[effect.id].status, False)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 100)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_disabling_not_side_effect(self):
        # Setup
        src_attr = self.mkattr()
        tgt_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        fit = Fit()
        item = Booster(self.mktype(
            attrs={tgt_attr.id: 100, src_attr.id: 1.2},
            effects=[effect]).id)
        fit.boosters.add(item)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 120)
        # Verification
        with self.assertRaises(NoSuchSideEffectError):
            item.set_side_effect_status(effect.id, False)
        self.assertNotIn(effect.id, item.side_effects)
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 120)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)

    def test_disabling_item_not_loaded(self):
        # Setup
        effect_id = self.allocate_effect_id()
        fit = Fit()
        item = Booster(self.allocate_type_id())
        fit.boosters.add(item)
        # Verification
        with self.assertRaises(NoSuchSideEffectError):
            item.set_side_effect_status(effect_id, False)
        # Cleanup
        self.assert_solsys_buffers_empty(fit.solar_system)
        self.assert_log_entries(0)
