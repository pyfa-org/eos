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


from eos import Implant
from eos import Rig
from eos.const.eos import ModAffecteeFilter
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eve import EffectCategoryId
from tests.integration.calculator.testcase import CalculatorTestCase


class TestOperatorForcedValue(CalculatorTestCase):
    """Test that post-assignment forces value of attribute."""

    def test_forced_value(self):
        tgt_attr = self.mkattr()
        src_attr = self.mkattr()
        modifier_pre_ass = self.mkmod(
            affectee_filter=ModAffecteeFilter.domain,
            affectee_domain=ModDomain.ship,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.pre_assign,
            affector_attr_id=src_attr.id)
        effect_pre_ass = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_pre_ass])
        influence_src_pre_ass = Implant(self.mktype(
            attrs={src_attr.id: 5},
            effects=[effect_pre_ass]).id)
        self.fit.implants.add(influence_src_pre_ass)
        modifier_pre_mul = self.mkmod(
            affectee_filter=ModAffecteeFilter.domain,
            affectee_domain=ModDomain.ship,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.pre_mul,
            affector_attr_id=src_attr.id)
        effect_pre_mul = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_pre_mul])
        influence_src_pre_mul = Implant(self.mktype(
            attrs={src_attr.id: 50},
            effects=[effect_pre_mul]).id)
        self.fit.implants.add(influence_src_pre_mul)
        modifier_pre_div = self.mkmod(
            affectee_filter=ModAffecteeFilter.domain,
            affectee_domain=ModDomain.ship,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.pre_div,
            affector_attr_id=src_attr.id)
        effect_pre_div = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_pre_div])
        influence_src_pre_div = Implant(self.mktype(
            attrs={src_attr.id: 0.5},
            effects=[effect_pre_div]).id)
        self.fit.implants.add(influence_src_pre_div)
        modifier_mod_add = self.mkmod(
            affectee_filter=ModAffecteeFilter.domain,
            affectee_domain=ModDomain.ship,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.mod_add,
            affector_attr_id=src_attr.id)
        effect_mod_add = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_mod_add])
        influence_src_mod_add = Implant(self.mktype(
            attrs={src_attr.id: 10},
            effects=[effect_mod_add]).id)
        self.fit.implants.add(influence_src_mod_add)
        modifier_mod_sub = self.mkmod(
            affectee_filter=ModAffecteeFilter.domain,
            affectee_domain=ModDomain.ship,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.mod_sub,
            affector_attr_id=src_attr.id)
        effect_mod_sub = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_mod_sub])
        influence_src_mod_sub = Implant(self.mktype(
            attrs={src_attr.id: 63},
            effects=[effect_mod_sub]).id)
        self.fit.implants.add(influence_src_mod_sub)
        modifier_post_mul = self.mkmod(
            affectee_filter=ModAffecteeFilter.domain,
            affectee_domain=ModDomain.ship,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.post_mul,
            affector_attr_id=src_attr.id)
        effect_post_mul = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_post_mul])
        influence_src_post_mul = Implant(self.mktype(
            attrs={src_attr.id: 1.35},
            effects=[effect_post_mul]).id)
        self.fit.implants.add(influence_src_post_mul)
        modifier_post_div = self.mkmod(
            affectee_filter=ModAffecteeFilter.domain,
            affectee_domain=ModDomain.ship,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.post_div,
            affector_attr_id=src_attr.id)
        effect_post_div = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_post_div])
        influence_src_post_div = Implant(self.mktype(
            attrs={src_attr.id: 2.7},
            effects=[effect_post_div]).id)
        self.fit.implants.add(influence_src_post_div)
        modifier_post_perc = self.mkmod(
            affectee_filter=ModAffecteeFilter.domain,
            affectee_domain=ModDomain.ship,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.post_percent,
            affector_attr_id=src_attr.id)
        effect_post_perc = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_post_perc])
        influence_src_post_perc = Implant(self.mktype(
            attrs={src_attr.id: 15},
            effects=[effect_post_perc]).id)
        self.fit.implants.add(influence_src_post_perc)
        modifier_post_ass = self.mkmod(
            affectee_filter=ModAffecteeFilter.domain,
            affectee_domain=ModDomain.ship,
            affectee_attr_id=tgt_attr.id,
            operator=ModOperator.post_assign,
            affector_attr_id=src_attr.id)
        effect_post_ass = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[modifier_post_ass])
        influence_src_post_ass = Implant(self.mktype(
            attrs={src_attr.id: 68},
            effects=[effect_post_ass]).id)
        self.fit.implants.add(influence_src_post_ass)
        influence_tgt = Rig(self.mktype(attrs={tgt_attr.id: 100}).id)
        # Action
        self.fit.rigs.add(influence_tgt)
        # Verification
        # Post-assignment value must override all other modifications
        self.assertAlmostEqual(influence_tgt.attrs[tgt_attr.id], 68)
        # Cleanup
        self.assert_solsys_buffers_empty(self.fit.solar_system)
        self.assert_log_entries(0)
