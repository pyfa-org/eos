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


from eos import Charge
from eos import ModuleLow
from eos import State
from eos.const.eos import ModDomain
from eos.const.eos import ModOperator
from eos.const.eos import ModTgtFilter
from eos.const.eve import AttrId
from eos.const.eve import EffectCategoryId
from eos.const.eve import EffectId
from eos.const.eve import TypeId
from tests.integration.customization.testcase import CustomizationTestCase


class TestPropulsionModules(CustomizationTestCase):

    def setUp(self):
        CustomizationTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.charged_armor_dmg_mult)
        self.mkattr(attr_id=AttrId.armor_dmg_amount, stackable=False)

    def test_local_aar(self):
        effect = self.mkeffect(
            effect_id=EffectId.fueled_armor_repair,
            category_id=EffectCategoryId.active)
        aar = ModuleLow(
            self.mktype(
                attrs={
                    AttrId.armor_dmg_amount: 50,
                    AttrId.charged_armor_dmg_mult: 3},
                effects=[effect],
                default_effect=effect).id,
            state=State.active)
        aar.charge = Charge(self.mktype(type_id=TypeId.nanite_repair_paste).id)
        self.fit.modules.low.append(aar)
        # Verification
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 150)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_remote_aar(self):
        effect = self.mkeffect(
            effect_id=EffectId.module_bonus_ancillary_remote_armor_repairer,
            category_id=EffectCategoryId.target)
        raar = ModuleLow(
            self.mktype(
                attrs={
                    AttrId.armor_dmg_amount: 50,
                    AttrId.charged_armor_dmg_mult: 3},
                effects=[effect],
                default_effect=effect).id,
            state=State.active)
        raar.charge = Charge(self.mktype(type_id=TypeId.nanite_repair_paste).id)
        self.fit.modules.low.append(raar)
        # Verification
        self.assertAlmostEqual(raar.attrs[AttrId.armor_dmg_amount], 150)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rep_amount_state(self):
        # Multiplier should be applied even when module is offline
        effect = self.mkeffect(
            effect_id=EffectId.fueled_armor_repair,
            category_id=EffectCategoryId.active)
        aar = ModuleLow(
            self.mktype(
                attrs={
                    AttrId.armor_dmg_amount: 50,
                    AttrId.charged_armor_dmg_mult: 3},
                effects=[effect],
                default_effect=effect).id,
            state=State.offline)
        aar.charge = Charge(self.mktype(type_id=TypeId.nanite_repair_paste).id)
        self.fit.modules.low.append(aar)
        # Verification
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 150)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rep_amount_aar_attr_mult_absent(self):
        effect = self.mkeffect(
            effect_id=EffectId.fueled_armor_repair,
            category_id=EffectCategoryId.active)
        aar = ModuleLow(
            self.mktype(
                attrs={AttrId.armor_dmg_amount: 50},
                effects=[effect],
                default_effect=effect).id,
            state=State.active)
        aar.charge = Charge(self.mktype(type_id=TypeId.nanite_repair_paste).id)
        self.fit.modules.low.append(aar)
        # Verification
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 50)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rep_amount_aar_attr_rep_amount_absent(self):
        effect = self.mkeffect(
            effect_id=EffectId.fueled_armor_repair,
            category_id=EffectCategoryId.active)
        aar = ModuleLow(
            self.mktype(
                attrs={AttrId.charged_armor_dmg_mult: 3},
                effects=[effect],
                default_effect=effect).id,
            state=State.active)
        aar.charge = Charge(self.mktype(type_id=TypeId.nanite_repair_paste).id)
        self.fit.modules.low.append(aar)
        # Verification
        with self.assertRaises(KeyError):
            aar.attrs[AttrId.armor_dmg_amount]
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rep_amount_charge_absent(self):
        effect = self.mkeffect(
            effect_id=EffectId.fueled_armor_repair,
            category_id=EffectCategoryId.active)
        aar = ModuleLow(
            self.mktype(
                attrs={
                    AttrId.armor_dmg_amount: 50,
                    AttrId.charged_armor_dmg_mult: 3},
                effects=[effect],
                default_effect=effect).id,
            state=State.active)
        self.fit.modules.low.append(aar)
        # Verification
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 50)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rep_amount_charge_not_loaded(self):
        effect = self.mkeffect(
            effect_id=EffectId.fueled_armor_repair,
            category_id=EffectCategoryId.active)
        aar = ModuleLow(
            self.mktype(
                attrs={
                    AttrId.armor_dmg_amount: 50,
                    AttrId.charged_armor_dmg_mult: 3},
                effects=[effect],
                default_effect=effect).id,
            state=State.active)
        aar.charge = Charge(TypeId.nanite_repair_paste)
        self.fit.modules.low.append(aar)
        # Verification
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 150)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rep_amount_recalc_aar_attr_mult_changed(self):
        multmod_src_attr = self.mkattr()
        multmod_mod = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=AttrId.charged_armor_dmg_mult,
            operator=ModOperator.post_percent,
            src_attr_id=multmod_src_attr.id)
        multmod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[multmod_mod])
        multmod = ModuleLow(self.mktype(
            attrs={multmod_src_attr.id: 50},
            effects=[multmod_effect]).id)
        effect = self.mkeffect(
            effect_id=EffectId.fueled_armor_repair,
            category_id=EffectCategoryId.active)
        aar = ModuleLow(
            self.mktype(
                attrs={
                    AttrId.armor_dmg_amount: 50,
                    AttrId.charged_armor_dmg_mult: 3},
                effects=[effect],
                default_effect=effect).id,
            state=State.active)
        aar.charge = Charge(self.mktype(type_id=TypeId.nanite_repair_paste).id)
        self.fit.modules.low.append(aar)
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 150)
        # Action
        self.fit.modules.low.append(multmod)
        # Verification
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 225)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rep_amount_recalc_charge_to_charge_absent(self):
        effect = self.mkeffect(
            effect_id=EffectId.fueled_armor_repair,
            category_id=EffectCategoryId.active)
        aar = ModuleLow(
            self.mktype(
                attrs={
                    AttrId.armor_dmg_amount: 50,
                    AttrId.charged_armor_dmg_mult: 3},
                effects=[effect],
                default_effect=effect).id,
            state=State.active)
        aar.charge = Charge(self.mktype(type_id=TypeId.nanite_repair_paste).id)
        self.fit.modules.low.append(aar)
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 150)
        # Action
        aar.charge = None
        # Verification
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 50)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rep_amount_recalc_charge_absent_to_charge(self):
        effect = self.mkeffect(
            effect_id=EffectId.fueled_armor_repair,
            category_id=EffectCategoryId.active)
        aar = ModuleLow(
            self.mktype(
                attrs={
                    AttrId.armor_dmg_amount: 50,
                    AttrId.charged_armor_dmg_mult: 3},
                effects=[effect],
                default_effect=effect).id,
            state=State.active)
        self.fit.modules.low.append(aar)
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 50)
        # Action
        aar.charge = Charge(self.mktype(type_id=TypeId.nanite_repair_paste).id)
        # Verification
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 150)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_rep_amount_stacking(self):
        # Multiplier shouldn't be stacking penalized against any other
        # multiplicative modifications
        multmod_src_attr_mul = self.mkattr()
        multmod_src_attr_div = self.mkattr()
        multmod_src_attr_perc = self.mkattr()
        multmod_mod_premul = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=AttrId.armor_dmg_amount,
            operator=ModOperator.pre_mul,
            src_attr_id=multmod_src_attr_mul.id)
        multmod_mod_prediv = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=AttrId.armor_dmg_amount,
            operator=ModOperator.pre_div,
            src_attr_id=multmod_src_attr_div.id)
        multmod_mod_postmul = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=AttrId.armor_dmg_amount,
            operator=ModOperator.post_mul,
            src_attr_id=multmod_src_attr_mul.id)
        multmod_mod_postdiv = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=AttrId.armor_dmg_amount,
            operator=ModOperator.post_div,
            src_attr_id=multmod_src_attr_div.id)
        multmod_mod_postperc = self.mkmod(
            tgt_filter=ModTgtFilter.domain,
            tgt_domain=ModDomain.ship,
            tgt_attr_id=AttrId.armor_dmg_amount,
            operator=ModOperator.post_percent,
            src_attr_id=multmod_src_attr_perc.id)
        multmod_effect = self.mkeffect(
            category_id=EffectCategoryId.passive,
            modifiers=[
                multmod_mod_premul,
                multmod_mod_prediv,
                multmod_mod_postmul,
                multmod_mod_postdiv,
                multmod_mod_postperc])
        multmod = ModuleLow(self.mktype(
            attrs={
                multmod_src_attr_mul.id: 2,
                multmod_src_attr_div.id: 0.5,
                multmod_src_attr_perc.id: 100},
            effects=[multmod_effect]).id)
        effect = self.mkeffect(
            effect_id=EffectId.fueled_armor_repair,
            category_id=EffectCategoryId.active)
        aar = ModuleLow(
            self.mktype(
                attrs={
                    AttrId.armor_dmg_amount: 50,
                    AttrId.charged_armor_dmg_mult: 3},
                effects=[effect],
                default_effect=effect).id,
            state=State.active)
        aar.charge = Charge(self.mktype(type_id=TypeId.nanite_repair_paste).id)
        self.fit.modules.low.append(aar)
        self.fit.modules.low.append(multmod)
        # Verification
        # If paste multiplier is not stacking penalized against any mods, final
        # result will be 50 * 3 * 2 ^ 5
        self.assertAlmostEqual(aar.attrs[AttrId.armor_dmg_amount], 4800)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
