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
from eos.tests.modifierBuilder.environment import DataHandler, callize
from eos.util.callableData import CallableData


class TestActionBuilderError(EosTestCase):
    """Test reaction to errors occurred during action building stage"""

    def testData(self):
        # Check reaction to expression data fetch errors
        callablePre = CallableData(callable=DataHandler({}).getExpression, args=(902,), kwargs={})
        callablePost = CallableData(callable=DataHandler({}).getExpression, args=(28,), kwargs={})
        effect = Effect(900, 0, preExpressionCallData=callablePre, postExpressionCallData=callablePost)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 900: unable to fetch expression 902")

    def testGeneric(self):
        ePreStub = Expression(1, 27, value="1")
        ePost = Expression(2, 1009)
        effect = Effect(568, 0, preExpressionCallData=callize(ePreStub), postExpressionCallData=callize(ePost))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 568: unknown generic operand 1009")

    def testIntStub(self):
        ePreStub = Expression(1, 27, value="0")
        ePost = Expression(2, 27, value="6")
        effect = Effect(662, 0, preExpressionCallData=callize(ePreStub), postExpressionCallData=callize(ePost))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 662: integer stub with unexpected value 6")

    def testBoolStub(self):
        ePreStub = Expression(1, 27, value="0")
        ePost = Expression(2, 23, value="False")
        effect = Effect(92, 0, preExpressionCallData=callize(ePreStub), postExpressionCallData=callize(ePost))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 92: boolean stub with unexpected value False")

    def testUnknown(self):
        # Check reaction to any errors of action builder,
        # which are not specifically processed by it
        ePreStub = Expression(1, 27, value="0")
        ePost = Expression(2, 23, value="Garbage")
        effect = Effect(66, 0, preExpressionCallData=callize(ePreStub), postExpressionCallData=callize(ePost))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.ERROR)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 66 due to unknown reason")

    def testValidation(self):
        # To make invalid action, we've just took location
        # and group- filtered expression tree and replaced its
        # actual top-level operands with operand describing
        # direct modification
        eTgtLoc = Expression(None, 24, value="Ship")
        eTgtGrp = Expression(None, 26, expressionGroupId=46)
        eTgtAttr = Expression(None, 22, expressionAttributeId=6)
        eOptr = Expression(None, 21, value="PostPercent")
        eSrcAttr = Expression(None, 22, expressionAttributeId=1576)
        eTgtItms = Expression(None, 48, arg1=eTgtLoc, arg2=eTgtGrp)
        eTgtSpec = Expression(None, 12, arg1=eTgtItms, arg2=eTgtAttr)
        eOptrTgt = Expression(None, 31, arg1=eOptr, arg2=eTgtSpec)
        eAddMod = Expression(1, 6, arg1=eOptrTgt, arg2=eSrcAttr)
        eRmMod = Expression(2, 58, arg1=eOptrTgt, arg2=eSrcAttr)
        effect = Effect(20807, 0, preExpressionCallData=callize(eAddMod), postExpressionCallData=callize(eRmMod))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "failed to parse expressions of effect 20807: failed to validate action")
