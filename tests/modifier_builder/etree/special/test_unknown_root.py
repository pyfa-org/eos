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


class TestBuilderEtreeUnknownRoot(ModBuilderTestCase):

    def test_int_stub(self):
        e_stub = self.ef.make(1, operandID=OperandId.def_int, expressionValue='0')
        effect_row = {
            'preExpression': e_stub['expressionID'],
            'postExpression': e_stub['expressionID']
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.skipped)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.eve_obj_builder.modifier_builder.builder')
        self.assertEqual(log_record.levelno, logging.INFO)
        expected = 'failed to build modifiers for effect 1: unknown root operand ID 27'
        self.assertEqual(log_record.msg, expected)

    def test_other(self):
        e_stub = self.ef.make(1, operandID=567)
        effect_row = {
            'preExpression': e_stub['expressionID'],
            'postExpression': e_stub['expressionID']
        }
        modifiers, status = self.run_builder(effect_row)
        self.assertEqual(status, EffectBuildStatus.skipped)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        log_record = self.log[0]
        self.assertEqual(log_record.name, 'eos.data.eve_obj_builder.modifier_builder.builder')
        self.assertEqual(log_record.levelno, logging.INFO)
        expected = 'failed to build modifiers for effect 1: unknown root operand ID 567'
        self.assertEqual(log_record.msg, expected)
