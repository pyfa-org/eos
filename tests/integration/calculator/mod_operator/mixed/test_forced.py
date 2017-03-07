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


class TestOperatorForcedValue(CalculatorTestCase):
    """Test that post-assignment forces value of attribute"""

    def test_forced_value(self):
        tgt_attr = self.ch.attribute()
        src_attr = self.ch.attribute()
        modifier_pre_ass = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.pre_assign,
            src_attr=src_attr.id
        )
        effect_pre_ass = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier_pre_ass,))
        influence_source_pre_ass = Implant(self.ch.type(
            effects=(effect_pre_ass,), attributes={src_attr.id: 5}
        ).id)
        self.fit.implants.add(influence_source_pre_ass)
        modifier_pre_mul = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.pre_mul,
            src_attr=src_attr.id
        )
        effect_pre_mul = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier_pre_mul,))
        influence_source_pre_mul = Implant(self.ch.type(
            effects=(effect_pre_mul,), attributes={src_attr.id: 50}
        ).id)
        self.fit.implants.add(influence_source_pre_mul)
        modifier_pre_div = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.pre_div,
            src_attr=src_attr.id
        )
        effect_pre_div = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier_pre_div,))
        influence_source_pre_div = Implant(self.ch.type(
            effects=(effect_pre_div,), attributes={src_attr.id: 0.5}
        ).id)
        self.fit.implants.add(influence_source_pre_div)
        modifier_mod_add = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.mod_add,
            src_attr=src_attr.id
        )
        effect_mod_add = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier_mod_add,))
        influence_source_mod_add = Implant(self.ch.type(
            effects=(effect_mod_add,), attributes={src_attr.id: 10}
        ).id)
        self.fit.implants.add(influence_source_mod_add)
        modifier_mod_sub = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.mod_sub,
            src_attr=src_attr.id
        )
        effect_mod_sub = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier_mod_sub,))
        influence_source_mod_sub = Implant(self.ch.type(
            effects=(effect_mod_sub,), attributes={src_attr.id: 63}
        ).id)
        self.fit.implants.add(influence_source_mod_sub)
        modifier_post_mul = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id
        )
        effect_post_mul = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier_post_mul,))
        influence_source_post_mul = Implant(self.ch.type(
            effects=(effect_post_mul,), attributes={src_attr.id: 1.35}
        ).id)
        self.fit.implants.add(influence_source_post_mul)
        modifier_post_div = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_div,
            src_attr=src_attr.id
        )
        effect_post_div = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier_post_div,))
        influence_source_post_div = Implant(self.ch.type(
            effects=(effect_post_div,), attributes={src_attr.id: 2.7}
        ).id)
        self.fit.implants.add(influence_source_post_div)
        modifier_post_perc = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id
        )
        effect_post_perc = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier_post_perc,))
        influence_source_post_perc = Implant(self.ch.type(
            effects=(effect_post_perc,), attributes={src_attr.id: 15}
        ).id)
        self.fit.implants.add(influence_source_post_perc)
        modifier_post_ass = DogmaModifier(
            tgt_filter=ModifierTargetFilter.domain,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=tgt_attr.id,
            operator=ModifierOperator.post_assign,
            src_attr=src_attr.id
        )
        effect_post_ass = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier_post_ass,))
        influence_source_post_ass = Implant(self.ch.type(
            effects=(effect_post_ass,), attributes={src_attr.id: 68}
        ).id)
        self.fit.implants.add(influence_source_post_ass)
        influence_target = Rig(self.ch.type(attributes={tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_target)
        # Verification
        # Post-assignment value must override all other modifications
        self.assertAlmostEqual(influence_target.attributes[tgt_attr.id], 68)
        # Cleanup
        self.fit.implants.remove(influence_source_pre_ass)
        self.fit.implants.remove(influence_source_pre_mul)
        self.fit.implants.remove(influence_source_pre_div)
        self.fit.implants.remove(influence_source_mod_add)
        self.fit.implants.remove(influence_source_mod_sub)
        self.fit.implants.remove(influence_source_post_mul)
        self.fit.implants.remove(influence_source_post_div)
        self.fit.implants.remove(influence_source_post_perc)
        self.fit.implants.remove(influence_source_post_ass)
        self.fit.rigs.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)
