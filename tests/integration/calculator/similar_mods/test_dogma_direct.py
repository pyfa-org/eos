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


from eos import ModuleHigh
from eos import Ship
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestSimilarModifiersDogma(CalculatorTestCase):

    def make_modifier(self, domain, src_attr, tgt_attr):
        return self.mkmod(
            tgt_filter=ModTgtFilter.item,
            tgt_domain=domain,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)

    def test_self_same_item(self):
        # Real scenario - capital ships boost their agility via proxy attrs
        # Setup
        tgt_attr = self.mkattr()
        src_attr1 = self.mkattr()
        src_attr2 = self.mkattr()
        modifier1 = self.make_modifier(ModDomain.self, src_attr1, tgt_attr)
        modifier2 = self.make_modifier(ModDomain.self, src_attr2, tgt_attr)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier1])
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier2])
        item = Ship(self.mktype(
            attrs={src_attr1.id: 20, src_attr2.id: 20, tgt_attr.id: 100},
            effects=(effect1, effect2)).id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ship_same_item(self):
        # Setup
        tgt_attr = self.mkattr()
        src_attr1 = self.mkattr()
        src_attr2 = self.mkattr()
        modifier1 = self.make_modifier(ModDomain.ship, src_attr1, tgt_attr)
        modifier2 = self.make_modifier(ModDomain.ship, src_attr2, tgt_attr)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.active,
            modifiers=[modifier1])
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.overload,
            modifiers=[modifier2])
        influence_src = ModuleHigh(
            self.mktype(
                attrs={src_attr1.id: 20, src_attr2.id: 20},
                effects=(effect1, effect2),
                default_effect=effect1).id,
            state=State.overload)
        influence_tgt = Ship(self.mktype(attrs={tgt_attr.id: 100}).id)
        self.fit.ship = influence_tgt
        # Action
        self.fit.modules.high.append(influence_src)
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr.id], 144)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ship_same_item_awaiting_one(self):
        # Setup
        tgt_attr = self.mkattr()
        src_attr1 = self.mkattr()
        src_attr2 = self.mkattr()
        modifier1 = self.make_modifier(ModDomain.ship, src_attr1, tgt_attr)
        modifier2 = self.make_modifier(ModDomain.ship, src_attr2, tgt_attr)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.active,
            modifiers=[modifier1])
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.overload,
            modifiers=[modifier2])
        influence_src = ModuleHigh(
            self.mktype(
                attrs={src_attr1.id: 20, src_attr2.id: 20},
                effects=(effect1, effect2),
                default_effect=effect1).id,
            state=State.active)
        influence_tgt = Ship(self.mktype(attrs={tgt_attr.id: 100}).id)
        self.fit.ship = influence_tgt
        # Action
        self.fit.modules.high.append(influence_src)
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr.id], 120)
        # Action
        influence_src.state = State.overload
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr.id], 144)
        # Action
        influence_src.state = State.active
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr.id], 120)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_ship_same_item_awaiting_two(self):
        # Setup
        tgt_attr = self.mkattr()
        src_attr1 = self.mkattr()
        src_attr2 = self.mkattr()
        modifier1 = self.make_modifier(ModDomain.ship, src_attr1, tgt_attr)
        modifier2 = self.make_modifier(ModDomain.ship, src_attr2, tgt_attr)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.active,
            modifiers=[modifier1])
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.overload,
            modifiers=[modifier2])
        influence_src = ModuleHigh(
            self.mktype(
                attrs={src_attr1.id: 20, src_attr2.id: 20},
                effects=(effect1, effect2),
                default_effect=effect1).id,
            state=State.online)
        influence_tgt = Ship(self.mktype(attrs={tgt_attr.id: 100}).id)
        self.fit.ship = influence_tgt
        # Action
        self.fit.modules.high.append(influence_src)
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr.id], 100)
        # Action
        influence_src.state = State.overload
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr.id], 144)
        # Action
        influence_src.state = State.online
        # Verification
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr.id], 100)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_self_same_item_attr(self):
        # Setup
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier1 = self.make_modifier(ModDomain.self, src_attr, tgt_attr)
        modifier2 = self.make_modifier(ModDomain.self, src_attr, tgt_attr)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier1])
        effect2 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier2])
        item = Ship(self.mktype(
            attrs={src_attr.id: 20, tgt_attr.id: 100},
            effects=(effect1, effect2)).id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_self_same_item_effect(self):
        # Setup
        tgt_attr = self.mkattr()
        src_attr1 = self.mkattr()
        src_attr2 = self.mkattr()
        modifier1 = self.make_modifier(ModDomain.self, src_attr1, tgt_attr)
        modifier2 = self.make_modifier(ModDomain.self, src_attr2, tgt_attr)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier1, modifier2])
        item = Ship(self.mktype(
            attrs={src_attr1.id: 20, src_attr2.id: 20, tgt_attr.id: 100},
            effects=[effect1]).id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_self_same_item_effect_attr(self):
        # Setup
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier1 = self.make_modifier(ModDomain.self, src_attr, tgt_attr)
        modifier2 = self.make_modifier(ModDomain.self, src_attr, tgt_attr)
        effect1 = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier1, modifier2])
        item = Ship(self.mktype(
            attrs={src_attr.id: 20, tgt_attr.id: 100},
            effects=[effect1]).id)
        # Action
        self.fit.ship = item
        # Verification
        self.assertAlmostEqual(item.attrs[tgt_attr.id], 144)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
