#===============================================================================
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
#===============================================================================


from eos.const.eos import EffectBuildStatus
from eos.const.eve import EffectCategory, Operand
from eos.tests.environment import Logger
from eos.tests.modifier_builder.modbuilder_testcase import ModBuilderTestCase


class TestActionBuilderError(ModBuilderTestCase):
    """Test reaction to errors occurred during action building stage"""

    def test_data_indirect(self):
        # Check reaction to expression data fetch errors,
        # if they occur not for root expression
        splice = self.ef.make(1, operandID=Operand.splice, arg1=37, arg2=105)
        modifiers, status = self.run_builder(splice['expressionID'],
                                             splice['expressionID'],
                                             EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.modifier_builder')
        self.assertEqual(log_record.levelno, Logger.ERROR)
        expected = 'failed to parse tree with base 1-1 and effect category 0: unable to fetch expression 37'
        self.assertEqual(log_record.msg, expected)

    def test_generic(self):
        e_pre_stub = self.ef.make(1, operandID=Operand.def_int, expressionValue='1')
        e_post = self.ef.make(2, operandID=1009)
        modifiers, status = self.run_builder(e_pre_stub['expressionID'],
                                             e_post['expressionID'],
                                             EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.modifier_builder')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        expected = 'failed to parse tree with base 1-2 and effect category 0: unknown generic operand 1009'
        self.assertEqual(log_record.msg, expected)

    def test_int_stub(self):
        e_pre_stub = self.ef.make(1, operandID=Operand.def_int, expressionValue='0')
        e_post = self.ef.make(2, operandID=Operand.def_int, expressionValue='6')
        modifiers, status = self.run_builder(e_pre_stub['expressionID'],
                                             e_post['expressionID'],
                                             EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.modifier_builder')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        expected = 'failed to parse tree with base 1-2 and effect category 0: integer stub with unexpected value 6'
        self.assertEqual(log_record.msg, expected)

    def test_bool_stub(self):
        e_pre_stub = self.ef.make(1, operandID=Operand.def_int, expressionValue='0')
        e_post = self.ef.make(2, operandID=Operand.def_bool, expressionValue='False')
        modifiers, status = self.run_builder(e_pre_stub['expressionID'],
                                             e_post['expressionID'],
                                             EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.modifier_builder')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        expected = 'failed to parse tree with base 1-2 and effect category 0: boolean stub with unexpected value False'
        self.assertEqual(log_record.msg, expected)

    def test_unknown(self):
        # Check reaction to any errors of action builder,
        # which are not specifically processed by it
        e_pre_stub = self.ef.make(1, operandID=Operand.def_int, expressionValue='0')
        e_post = self.ef.make(2, operandID=Operand.def_bool, expressionValue='Garbage')
        modifiers, status = self.run_builder(e_pre_stub['expressionID'],
                                             e_post['expressionID'],
                                             EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.modifier_builder')
        self.assertEqual(log_record.levelno, Logger.ERROR)
        expected = 'failed to parse tree with base 1-2 and effect category 0 due to unknown reason'
        self.assertEqual(log_record.msg, expected)

    def test_validation(self):
        # To make invalid action, we've just took location
        # and group- filtered expression tree and replaced its
        # actual top-level operands with operand describing
        # direct modification
        e_tgt_loc = self.ef.make(1, operandID=Operand.def_loc, expressionValue='Ship')
        e_tgt_grp = self.ef.make(2, operandID=Operand.def_grp, expressionGroupID=46)
        e_tgt_attr = self.ef.make(3, operandID=Operand.def_attr, expressionAttributeID=6)
        e_optr = self.ef.make(4, operandID=Operand.def_optr, expressionValue='PostPercent')
        e_src_attr = self.ef.make(5, operandID=Operand.def_attr, expressionAttributeID=1576)
        e_tgt_itms = self.ef.make(6, operandID=Operand.loc_grp, arg1=e_tgt_loc['expressionID'],
                                  arg2=e_tgt_grp['expressionID'])
        e_tgt_spec = self.ef.make(7, operandID=Operand.itm_attr, arg1=e_tgt_itms['expressionID'],
                                  arg2=e_tgt_attr['expressionID'])
        e_optr_tgt = self.ef.make(8, operandID=Operand.optr_tgt, arg1=e_optr['expressionID'],
                                  arg2=e_tgt_spec['expressionID'])
        e_add_mod = self.ef.make(9, operandID=Operand.add_itm_mod, arg1=e_optr_tgt['expressionID'],
                                 arg2=e_src_attr['expressionID'])
        e_rm_mod = self.ef.make(10, operandID=Operand.rm_itm_mod, arg1=e_optr_tgt['expressionID'],
                                arg2=e_src_attr['expressionID'])
        modifiers, status = self.run_builder(e_add_mod['expressionID'],
                                             e_rm_mod['expressionID'],
                                             EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos_test.modifier_builder')
        self.assertEqual(log_record.levelno, Logger.WARNING)
        expected = 'failed to parse tree with base 9-10 and effect category 0: failed to validate action'
        self.assertEqual(log_record.msg, expected)
