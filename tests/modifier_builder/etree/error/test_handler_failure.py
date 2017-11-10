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


import logging

from eos.const.eos import EffectBuildStatus
from eos.const.eve import OperandId
from tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestBuilderEtreeErrorsHandlerFailure(ModBuilderTestCase):

    def setUp(self):
        ModBuilderTestCase.setUp(self)
        e_tgt = self.ef.make(
            1, operandID=OperandId.def_dom, expressionValue='UnknownDomain')
        e_tgt_attr = self.ef.make(
            2, operandID=OperandId.def_attr, expressionAttributeID=9)
        e_optr = self.ef.make(
            3, operandID=OperandId.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(
            4, operandID=OperandId.def_attr, expressionAttributeID=327)
        e_tgt_spec = self.ef.make(
            5, operandID=OperandId.itm_attr, arg1=e_tgt['expressionID'],
            arg2=e_tgt_attr['expressionID'])
        e_optr_tgt = self.ef.make(
            6, operandID=OperandId.optr_tgt, arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID'])
        self.e_add_mod_error = self.ef.make(
            7, operandID=OperandId.add_itm_mod, arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID'])
        self.e_rm_mod_error = self.ef.make(
            8, operandID=OperandId.rm_itm_mod, arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID'])

    def test_single(self):
        effect_row = {
            'preExpression': self.e_add_mod_error['expressionID'],
            'postExpression': self.e_rm_mod_error['expressionID']}
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(
            log_record.name,
            'eos.data.eve_obj_builder.modifier_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        self.assertEqual(
            log_record.msg, 'effect 1, building 1 modifiers: 1 build errors')

    def test_partial_error_first(self):
        e_tgt = self.ef.make(
            9, operandID=OperandId.def_dom, expressionValue='Ship')
        e_tgt_attr = self.ef.make(
            10, operandID=OperandId.def_attr, expressionAttributeID=9)
        e_optr = self.ef.make(
            11, operandID=OperandId.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(
            12, operandID=OperandId.def_attr, expressionAttributeID=327)
        e_tgt_spec = self.ef.make(
            13, operandID=OperandId.itm_attr, arg1=e_tgt['expressionID'],
            arg2=e_tgt_attr['expressionID'])
        e_optr_tgt = self.ef.make(
            14, operandID=OperandId.optr_tgt, arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID'])
        e_add_mod_valid = self.ef.make(
            15, operandID=OperandId.add_itm_mod,
            arg1=e_optr_tgt['expressionID'], arg2=e_src_attr['expressionID'])
        e_rm_mod_valid = self.ef.make(
            16, operandID=OperandId.rm_itm_mod, arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID'])
        e_add_splice = self.ef.make(
            17, operandID=OperandId.splice,
            arg1=self.e_add_mod_error['expressionID'],
            arg2=e_add_mod_valid['expressionID'])
        e_rm_splice = self.ef.make(
            18, operandID=OperandId.splice,
            arg1=self.e_rm_mod_error['expressionID'],
            arg2=e_rm_mod_valid['expressionID'])
        effect_row = {
            'preExpression': e_add_splice['expressionID'],
            'postExpression': e_rm_splice['expressionID']}
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(
            log_record.name,
            'eos.data.eve_obj_builder.modifier_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        self.assertEqual(
            log_record.msg, 'effect 1, building 2 modifiers: 1 build errors')

    def test_partial_error_last(self):
        e_tgt = self.ef.make(
            9, operandID=OperandId.def_dom, expressionValue='Ship')
        e_tgt_attr = self.ef.make(
            10, operandID=OperandId.def_attr, expressionAttributeID=9)
        e_optr = self.ef.make(
            11, operandID=OperandId.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(
            12, operandID=OperandId.def_attr, expressionAttributeID=327)
        e_tgt_spec = self.ef.make(
            13, operandID=OperandId.itm_attr, arg1=e_tgt['expressionID'],
            arg2=e_tgt_attr['expressionID'])
        e_optr_tgt = self.ef.make(
            14, operandID=OperandId.optr_tgt, arg1=e_optr['expressionID'],
            arg2=e_tgt_spec['expressionID'])
        e_add_mod_valid = self.ef.make(
            15, operandID=OperandId.add_itm_mod,
            arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID'])
        e_rm_mod_valid = self.ef.make(
            16, operandID=OperandId.rm_itm_mod, arg1=e_optr_tgt['expressionID'],
            arg2=e_src_attr['expressionID'])
        e_add_splice = self.ef.make(
            17, operandID=OperandId.splice,
            arg1=e_add_mod_valid['expressionID'],
            arg2=self.e_add_mod_error['expressionID'])
        e_rm_splice = self.ef.make(
            18, operandID=OperandId.splice, arg1=e_rm_mod_valid['expressionID'],
            arg2=self.e_rm_mod_error['expressionID'])
        effect_row = {
            'preExpression': e_add_splice['expressionID'],
            'postExpression': e_rm_splice['expressionID']}
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.success_partial)
        self.assertEqual(len(modifiers), 1)
        log = self.get_log()
        self.assertEqual(len(log), 1)
        log_record = log[0]
        self.assertEqual(
            log_record.name,
            'eos.data.eve_obj_builder.modifier_builder.builder')
        self.assertEqual(log_record.levelno, logging.ERROR)
        self.assertEqual(
            log_record.msg, 'effect 1, building 2 modifiers: 1 build errors')
