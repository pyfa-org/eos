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
from eos.const.eos import ModDomain, ModOperator, ModTgtFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestOperatorAllIn(CalculatorTestCase):
    """Test interaction of all operators, besides post-assignment."""

    def test_all_in(self):
        tgt_attr = self.ch.attr(stackable=0)
        src_attr = self.ch.attr()
        modifier_pre_ass = self.mod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.pre_assign,
            src_attr_id=src_attr.id)
        effect_pre_ass = self.ch.effect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_pre_ass])
        value_pre_ass = 5
        influence_src_pre_ass = Implant(self.ch.type(
            attrs={src_attr.id: value_pre_ass},
            effects=[effect_pre_ass]).id)
        self.fit.implants.add(influence_src_pre_ass)
        modifier_pre_mul = self.mod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.pre_mul,
            src_attr_id=src_attr.id)
        effect_pre_mul = self.ch.effect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_pre_mul])
        value_pre_mul = 50
        influence_src_pre_mul = Implant(self.ch.type(
            attrs={src_attr.id: value_pre_mul},
            effects=[effect_pre_mul]).id)
        self.fit.implants.add(influence_src_pre_mul)
        modifier_pre_div = self.mod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.pre_div,
            src_attr_id=src_attr.id)
        effect_pre_div = self.ch.effect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_pre_div])
        value_pre_div = 0.5
        influence_src_pre_div = Implant(self.ch.type(
            attrs={src_attr.id: value_pre_div},
            effects=[effect_pre_div]).id)
        self.fit.implants.add(influence_src_pre_div)
        modifier_mod_add = self.mod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.mod_add,
            src_attr_id=src_attr.id)
        effect_mod_add = self.ch.effect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_mod_add])
        value_mod_add = 10
        influence_src_mod_add = Implant(self.ch.type(
            attrs={src_attr.id: value_mod_add},
            effects=[effect_mod_add]).id)
        self.fit.implants.add(influence_src_mod_add)
        modifier_mod_sub = self.mod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.mod_sub,
            src_attr_id=src_attr.id)
        effect_mod_sub = self.ch.effect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_mod_sub])
        value_mod_sub = 63
        influence_src_mod_sub = Implant(self.ch.type(
            attrs={src_attr.id: value_mod_sub},
            effects=[effect_mod_sub]).id)
        self.fit.implants.add(influence_src_mod_sub)
        modifier_post_mul = self.mod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_mul,
            src_attr_id=src_attr.id)
        effect_post_mul = self.ch.effect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_post_mul])
        value_post_mul = 1.35
        influence_src_post_mul = Implant(self.ch.type(
            attrs={src_attr.id: value_post_mul},
            effects=[effect_post_mul]).id)
        self.fit.implants.add(influence_src_post_mul)
        modifier_post_div = self.mod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_div,
            src_attr_id=src_attr.id)
        effect_post_div = self.ch.effect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_post_div])
        value_post_div = 2.7
        influence_src_post_div = Implant(self.ch.type(
            attrs={src_attr.id: value_post_div},
            effects=[effect_post_div]).id)
        self.fit.implants.add(influence_src_post_div)
        modifier_post_perc = self.mod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            src_attr_id=src_attr.id)
        effect_post_perc = self.ch.effect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_post_perc])
        value_post_perc = 15
        influence_src_post_perc = Implant(self.ch.type(
            attrs={src_attr.id: value_post_perc},
            effects=[effect_post_perc]).id)
        self.fit.implants.add(influence_src_post_perc)
        influence_tgt = Rig(self.ch.type(attrs={tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_tgt)
        # Verification
        # Operators shouldn't be penalized and should go in this order
        exp_value = ((
            value_pre_ass * value_pre_mul / value_pre_div +
            value_mod_add - value_mod_sub) *
            value_post_mul / value_post_div * (1 + value_post_perc / 100))
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr.id], exp_value)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
