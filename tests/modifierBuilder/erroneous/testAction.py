#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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
from eos.eve.effect import Effect
from eos.eve.expression import Expression
from eos.fit.attributeCalculator.modifier.modifierBuilder import ModifierBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase
from eos.tests.modifierBuilder.environment import DataHandler


class TestActionBuilderError(EosTestCase):
    """Test reaction to errors occurred during action building stage"""

    def testDataDirect(self):
        dh = DataHandler()
        # Check reaction to expression data fetch errors
        effect = Effect(dataHandler=dh, effectId=900, categoryId=0, preExpressionId=902, postExpressionId=28)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 900: unable to fetch expression 902")

    def testDataIndirect(self):
        dh = DataHandler()
        # Check reaction to expression data fetch errors,
        # if they occur not for root expression
        splice = Expression(dataHandler=dh, expressionId=1, operandId=17, arg1Id=37, arg2Id=105)
        effect = Effect(dataHandler=dh, effectId=900, categoryId=0, preExpressionId=1, postExpressionId=1)
        dh.addExpressions((splice,))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 900: unable to fetch expression 37")

    def testGeneric(self):
        dh = DataHandler()
        ePreStub = Expression(dataHandler=dh, expressionId=1, operandId=27, value="1")
        ePost = Expression(dataHandler=dh, expressionId=2, operandId=1009)
        dh.addExpressions((ePreStub, ePost))
        effect = Effect(dataHandler=dh, effectId=568, categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 568: unknown generic operand 1009")

    def testIntStub(self):
        dh = DataHandler()
        ePreStub = Expression(dataHandler=dh, expressionId=1, operandId=27, value="0")
        ePost = Expression(dataHandler=dh, expressionId=2, operandId=27, value="6")
        dh.addExpressions((ePreStub, ePost))
        effect = Effect(dataHandler=dh, effectId=662, categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 662: integer stub with unexpected value 6")

    def testBoolStub(self):
        dh = DataHandler()
        ePreStub = Expression(dataHandler=dh, expressionId=1, operandId=27, value="0")
        ePost = Expression(dataHandler=dh, expressionId=2, operandId=23, value="False")
        dh.addExpressions((ePreStub, ePost))
        effect = Effect(dataHandler=dh, effectId=92, categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 92: boolean stub with unexpected value False")

    def testUnknown(self):
        dh = DataHandler()
        # Check reaction to any errors of action builder,
        # which are not specifically processed by it
        ePreStub = Expression(dataHandler=dh, expressionId=1, operandId=27, value="0")
        ePost = Expression(dataHandler=dh, expressionId=2, operandId=23, value="Garbage")
        dh.addExpressions((ePreStub, ePost))
        effect = Effect(dataHandler=dh, effectId=66, categoryId=0, preExpressionId=ePreStub.id, postExpressionId=ePost.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 66 due to unknown reason")

    def testValidation(self):
        dh = DataHandler()
        # To make invalid action, we've just took location
        # and group- filtered expression tree and replaced its
        # actual top-level operands with operand describing
        # direct modification
        eTgtLoc = Expression(dataHandler=dh, expressionId=1, operandId=24, value="Ship")
        eTgtGrp = Expression(dataHandler=dh, expressionId=2, operandId=26, expressionGroupId=46)
        eTgtAttr = Expression(dataHandler=dh, expressionId=3, operandId=22, expressionAttributeId=6)
        eOptr = Expression(dataHandler=dh, expressionId=4, operandId=21, value="PostPercent")
        eSrcAttr = Expression(dataHandler=dh, expressionId=5, operandId=22, expressionAttributeId=1576)
        eTgtItms = Expression(dataHandler=dh, expressionId=6, operandId=48, arg1Id=eTgtLoc.id, arg2Id=eTgtGrp.id)
        eTgtSpec = Expression(dataHandler=dh, expressionId=7, operandId=12, arg1Id=eTgtItms.id, arg2Id=eTgtAttr.id)
        eOptrTgt = Expression(dataHandler=dh, expressionId=8, operandId=31, arg1Id=eOptr.id, arg2Id=eTgtSpec.id)
        eAddMod = Expression(dataHandler=dh, expressionId=9, operandId=6, arg1Id=eOptrTgt.id, arg2Id=eSrcAttr.id)
        eRmMod = Expression(dataHandler=dh, expressionId=10, operandId=58, arg1Id=eOptrTgt.id, arg2Id=eSrcAttr.id)
        dh.addExpressions((eTgtLoc, eTgtGrp, eTgtAttr, eOptr, eSrcAttr, eTgtItms, eTgtSpec, eOptrTgt, eAddMod, eRmMod))
        effect = Effect(dataHandler=dh, effectId=20807, categoryId=0, preExpressionId=eAddMod.id, postExpressionId=eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 20807: failed to validate action")
