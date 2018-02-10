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


from eos import Ship
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestOneItemManyModifiers(CalculatorTestCase):
    """Make sure that similar yet different modifications are applied.

    This test set appeared after there was a bug in eos where multiple
    modifications coming from the same item were applied as just one
    modification, with condition that operator and value were the same.
    """

    def test_same_item(self):
        # Real scenario - capital ships boost their agility via proxy attrs
        tgt_attr = self.mkattr()
        src_attr1 = self.mkattr()
        src_attr2 = self.mkattr()
        modifier1 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr1.id)
        modifier2 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr2.id)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier1])
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier2])
        item = Ship(self.mktype(
            attrs={src_attr1.id: 20, src_attr2.id: 20, tgt_attr.id: 100},
            effects=(effect1, effect2)).id)
        self.fit.ship = item
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)

    def test_same_item_effect(self):
        tgt_attr = self.mkattr()
        src_attr1 = self.mkattr()
        src_attr2 = self.mkattr()
        modifier1 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr1.id)
        modifier2 = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr2.id)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier1, modifier2])
        item = Ship(self.mktype(
            attrs={src_attr1.id: 20, src_attr2.id: 20, tgt_attr.id: 100},
            effects=[effect1]).id)
        self.fit.ship = item
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)

    def test_same_item_modifier(self):
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        item = Ship(self.mktype(
            attrs={src_attr.id: 20, tgt_attr.id: 100},
            effects=(effect1, effect2)).id)
        self.fit.ship = item
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)

    def test_same_item_effect_modifier(self):
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier = self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=ModDomain.self,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier])
        item = Ship(self.mktype(
            attrs={src_attr.id: 20, tgt_attr.id: 100},
            effects=[effect1]).id)
        self.fit.ship = item
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)
