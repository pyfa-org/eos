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


from eos.const.eos import ModifierType, ModifierDomain, ModifierOperator, State
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import Modifier
from tests.calculator.calculator_testcase import CalculatorTestCase
from tests.calculator.environment import IndependentItem, ShipDomainItem


class TestOperatorForcedValue(CalculatorTestCase):
    """Test that post-assignment forces value of attribute"""

    def test_forced_value(self):
        tgt_attr = self.ch.attribute(attribute_id=1)
        src_attr = self.ch.attribute(attribute_id=2)
        modifier_pre_ass = Modifier()
        modifier_pre_ass.type = ModifierType.domain
        modifier_pre_ass.domain = ModifierDomain.ship
        modifier_pre_ass.state = State.offline
        modifier_pre_ass.src_attr = src_attr.id
        modifier_pre_ass.operator = ModifierOperator.pre_assign
        modifier_pre_ass.tgt_attr = tgt_attr.id
        effect_pre_ass = self.ch.effect(effect_id=1, category=EffectCategory.passive)
        effect_pre_ass.modifiers = (modifier_pre_ass,)
        influence_source_pre_ass = IndependentItem(self.ch.type(
            type_id=1, effects=(effect_pre_ass,),
            attributes={src_attr.id: 5}
        ))
        self.fit.items.add(influence_source_pre_ass)
        modifier_pre_mul = Modifier()
        modifier_pre_mul.type = ModifierType.domain
        modifier_pre_mul.domain = ModifierDomain.ship
        modifier_pre_mul.state = State.offline
        modifier_pre_mul.src_attr = src_attr.id
        modifier_pre_mul.operator = ModifierOperator.pre_mul
        modifier_pre_mul.tgt_attr = tgt_attr.id
        effect_pre_mul = self.ch.effect(effect_id=2, category=EffectCategory.passive)
        effect_pre_mul.modifiers = (modifier_pre_mul,)
        influence_source_pre_mul = IndependentItem(self.ch.type(
            type_id=2, effects=(effect_pre_mul,),
            attributes={src_attr.id: 50}
        ))
        self.fit.items.add(influence_source_pre_mul)
        modifier_pre_div = Modifier()
        modifier_pre_div.type = ModifierType.domain
        modifier_pre_div.domain = ModifierDomain.ship
        modifier_pre_div.state = State.offline
        modifier_pre_div.src_attr = src_attr.id
        modifier_pre_div.operator = ModifierOperator.pre_div
        modifier_pre_div.tgt_attr = tgt_attr.id
        effect_pre_div = self.ch.effect(effect_id=3, category=EffectCategory.passive)
        effect_pre_div.modifiers = (modifier_pre_div,)
        influence_source_pre_div = IndependentItem(self.ch.type(
            type_id=3, effects=(effect_pre_div,),
            attributes={src_attr.id: 0.5}
        ))
        self.fit.items.add(influence_source_pre_div)
        modifier_mod_add = Modifier()
        modifier_mod_add.type = ModifierType.domain
        modifier_mod_add.domain = ModifierDomain.ship
        modifier_mod_add.state = State.offline
        modifier_mod_add.src_attr = src_attr.id
        modifier_mod_add.operator = ModifierOperator.mod_add
        modifier_mod_add.tgt_attr = tgt_attr.id
        effect_mod_add = self.ch.effect(effect_id=4, category=EffectCategory.passive)
        effect_mod_add.modifiers = (modifier_mod_add,)
        influence_source_mod_add = IndependentItem(self.ch.type(
            type_id=4, effects=(effect_mod_add,),
            attributes={src_attr.id: 10}
        ))
        self.fit.items.add(influence_source_mod_add)
        modifier_mod_sub = Modifier()
        modifier_mod_sub.type = ModifierType.domain
        modifier_mod_sub.domain = ModifierDomain.ship
        modifier_mod_sub.state = State.offline
        modifier_mod_sub.src_attr = src_attr.id
        modifier_mod_sub.operator = ModifierOperator.mod_sub
        modifier_mod_sub.tgt_attr = tgt_attr.id
        effect_mod_sub = self.ch.effect(effect_id=5, category=EffectCategory.passive)
        effect_mod_sub.modifiers = (modifier_mod_sub,)
        influence_source_mod_sub = IndependentItem(self.ch.type(
            type_id=5, effects=(effect_mod_sub,),
            attributes={src_attr.id: 63}
        ))
        self.fit.items.add(influence_source_mod_sub)
        modifier_post_mul = Modifier()
        modifier_post_mul.type = ModifierType.domain
        modifier_post_mul.domain = ModifierDomain.ship
        modifier_post_mul.state = State.offline
        modifier_post_mul.src_attr = src_attr.id
        modifier_post_mul.operator = ModifierOperator.post_mul
        modifier_post_mul.tgt_attr = tgt_attr.id
        effect_post_mul = self.ch.effect(effect_id=6, category=EffectCategory.passive)
        effect_post_mul.modifiers = (modifier_post_mul,)
        influence_source_post_mul = IndependentItem(self.ch.type(
            type_id=6, effects=(effect_post_mul,),
            attributes={src_attr.id: 1.35}
        ))
        self.fit.items.add(influence_source_post_mul)
        modifier_post_div = Modifier()
        modifier_post_div.type = ModifierType.domain
        modifier_post_div.domain = ModifierDomain.ship
        modifier_post_div.state = State.offline
        modifier_post_div.src_attr = src_attr.id
        modifier_post_div.operator = ModifierOperator.post_div
        modifier_post_div.tgt_attr = tgt_attr.id
        effect_post_div = self.ch.effect(effect_id=7, category=EffectCategory.passive)
        effect_post_div.modifiers = (modifier_post_div,)
        influence_source_post_div = IndependentItem(self.ch.type(
            type_id=7, effects=(effect_post_div,),
            attributes={src_attr.id: 2.7}
        ))
        self.fit.items.add(influence_source_post_div)
        modifier_post_perc = Modifier()
        modifier_post_perc.type = ModifierType.domain
        modifier_post_perc.domain = ModifierDomain.ship
        modifier_post_perc.state = State.offline
        modifier_post_perc.src_attr = src_attr.id
        modifier_post_perc.operator = ModifierOperator.post_percent
        modifier_post_perc.tgt_attr = tgt_attr.id
        effect_post_perc = self.ch.effect(effect_id=8, category=EffectCategory.passive)
        effect_post_perc.modifiers = (modifier_post_perc,)
        influence_source_post_perc = IndependentItem(self.ch.type(
            type_id=8, effects=(effect_post_perc,),
            attributes={src_attr.id: 15}
        ))
        self.fit.items.add(influence_source_post_perc)
        modifier_post_ass = Modifier()
        modifier_post_ass.type = ModifierType.domain
        modifier_post_ass.domain = ModifierDomain.ship
        modifier_post_ass.state = State.offline
        modifier_post_ass.src_attr = src_attr.id
        modifier_post_ass.operator = ModifierOperator.post_assign
        modifier_post_ass.tgt_attr = tgt_attr.id
        effect_post_ass = self.ch.effect(effect_id=9, category=EffectCategory.passive)
        effect_post_ass.modifiers = (modifier_post_ass,)
        influence_source_post_ass = IndependentItem(self.ch.type(
            type_id=9, effects=(effect_post_ass,),
            attributes={src_attr.id: 68}
        ))
        self.fit.items.add(influence_source_post_ass)
        influence_target = ShipDomainItem(self.ch.type(type_id=10, attributes={tgt_attr.id: 100}))
        # Action
        self.fit.items.add(influence_target)
        # Verification
        # Post-assignment value must override all other modifications
        self.assertAlmostEqual(influence_target.attributes[tgt_attr.id], 68)
        # Cleanup
        self.fit.items.remove(influence_source_pre_ass)
        self.fit.items.remove(influence_source_pre_mul)
        self.fit.items.remove(influence_source_pre_div)
        self.fit.items.remove(influence_source_mod_add)
        self.fit.items.remove(influence_source_mod_sub)
        self.fit.items.remove(influence_source_post_mul)
        self.fit.items.remove(influence_source_post_div)
        self.fit.items.remove(influence_source_post_perc)
        self.fit.items.remove(influence_source_post_ass)
        self.fit.items.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_calculator_buffers_empty(self.fit)
