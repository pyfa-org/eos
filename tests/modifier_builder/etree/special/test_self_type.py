# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2015 Anton Vorobyov
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


from eos.const.eos import EffectBuildStatus, FilterType
from eos.const.eve import EffectCategory, Operand
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderEtreeSelfType(ModBuilderTestCase):
    """Test parsing of trees describing modification which contains reference to typeID of its carrier"""

    def test_build_success(self):
        e_tgt_own = self.ef.make(1, operandID=Operand.def_loc, expressionValue='Char')
        e_self = self.ef.make(2, operandID=Operand.def_loc, expressionValue='Self')
        e_self_type = self.ef.make(3, operandID=Operand.get_type, arg1=e_self['expressionID'])
        e_tgt_attr = self.ef.make(4, operandID=Operand.def_attr, expressionAttributeID=64)
        e_optr = self.ef.make(5, operandID=Operand.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(6, operandID=Operand.def_attr, expressionAttributeID=292)
        e_tgt_itms = self.ef.make(
            7, operandID=Operand.loc_srq,
            arg1=e_tgt_own['expressionID'],
            arg2=e_self_type['expressionID']
        )
        e_tgt_spec = self.ef.make(
            8, operandID=Operand.itm_attr,
            arg1=e_tgt_itms['expressionID'],
            arg2=e_tgt_attr['expressionID']
        )
        e_optr_tgt = self.ef.make(
            9, operandID=Operand.optr_tgt,
            arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID']
        )
        e_add_mod = self.ef.make(
            10, operandID=Operand.add_own_srq_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        e_rm_mod = self.ef.make(
            11, operandID=Operand.rm_own_srq_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        effect_row = {
            'pre_expression': e_add_mod['expressionID'],
            'post_expression': e_rm_mod['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.filter_type, FilterType.skill_self)
        self.assertEqual(modifier.filter_value, None)
        self.assertEqual(len(self.log), 0)
