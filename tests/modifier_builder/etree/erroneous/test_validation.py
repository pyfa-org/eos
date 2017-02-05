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


import logging

from eos.const.eos import EffectBuildStatus
from eos.const.eve import EffectCategory, Operand
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderEtreeErrorsValidation(ModBuilderTestCase):

    def setUp(self):
        super().setUp()
        e_tgt_own = self.ef.make(1, operandID=Operand.def_dom, expressionValue='Ship')
        e_tgt_srq = self.ef.make(2, operandID=Operand.def_type, expressionTypeID=3412)
        e_tgt_attr = self.ef.make(3, operandID=Operand.def_attr, expressionAttributeID=1372)
        e_optr = self.ef.make(4, operandID=Operand.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(5, operandID=Operand.def_attr, expressionAttributeID=1156)
        e_tgt_itms = self.ef.make(
            6, operandID=Operand.dom_srq,
            arg1=e_tgt_own['expressionID'],
            arg2=e_tgt_srq['expressionID']
        )
        e_tgt_spec = self.ef.make(
            7, operandID=Operand.itm_attr,
            arg1=e_tgt_itms['expressionID'],
            arg2=e_tgt_attr['expressionID']
        )
        e_optr_tgt = self.ef.make(
            8, operandID=Operand.optr_tgt,
            arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID']
        )
        self.e_add_mod_invalid = self.ef.make(
            9, operandID=Operand.add_own_srq_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        self.e_rm_mod_invalid = self.ef.make(
            10, operandID=Operand.rm_own_srq_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )

    def test_single(self):
        effect_row = {
            'pre_expression': self.e_add_mod_invalid['expressionID'],
            'post_expression': self.e_rm_mod_invalid['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        expected = 'effect 1, building 1 modifiers: 1 validation failures'
        self.assertEqual(log_record.msg, expected)

    def test_partial_invalid_first(self):
        e_tgt = self.ef.make(11, operandID=Operand.def_dom, expressionValue='Ship')
        e_tgt_attr = self.ef.make(12, operandID=Operand.def_attr, expressionAttributeID=9)
        e_optr = self.ef.make(13, operandID=Operand.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(14, operandID=Operand.def_attr, expressionAttributeID=327)
        e_tgt_spec = self.ef.make(
            15, operandID=Operand.itm_attr,
            arg1=e_tgt['expressionID'],
            arg2=e_tgt_attr['expressionID']
        )
        e_optr_tgt = self.ef.make(
            16, operandID=Operand.optr_tgt,
            arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID']
        )
        e_add_mod_valid = self.ef.make(
            17, operandID=Operand.add_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        e_rm_mod_valid = self.ef.make(
            18, operandID=Operand.rm_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        e_add_splice = self.ef.make(
            19, operandID=Operand.splice,
            arg1=self.e_add_mod_invalid['expressionID'],
            arg2=e_add_mod_valid['expressionID']
        )
        e_rm_splice = self.ef.make(
            20, operandID=Operand.splice,
            arg1=self.e_rm_mod_invalid['expressionID'],
            arg2=e_rm_mod_valid['expressionID']
        )
        effect_row = {
            'pre_expression': e_add_splice['expressionID'],
            'post_expression': e_rm_splice['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        expected = 'effect 1, building 2 modifiers: 1 validation failures'
        self.assertEqual(log_record.msg, expected)

    def test_partial_invalid_last(self):
        e_tgt = self.ef.make(11, operandID=Operand.def_dom, expressionValue='Ship')
        e_tgt_attr = self.ef.make(12, operandID=Operand.def_attr, expressionAttributeID=9)
        e_optr = self.ef.make(13, operandID=Operand.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(14, operandID=Operand.def_attr, expressionAttributeID=327)
        e_tgt_spec = self.ef.make(
            15, operandID=Operand.itm_attr,
            arg1=e_tgt['expressionID'],
            arg2=e_tgt_attr['expressionID']
        )
        e_optr_tgt = self.ef.make(
            16, operandID=Operand.optr_tgt,
            arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID']
        )
        e_add_mod_valid = self.ef.make(
            17, operandID=Operand.add_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        e_rm_mod_valid = self.ef.make(
            18, operandID=Operand.rm_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        e_add_splice = self.ef.make(
            19, operandID=Operand.splice,
            arg1=e_add_mod_valid['expressionID'],
            arg2=self.e_add_mod_invalid['expressionID']
        )
        e_rm_splice = self.ef.make(
            20, operandID=Operand.splice,
            arg1=e_rm_mod_valid['expressionID'],
            arg2=self.e_rm_mod_invalid['expressionID']
        )
        effect_row = {
            'pre_expression': e_add_splice['expressionID'],
            'post_expression': e_rm_splice['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        expected = 'effect 1, building 2 modifiers: 1 validation failures'
        self.assertEqual(log_record.msg, expected)

    def test_building_and_validation_failure(self):
        e_tgt = self.ef.make(11, operandID=Operand.def_dom, expressionValue='Ship')
        e_tgt_attr = self.ef.make(12, operandID=Operand.def_attr, expressionAttributeID=9)
        e_optr = self.ef.make(13, operandID=Operand.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(14, operandID=Operand.def_attr, expressionAttributeID=327)
        e_tgt_spec = self.ef.make(
            15, operandID=Operand.itm_attr,
            arg1=e_tgt['expressionID'],
            arg2=e_tgt_attr['expressionID']
        )
        e_optr_tgt = self.ef.make(
            16, operandID=Operand.optr_tgt,
            arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID']
        )
        e_add_mod_valid = self.ef.make(
            17, operandID=Operand.add_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        e_rm_mod_valid = self.ef.make(
            18, operandID=Operand.rm_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID']
        )
        e_mod_error = self.ef.make(19, operandID=Operand.def_grp)
        e_add_splice1 = self.ef.make(
            20, operandID=Operand.splice,
            arg1=self.e_add_mod_invalid['expressionID'],
            arg2=e_add_mod_valid['expressionID']
        )
        e_rm_splice1 = self.ef.make(
            21, operandID=Operand.splice,
            arg1=self.e_rm_mod_invalid['expressionID'],
            arg2=e_rm_mod_valid['expressionID']
        )
        e_add_splice2 = self.ef.make(
            22, operandID=Operand.splice,
            arg1=e_mod_error['expressionID'],
            arg2=e_add_splice1['expressionID']
        )
        e_rm_splice2 = self.ef.make(
            23, operandID=Operand.splice,
            arg1=e_mod_error['expressionID'],
            arg2=e_rm_splice1['expressionID']
        )
        effect_row = {
            'pre_expression': e_add_splice2['expressionID'],
            'post_expression': e_rm_splice2['expressionID'],
            'effect_category': EffectCategory.passive
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.cache_generator.modifier_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        expected = 'effect 1, building 3 modifiers: 1 build errors, 1 validation failures'
        self.assertEqual(log_record.msg, expected)
