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


from eos.const.eos import EffectBuildStatus
from eos.const.eve import OperandId
from tests.mod_builder.testcase import ModBuilderTestCase


class TestBuilderEtreeSplicing(ModBuilderTestCase):

    def test_build_success(self):
        e_tgt_dom = self.ef.make(
            1, operandID=OperandId.def_dom, expressionValue='Target')
        e_tgt_srq = self.ef.make(
            2, operandID=OperandId.def_type, expressionTypeID=3300)
        e_tgt_attr1 = self.ef.make(
            3, operandID=OperandId.def_attr, expressionAttributeID=54)
        e_tgt_attr2 = self.ef.make(
            4, operandID=OperandId.def_attr, expressionAttributeID=158)
        e_tgt_attr3 = self.ef.make(
            5, operandID=OperandId.def_attr, expressionAttributeID=160)
        e_optr = self.ef.make(
            6, operandID=OperandId.def_optr, expressionValue='PostPercent')
        e_src_attr1 = self.ef.make(
            7, operandID=OperandId.def_attr, expressionAttributeID=351)
        e_src_attr2 = self.ef.make(
            8, operandID=OperandId.def_attr, expressionAttributeID=349)
        e_src_attr3 = self.ef.make(
            9, operandID=OperandId.def_attr, expressionAttributeID=767)
        e_tgt_itms = self.ef.make(
            10, operandID=OperandId.dom_srq, arg1=e_tgt_dom['expressionID'],
            arg2=e_tgt_srq['expressionID'])
        e_tgt_spec1 = self.ef.make(
            11, operandID=OperandId.itm_attr, arg1=e_tgt_itms['expressionID'],
            arg2=e_tgt_attr1['expressionID'])
        e_tgt_spec2 = self.ef.make(
            12, operandID=OperandId.itm_attr, arg1=e_tgt_itms['expressionID'],
            arg2=e_tgt_attr2['expressionID'])
        e_tgt_spec3 = self.ef.make(
            13, operandID=OperandId.itm_attr, arg1=e_tgt_itms['expressionID'],
            arg2=e_tgt_attr3['expressionID'])
        e_optr_tgt1 = self.ef.make(
            14, operandID=OperandId.optr_tgt, arg1=e_optr['expressionID'],
            arg2=e_tgt_spec1['expressionID'])
        e_optr_tgt2 = self.ef.make(
            15, operandID=OperandId.optr_tgt, arg1=e_optr['expressionID'],
            arg2=e_tgt_spec2['expressionID'])
        e_optr_tgt3 = self.ef.make(
            16, operandID=OperandId.optr_tgt, arg1=e_optr['expressionID'],
            arg2=e_tgt_spec3['expressionID'])
        e_add_mod1 = self.ef.make(
            17, operandID=OperandId.add_dom_srq_mod,
            arg1=e_optr_tgt1['expressionID'], arg2=e_src_attr1['expressionID'])
        e_add_mod2 = self.ef.make(
            18, operandID=OperandId.add_dom_srq_mod,
            arg1=e_optr_tgt2['expressionID'], arg2=e_src_attr2['expressionID'])
        e_add_mod3 = self.ef.make(
            19, operandID=OperandId.add_dom_srq_mod,
            arg1=e_optr_tgt3['expressionID'], arg2=e_src_attr3['expressionID'])
        e_rm_mod1 = self.ef.make(
            20, operandID=OperandId.rm_dom_srq_mod,
            arg1=e_optr_tgt1['expressionID'], arg2=e_src_attr1['expressionID'])
        e_rm_mod2 = self.ef.make(
            21, operandID=OperandId.rm_dom_srq_mod,
            arg1=e_optr_tgt2['expressionID'], arg2=e_src_attr2['expressionID'])
        e_rm_mod3 = self.ef.make(
            22, operandID=OperandId.rm_dom_srq_mod,
            arg1=e_optr_tgt3['expressionID'], arg2=e_src_attr3['expressionID'])
        e_add_splice1 = self.ef.make(
            23, operandID=OperandId.splice, arg1=e_add_mod1['expressionID'],
            arg2=e_add_mod3['expressionID'])
        e_add_splice2 = self.ef.make(
            24, operandID=OperandId.splice, arg1=e_add_mod2['expressionID'],
            arg2=e_add_splice1['expressionID'])
        e_rm_splice1 = self.ef.make(
            25, operandID=OperandId.splice, arg1=e_rm_mod1['expressionID'],
            arg2=e_rm_mod3['expressionID'])
        e_rm_splice2 = self.ef.make(
            26, operandID=OperandId.splice, arg1=e_rm_mod2['expressionID'],
            arg2=e_rm_splice1['expressionID'])
        effect_row = {
            'preExpression': e_add_splice2['expressionID'],
            'postExpression': e_rm_splice2['expressionID']}
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success)
        self.assertEqual(len(modifiers), 3)
        self.assert_log_entries(0)
