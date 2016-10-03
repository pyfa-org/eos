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


from eos.const.eos import State, Domain, EffectBuildStatus, Scope, Operator
from eos.const.eve import EffectCategory, Operand
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderPriority(ModBuilderTestCase):
    """Check which kind of builder is picked for which case"""

    def setUp(self):
        super().setUp()
        e_tgt = self.ef.make(1, operandID=Operand.def_loc, expressionValue='Ship')
        e_tgt_attr = self.ef.make(2, operandID=Operand.def_attr, expressionAttributeID=9)
        e_optr = self.ef.make(3, operandID=Operand.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(4, operandID=Operand.def_attr, expressionAttributeID=327)
        e_tgt_spec = self.ef.make(
            5, operandID=Operand.itm_attr,
            arg1=e_tgt['expressionID'],
            arg2=e_tgt_attr['expressionID']
        )
        e_optr_tgt = self.ef.make(
            6, operandID=Operand.optr_tgt,
            arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID']
        )
        self.e_add_mod = self.ef.make(
            7, operandID=Operand.add_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        self.e_rm_mod = self.ef.make(
            8, operandID=Operand.rm_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )

    def test_etree(self):
        effect_row = {
            'pre_expression': self.e_add_mod['expressionID'],
            'post_expression': self.e_rm_mod['expressionID'],
            'effect_category': EffectCategory.passive,
            'modifier_info': None
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.scope, Scope.local)
        self.assertEqual(modifier.domain, Domain.ship)
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.src_attr, 327)
        self.assertEqual(modifier.operator, Operator.post_percent)
        self.assertEqual(modifier.tgt_attr, 9)
        self.assertIsNone(modifier.filter_type)
        self.assertIsNone(modifier.filter_value)
        self.assertEqual(len(self.log), 0)

    def test_modinfo(self):
        effect_row = {
            'pre_expression': self.e_add_mod['expressionID'],
            'post_expression': self.e_rm_mod['expressionID'],
            'effect_category': EffectCategory.passive,
            'modifier_info': '- domain: charID\n  func: ItemModifier\n  modifiedAttributeID: 164\n'
                '  modifyingAttributeID: 175\n  operator: 2\n'
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_full)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.scope, Scope.local)
        self.assertEqual(modifier.domain, Domain.character)
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.src_attr, 175)
        self.assertEqual(modifier.operator, Operator.mod_add)
        self.assertEqual(modifier.tgt_attr, 164)
        self.assertIsNone(modifier.filter_type)
        self.assertIsNone(modifier.filter_value)
        self.assertEqual(len(self.log), 0)
