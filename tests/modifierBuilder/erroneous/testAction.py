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


class TestActionBuilderError(ModBuilderTestCase):
    """Test reaction to errors occurred during action building stage"""

    def testDataIndirect(self):
        # Check reaction to expression data fetch errors,
        # if they occur not for root expression
        splice = self.ef.make(1, operandId=17, arg1Id=37, arg2Id=105)
        modifiers, status = self.runBuilder(splice['expressionId'], splice['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        expected = 'failed to parse tree with base 1-1 and effect category 0: unable to fetch expression 37'
        self.assertEqual(logRecord.msg, expected)

    def testGeneric(self):
        ePreStub = self.ef.make(1, operandId=27, expressionValue='1')
        ePost = self.ef.make(2, operandId=1009)
        modifiers, status = self.runBuilder(ePreStub['expressionId'], ePost['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        expected = 'failed to parse tree with base 1-2 and effect category 0: unknown generic operand 1009'
        self.assertEqual(logRecord.msg, expected)

    def testIntStub(self):
        ePreStub = self.ef.make(1, operandId=27, expressionValue='0')
        ePost = self.ef.make(2, operandId=27, expressionValue='6')
        modifiers, status = self.runBuilder(ePreStub['expressionId'], ePost['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        expected = 'failed to parse tree with base 1-2 and effect category 0: integer stub with unexpected value 6'
        self.assertEqual(logRecord.msg, expected)

    def testBoolStub(self):
        ePreStub = self.ef.make(1, operandId=27, expressionValue='0')
        ePost = self.ef.make(2, operandId=23, expressionValue='False')
        modifiers, status = self.runBuilder(ePreStub['expressionId'], ePost['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        expected = 'failed to parse tree with base 1-2 and effect category 0: boolean stub with unexpected value False'
        self.assertEqual(logRecord.msg, expected)

    def testUnknown(self):
        # Check reaction to any errors of action builder,
        # which are not specifically processed by it
        ePreStub = self.ef.make(1, operandId=27, expressionValue='0')
        ePost = self.ef.make(2, operandId=23, expressionValue='Garbage')
        modifiers, status = self.runBuilder(ePreStub['expressionId'], ePost['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        expected = 'failed to parse tree with base 1-2 and effect category 0 due to unknown reason'
        self.assertEqual(logRecord.msg, expected)

    def testValidation(self):
        # To make invalid action, we've just took location
        # and group- filtered expression tree and replaced its
        # actual top-level operands with operand describing
        # direct modification
        eTgtLoc = self.ef.make(1, operandId=24, expressionValue='Ship')
        eTgtGrp = self.ef.make(2, operandId=26, expressionGroupId=46)
        eTgtAttr = self.ef.make(3, operandId=22, expressionAttributeId=6)
        eOptr = self.ef.make(4, operandId=21, expressionValue='PostPercent')
        eSrcAttr = self.ef.make(5, operandId=22, expressionAttributeId=1576)
        eTgtItms = self.ef.make(6, operandId=48, arg1Id=eTgtLoc['expressionId'], arg2Id=eTgtGrp['expressionId'])
        eTgtSpec = self.ef.make(7, operandId=12, arg1Id=eTgtItms['expressionId'], arg2Id=eTgtAttr['expressionId'])
        eOptrTgt = self.ef.make(8, operandId=31, arg1Id=eOptr['expressionId'], arg2Id=eTgtSpec['expressionId'])
        eAddMod = self.ef.make(9, operandId=6, arg1Id=eOptrTgt['expressionId'], arg2Id=eSrcAttr['expressionId'])
        eRmMod = self.ef.make(10, operandId=58, arg1Id=eOptrTgt['expressionId'], arg2Id=eSrcAttr['expressionId'])
        modifiers, status = self.runBuilder(eAddMod['expressionId'], eRmMod['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        expected = 'failed to parse tree with base 9-10 and effect category 0: failed to validate action'
        self.assertEqual(logRecord.msg, expected)
