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


from eos import *
from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestOperatorAllIn(CalculatorTestCase):
    """Test interaction of all operators, besides post-assignment"""

    def test_all_in(self):
        tgt_attr = self.ch.attribute(stackable=0)
        src_attr = self.ch.attribute()
        modifier_pre_ass = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.pre_assign,
            src_attr=src_attr.id
        )
        effect_pre_ass = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier_pre_ass])
        value_pre_ass = 5
        influence_source_pre_ass = Implant(self.ch.type(
            effects=[effect_pre_ass], attributes={src_attr.id: value_pre_ass}
        ).id)
        self.fit.implants.add(influence_source_pre_ass)
        modifier_pre_mul = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.pre_mul,
            src_attr=src_attr.id
        )
        effect_pre_mul = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier_pre_mul])
        value_pre_mul = 50
        influence_source_pre_mul = Implant(self.ch.type(
            effects=[effect_pre_mul], attributes={src_attr.id: value_pre_mul}
        ).id)
        self.fit.implants.add(influence_source_pre_mul)
        modifier_pre_div = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.pre_div,
            src_attr=src_attr.id
        )
        effect_pre_div = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier_pre_div])
        value_pre_div = 0.5
        influence_source_pre_div = Implant(self.ch.type(
            effects=[effect_pre_div], attributes={src_attr.id: value_pre_div}
        ).id)
        self.fit.implants.add(influence_source_pre_div)
        modifier_mod_add = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.mod_add,
            src_attr=src_attr.id
        )
        effect_mod_add = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier_mod_add])
        value_mod_add = 10
        influence_source_mod_add = Implant(self.ch.type(
            effects=[effect_mod_add], attributes={src_attr.id: value_mod_add}
        ).id)
        self.fit.implants.add(influence_source_mod_add)
        modifier_mod_sub = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.mod_sub,
            src_attr=src_attr.id
        )
        effect_mod_sub = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier_mod_sub])
        value_mod_sub = 63
        influence_source_mod_sub = Implant(self.ch.type(
            effects=[effect_mod_sub], attributes={src_attr.id: value_mod_sub}
        ).id)
        self.fit.implants.add(influence_source_mod_sub)
        modifier_post_mul = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id
        )
        effect_post_mul = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier_post_mul])
        value_post_mul = 1.35
        influence_source_post_mul = Implant(self.ch.type(
            effects=[effect_post_mul], attributes={src_attr.id: value_post_mul}
        ).id)
        self.fit.implants.add(influence_source_post_mul)
        modifier_post_div = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_div,
            src_attr=src_attr.id
        )
        effect_post_div = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier_post_div])
        value_post_div = 2.7
        influence_source_post_div = Implant(self.ch.type(
            effects=[effect_post_div], attributes={src_attr.id: value_post_div}
        ).id)
        self.fit.implants.add(influence_source_post_div)
        modifier_post_perc = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id
        )
        effect_post_perc = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier_post_perc])
        value_post_perc = 15
        influence_source_post_perc = Implant(self.ch.type(
            effects=[effect_post_perc], attributes={src_attr.id: value_post_perc}
        ).id)
        self.fit.implants.add(influence_source_post_perc)
        influence_target = Rig(self.ch.type(attributes={tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_target)
        # Verification
        # Operators shouldn't be penalized and should go in this order
        exp_value = (
            ((value_pre_ass * value_pre_mul / value_pre_div) + value_mod_add - value_mod_sub) *
            value_post_mul / value_post_div * (1 + value_post_perc / 100)
        )
        self.assertAlmostEqual(influence_target.attributes[tgt_attr.id], exp_value)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
