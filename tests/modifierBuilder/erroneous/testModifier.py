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


class TestModifierBuilderError(EosTestCase):
    """Test reaction to errors occurred during modifier building stage"""

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

    def testUnusedActions(self):
        dh = DataHandler()
        # To produce unused actions, we're passing just tree
        # which describes action which applies something, and
        # stub instead of action undoing it
        eTgt = Expression(dataHandler=dh, expressionId=1, operandId=24, value="Ship")
        eTgtAttr = Expression(dataHandler=dh, expressionId=2, operandId=22, expressionAttributeId=9)
        eOptr = Expression(dataHandler=dh, expressionId=3, operandId=21, value="PostPercent")
        eSrcAttr = Expression(dataHandler=dh, expressionId=4, operandId=22, expressionAttributeId=327)
        eTgtSpec = Expression(dataHandler=dh, expressionId=5, operandId=12, arg1Id=eTgt.id, arg2Id=eTgtAttr.id)
        eOptrTgt = Expression(dataHandler=dh, expressionId=6, operandId=31, arg1Id=eOptr.id, arg2Id=eTgtSpec.id)
        eAddMod = Expression(dataHandler=dh, expressionId=7, operandId=6, arg1Id=eOptrTgt.id, arg2Id=eSrcAttr.id)
        ePostStub = Expression(dataHandler=dh, expressionId=8, operandId=27, value="1")
        dh.addExpressions((eTgt, eTgtAttr, eOptr, eSrcAttr, eTgtSpec, eOptrTgt, eAddMod, ePostStub))
        effect = Effect(dataHandler=dh, effectId=799, categoryId=0, preExpressionId=eAddMod.id, postExpressionId=ePostStub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
        logRecord = self.log[0]
        self.assertEqual(logRecord.name, "eos_test.modifierBuilder")
        self.assertEqual(logRecord.levelno, Logger.WARNING)
        self.assertEqual(logRecord.msg, "unused actions left after generating modifiers for effect 799")
