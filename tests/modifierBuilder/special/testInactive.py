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


class TestInactive(EosTestCase):
    """Test parsing of trees involving disabled operands"""

    def setUp(self):
        EosTestCase.setUp(self)
        self.stub = self.ch.expression(expressionId=-1, operandId=27, value="1")

    def testAttack(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=13)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testCargoScan(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=14)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testCheatTeleDock(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=15)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testCheatTeleGate(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=16)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testAoeDecloak(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=19)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testEcmBurst(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=30)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testAoeDmg(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=32)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testMissileLaunch(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=44)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testDefenderLaunch(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=45)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testFofLaunch(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=47)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testMine(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=50)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testPowerBooster(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=53)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testShipScan(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=66)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testSurveyScan(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=69)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testTgtHostile(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=70)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testTgtSilent(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=71)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testToolTgtSkills(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=72)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testUserError(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=73)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testVrfTgtGrp(self):
        disabledPre = self.ch.expression(expressionId=1, operandId=74)
        effect = self.ch.effect(categoryId=0, preExpressionId=disabledPre.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
