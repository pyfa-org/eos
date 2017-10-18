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
from eos.const.eos import ModifierDomain, ModifierOperator, ModifierTargetFilter
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestOperatorForcedValue(CalculatorTestCase):
    """Test that post-assignment forces value of attribute."""

    def test_forced_value(self):
        tgt_attr = self.ch.attr()
        src_attr = self.ch.attr()
        modifier_pre_ass = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.pre_assign,
            src_attr=src_attr.id)
        effect_pre_ass = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier_pre_ass])
        influence_src_pre_ass = Implant(self.ch.type(
            attributes={src_attr.id: 5}, effects=[effect_pre_ass]).id)
        self.fit.implants.add(influence_src_pre_ass)
        modifier_pre_mul = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.pre_mul,
            src_attr=src_attr.id)
        effect_pre_mul = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier_pre_mul])
        influence_src_pre_mul = Implant(self.ch.type(
            attributes={src_attr.id: 50}, effects=[effect_pre_mul]).id)
        self.fit.implants.add(influence_src_pre_mul)
        modifier_pre_div = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.pre_div,
            src_attr=src_attr.id)
        effect_pre_div = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier_pre_div])
        influence_src_pre_div = Implant(self.ch.type(
            attributes={src_attr.id: 0.5}, effects=[effect_pre_div]).id)
        self.fit.implants.add(influence_src_pre_div)
        modifier_mod_add = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.mod_add,
            src_attr=src_attr.id)
        effect_mod_add = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier_mod_add])
        influence_src_mod_add = Implant(self.ch.type(
            attributes={src_attr.id: 10}, effects=[effect_mod_add]).id)
        self.fit.implants.add(influence_src_mod_add)
        modifier_mod_sub = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.mod_sub,
            src_attr=src_attr.id)
        effect_mod_sub = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier_mod_sub])
        influence_src_mod_sub = Implant(self.ch.type(
            attributes={src_attr.id: 63}, effects=[effect_mod_sub]).id)
        self.fit.implants.add(influence_src_mod_sub)
        modifier_post_mul = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id)
        effect_post_mul = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier_post_mul])
        influence_src_post_mul = Implant(self.ch.type(
            attributes={src_attr.id: 1.35}, effects=[effect_post_mul]).id)
        self.fit.implants.add(influence_src_post_mul)
        modifier_post_div = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_div,
            src_attr=src_attr.id)
        effect_post_div = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier_post_div])
        influence_src_post_div = Implant(self.ch.type(
            attributes={src_attr.id: 2.7}, effects=[effect_post_div]).id)
        self.fit.implants.add(influence_src_post_div)
        modifier_post_perc = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id)
        effect_post_perc = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier_post_perc])
        influence_src_post_perc = Implant(self.ch.type(
            attributes={src_attr.id: 15}, effects=[effect_post_perc]).id)
        self.fit.implants.add(influence_src_post_perc)
        modifier_post_ass = self.mod(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_assign,
            src_attr=src_attr.id)
        effect_post_ass = self.ch.effect(
            category=EffectCategoryId.passive, modifiers=[modifier_post_ass])
        influence_src_post_ass = Implant(self.ch.type(
            attributes={src_attr.id: 68}, effects=[effect_post_ass]).id)
        self.fit.implants.add(influence_src_post_ass)
        influence_tgt = Rig(self.ch.type(attributes={tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_tgt)
        # Verification
        # Post-assignment value must override all other modifications
        self.assertAlmostEqual(influence_tgt.attributes[tgt_attr.id], 68)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
