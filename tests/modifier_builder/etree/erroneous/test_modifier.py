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


import logging

from eos.const.eos import EffectBuildStatus
from eos.const.eve import EffectCategory, Operand
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderEtreeModifierError(ModBuilderTestCase):
    """Test reaction to errors occurred during modifier building stage"""

    def test_data_direct(self):
        # Check reaction to expression data fetch errors
        effect_row = {
            'effect_id': 915,
            'pre_expression': 902,
            'post_expression': 28,
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.expression_tree.effect2modifiers')
        self.assertEqual(log_record.levelno, logging.ERROR)
        expected = 'failed to parse expression tree of effect 915: unable to fetch expression 902'
        self.assertEqual(log_record.msg, expected)

    def test_unused_actions(self):
        # To produce unused actions, we're passing just tree
        # which describes action which applies something, and
        # stub instead of action undoing it
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
        e_add_mod = self.ef.make(
            7, operandID=Operand.add_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        e_post_stub = self.ef.make(8, operandID=Operand.def_int, expressionValue='1')
        effect_row = {
            'effect_id': 29,
            'pre_expression': e_add_mod['expressionID'],
            'post_expression': e_post_stub['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.ok_partial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.expression_tree.effect2modifiers')
        self.assertEqual(log_record.levelno, logging.WARNING)
        expected = 'unused actions left after parsing expression tree of effect 29'
        self.assertEqual(log_record.msg, expected)
