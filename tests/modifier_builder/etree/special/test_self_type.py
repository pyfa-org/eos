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


from eos.const.eos import EffectBuildStatus, EosType
from eos.const.eve import Operand
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderEtreeSelfType(ModBuilderTestCase):

    def make_etree(self, add_mod_operand, rm_mod_operand):
        e_tgt_own = self.ef.make(
            1, operandID=Operand.def_dom, expressionValue='Char')
        e_self = self.ef.make(
            2, operandID=Operand.def_dom, expressionValue='Self')
        e_self_type = self.ef.make(
            3, operandID=Operand.get_type, arg1=e_self['expressionID'])
        e_tgt_attr = self.ef.make(
            4, operandID=Operand.def_attr, expressionAttributeID=64)
        e_optr = self.ef.make(
            5, operandID=Operand.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(
            6, operandID=Operand.def_attr, expressionAttributeID=292)
        e_tgt_itms = self.ef.make(
            7, operandID=Operand.dom_srq, arg1=e_tgt_own['expressionID'],
            arg2=e_self_type['expressionID'])
        e_tgt_spec = self.ef.make(
            8, operandID=Operand.itm_attr, arg1=e_tgt_itms['expressionID'],
            arg2=e_tgt_attr['expressionID'])
        e_optr_tgt = self.ef.make(
            9, operandID=Operand.optr_tgt, arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID'])
        e_add_mod = self.ef.make(
            10, operandID=add_mod_operand, arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID'])
        e_rm_mod = self.ef.make(
            11, operandID=rm_mod_operand, arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID'])
        self.effect_row = {
            'preExpression': e_add_mod['expressionID'],
            'postExpression': e_rm_mod['expressionID']}

    def test_mod_domain_skillrq(self):
        self.make_etree(Operand.add_dom_srq_mod, Operand.rm_dom_srq_mod)
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.tgt_filter_extra_arg, EosType.current_self)
        self.assertEqual(len(self.get_log()), 0)

    def test_mod_owner_skillrq(self):
        self.make_etree(Operand.add_own_srq_mod, Operand.rm_own_srq_mod)
        modifiers, status = self.run_builder(self.effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.tgt_filter_extra_arg, EosType.current_self)
        self.assertEqual(len(self.get_log()), 0)
