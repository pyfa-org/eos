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


from eos.const.eos import EffectBuildStatus
from eos.const.eve import EffectCategory, Operand
from eos.tests.environment import Logger
from eos.tests.modifierBuilder.modBuilderTestCase import ModBuilderTestCase


class TestActionBuilderError(ModBuilderTestCase):
    """Test reaction to errors occurred during action building stage"""

    def testDataIndirect(self):
        # Check reaction to expression data fetch errors,
        # if they occur not for root expression
        splice = self.ef.make(1, operandID=Operand.splice, arg1=37, arg2=105)
        modifiers, status = self.runBuilder(splice['expressionID'], splice['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        expected = 'failed to parse tree with base 1-1 and effect category 0: unable to fetch expression 37'
        self.assertEqual(logRecord.msg, expected)

    def testGeneric(self):
        ePreStub = self.ef.make(1, operandID=Operand.defInt, expressionValue='1')
        ePost = self.ef.make(2, operandID=1009)
        modifiers, status = self.runBuilder(ePreStub['expressionID'], ePost['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        expected = 'failed to parse tree with base 1-2 and effect category 0: unknown generic operand 1009'
        self.assertEqual(logRecord.msg, expected)

    def testIntStub(self):
        ePreStub = self.ef.make(1, operandID=Operand.defInt, expressionValue='0')
        ePost = self.ef.make(2, operandID=Operand.defInt, expressionValue='6')
        modifiers, status = self.runBuilder(ePreStub['expressionID'], ePost['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        expected = 'failed to parse tree with base 1-2 and effect category 0: integer stub with unexpected value 6'
        self.assertEqual(logRecord.msg, expected)

    def testBoolStub(self):
        ePreStub = self.ef.make(1, operandID=Operand.defInt, expressionValue='0')
        ePost = self.ef.make(2, operandID=Operand.defBool, expressionValue='False')
        modifiers, status = self.runBuilder(ePreStub['expressionID'], ePost['expressionID'], EffectCategory.passive)
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
        ePreStub = self.ef.make(1, operandID=Operand.defInt, expressionValue='0')
        ePost = self.ef.make(2, operandID=Operand.defBool, expressionValue='Garbage')
        modifiers, status = self.runBuilder(ePreStub['expressionID'], ePost['expressionID'], EffectCategory.passive)
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
        eTgtLoc = self.ef.make(1, operandID=Operand.defLoc, expressionValue='Ship')
        eTgtGrp = self.ef.make(2, operandID=Operand.defGrp, expressionGroupID=46)
        eTgtAttr = self.ef.make(3, operandID=Operand.defAttr, expressionAttributeID=6)
        eOptr = self.ef.make(4, operandID=Operand.defOptr, expressionValue='PostPercent')
        eSrcAttr = self.ef.make(5, operandID=Operand.defAttr, expressionAttributeID=1576)
        eTgtItms = self.ef.make(6, operandID=Operand.locGrp, arg1=eTgtLoc['expressionID'], arg2=eTgtGrp['expressionID'])
        eTgtSpec = self.ef.make(7, operandID=Operand.itmAttr, arg1=eTgtItms['expressionID'], arg2=eTgtAttr['expressionID'])
        eOptrTgt = self.ef.make(8, operandID=Operand.optrTgt, arg1=eOptr['expressionID'], arg2=eTgtSpec['expressionID'])
        eAddMod = self.ef.make(9, operandID=Operand.addItmMod, arg1=eOptrTgt['expressionID'], arg2=eSrcAttr['expressionID'])
        eRmMod = self.ef.make(10, operandID=Operand.rmItmMod, arg1=eOptrTgt['expressionID'], arg2=eSrcAttr['expressionID'])
        modifiers, status = self.runBuilder(eAddMod['expressionID'], eRmMod['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        expected = 'failed to parse tree with base 9-10 and effect category 0: failed to validate action'
        self.assertEqual(logRecord.msg, expected)
