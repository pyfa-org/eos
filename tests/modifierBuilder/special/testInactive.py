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


class TestInactive(EosTestCase):
    """Test parsing of trees involving disabled operands"""

    def setUp(self):
        EosTestCase.setUp(self)
        self.dh = DataHandler()
        self.stub = Expression(dataHandler=self.dh, expressionId=-1, operandId=27, value="1")
        self.dh.addExpressions((self.stub,))

    def testAttack(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=13)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testCargoScan(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=14)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testCheatTeleDock(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=15)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testCheatTeleGate(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=16)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testAoeDecloak(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=19)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testEcmBurst(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=30)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testAoeDmg(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=32)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testMissileLaunch(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=44)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testDefenderLaunch(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=45)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testFofLaunch(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=47)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testMine(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=50)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testPowerBooster(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=53)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testShipScan(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=66)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testSurveyScan(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=69)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testTgtHostile(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=70)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testTgtSilent(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=71)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testToolTgtSkills(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=72)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testUserError(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=73)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testVrfTgtGrp(self):
        disabledPre = Expression(dataHandler=self.dh, expressionId=1, operandId=74)
        self.dh.addExpressions((disabledPre,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
