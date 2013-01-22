#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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


from eos.const import EffectBuildStatus
from eos.tests.environment import Logger
from eos.tests.modifierBuilder.modBuilderTestCase import ModBuilderTestCase


class TestModifierBuilderError(ModBuilderTestCase):
    """Test reaction to errors occurred during modifier building stage"""

    def testDataDirect(self):
        # Check reaction to expression data fetch errors
        modifiers, status = self.runBuilder(902, 28, 0)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        expected = 'failed to parse tree with base 902-28 and effect category 0: unable to fetch expression 902'
        self.assertEqual(logRecord.msg, expected)

    def testUnusedActions(self):
        # To produce unused actions, we're passing just tree
        # which describes action which applies something, and
        # stub instead of action undoing it
        eTgt = self.ef.make(1, operandId=24, expressionValue='Ship')
        eTgtAttr = self.ef.make(2, operandId=22, expressionAttributeId=9)
        eOptr = self.ef.make(3, operandId=21, expressionValue='PostPercent')
        eSrcAttr = self.ef.make(4, operandId=22, expressionAttributeId=327)
        eTgtSpec = self.ef.make(5, operandId=12, arg1Id=eTgt['expressionId'], arg2Id=eTgtAttr['expressionId'])
        eOptrTgt = self.ef.make(6, operandId=31, arg1Id=eOptr['expressionId'], arg2Id=eTgtSpec['expressionId'])
        eAddMod = self.ef.make(7, operandId=6, arg1Id=eOptrTgt['expressionId'], arg2Id=eSrcAttr['expressionId'])
        ePostStub = self.ef.make(8, operandId=27, expressionValue='1')
        modifiers, status = self.runBuilder(eAddMod['expressionId'], ePostStub['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        expected = 'unused actions left after parsing tree with base 7-8 and effect category 0'
        self.assertEqual(logRecord.msg, expected)
