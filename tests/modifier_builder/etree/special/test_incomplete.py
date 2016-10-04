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


from eos.const.eos import EffectBuildStatus
from eos.const.eve import EffectCategory, Operand
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderEtreeIncomplete(ModBuilderTestCase):
    """Test parsing of trees, which include actions, which are not converted into modifiers"""

    def setUp(self):
        super().setUp()
        # Modifier, except for top-most expression, which
        # is added in test cases
        e_tgt = self.ef.make(1, operandID=Operand.def_loc, expressionValue='Ship')
        e_tgt_attr = self.ef.make(2, operandID=Operand.def_attr, expressionAttributeID=9)
        e_optr = self.ef.make(3, operandID=Operand.def_optr, expressionValue='PostPercent')
        self.e_src_attr = self.ef.make(4, operandID=Operand.def_attr, expressionAttributeID=327)
        e_tgt_spec = self.ef.make(
            5, operandID=Operand.itm_attr,
            arg1=e_tgt['expressionID'],
            arg2=e_tgt_attr['expressionID']
        )
        self.e_optr_tgt = self.ef.make(
            6, operandID=Operand.optr_tgt,
            arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID']
        )
        self.stub = self.ef.make(7, operandID=Operand.def_int, expressionValue='1')

    def test_rre(self):
        e_add_mod = self.ef.make(
            8, operandID=Operand.add_itm_mod,
            arg1=self.e_optr_tgt['expressionID'],
            arg2=self.e_src_attr['expressionID']
        )
        effect_row = {
            'pre_expression': e_add_mod['expressionID'],
            'post_expression': self.stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)

    def test_post(self):
        e_rm_mod = self.ef.make(
            8, operandID=Operand.rm_itm_mod,
            arg1=self.e_optr_tgt['expressionID'],
            arg2=self.e_src_attr['expressionID']
        )
        effect_row = {
            'pre_expression': self.stub['expressionID'],
            'post_expression': e_rm_mod['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
