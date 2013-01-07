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
from eos.fit.attributeCalculator.modifier.modifierBuilder import ModifierBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase


class TestActionBuilderError(EosTestCase):
    """Test reaction to errors occurred during action building stage"""

    def testDataIndirect(self):
        # Check reaction to expression data fetch errors,
        # if they occur not for root expression
        splice = self.ch.expression(expressionId=1, operandId=17, arg1Id=37, arg2Id=105)
        effect = self.ch.effect(effectId=900, categoryId=0, preExpressionId=splice.id, postExpressionId=splice.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        self.assertEqual(logRecord.msg, 'failed to parse expressions of effect 900: unable to fetch expression 37')

    def testGeneric(self):
        ePreStub = self.ch.expression(expressionId=1, operandId=27, value='1')
        ePost = self.ch.expression(expressionId=2, operandId=1009)
        effect = self.ch.effect(effectId=568, categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, 'failed to parse expressions of effect 568: unknown generic operand 1009')

    def testIntStub(self):
        ePreStub = self.ch.expression(expressionId=1, operandId=27, value='0')
        ePost = self.ch.expression(expressionId=2, operandId=27, value='6')
        effect = self.ch.effect(effectId=662, categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, 'failed to parse expressions of effect 662: integer stub with unexpected value 6')

    def testBoolStub(self):
        ePreStub = self.ch.expression(expressionId=1, operandId=27, value='0')
        ePost = self.ch.expression(expressionId=2, operandId=23, value='False')
        effect = self.ch.effect(effectId=92, categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, 'failed to parse expressions of effect 92: boolean stub with unexpected value False')

    def testUnknown(self):
        # Check reaction to any errors of action builder,
        # which are not specifically processed by it
        ePreStub = self.ch.expression(expressionId=1, operandId=27, value='0')
        ePost = self.ch.expression(expressionId=2, operandId=23, value='Garbage')
        effect = self.ch.effect(effectId=66, categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        self.assertEqual(logRecord.msg, 'failed to parse expressions of effect 66 due to unknown reason')

    def testValidation(self):
        # To make invalid action, we've just took location
        # and group- filtered expression tree and replaced its
        # actual top-level operands with operand describing
        # direct modification
        eTgtLoc = self.ch.expression(expressionId=1, operandId=24, value='Ship')
        eTgtGrp = self.ch.expression(expressionId=2, operandId=26, expressionGroupId=46)
        eTgtAttr = self.ch.expression(expressionId=3, operandId=22, expressionAttributeId=6)
        eOptr = self.ch.expression(expressionId=4, operandId=21, value='PostPercent')
        eSrcAttr = self.ch.expression(expressionId=5, operandId=22, expressionAttributeId=1576)
        eTgtItms = self.ch.expression(expressionId=6, operandId=48, arg1Id=eTgtLoc.id, arg2Id=eTgtGrp.id)
        eTgtSpec = self.ch.expression(expressionId=7, operandId=12, arg1Id=eTgtItms.id, arg2Id=eTgtAttr.id)
        eOptrTgt = self.ch.expression(expressionId=8, operandId=31, arg1Id=eOptr.id, arg2Id=eTgtSpec.id)
        eAddMod = self.ch.expression(expressionId=9, operandId=6, arg1Id=eOptrTgt.id, arg2Id=eSrcAttr.id)
        eRmMod = self.ch.expression(expressionId=10, operandId=58, arg1Id=eOptrTgt.id, arg2Id=eSrcAttr.id)
        effect = self.ch.effect(effectId=20807, categoryId=0, preExpressionId=eAddMod.id, postExpressionId=eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, 'eos_test.modifierBuilder')
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, 'failed to parse expressions of effect 20807: failed to validate action')
