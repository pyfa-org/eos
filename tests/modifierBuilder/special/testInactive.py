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
from eos.tests.modifierBuilder.modBuilderTestCase import ModBuilderTestCase


class TestInactive(ModBuilderTestCase):
    """Test parsing of trees involving disabled operands"""

    def setUp(self):
        ModBuilderTestCase.setUp(self)
        self.stub = self.ef.make(-1, operandID=Operand.defInt, expressionValue='1')

    def testAttack(self):
        disabledPre = self.ef.make(1, operandID=Operand.attack)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testCargoScan(self):
        disabledPre = self.ef.make(1, operandID=Operand.cargoScan)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testCheatTeleDock(self):
        disabledPre = self.ef.make(1, operandID=Operand.cheatTeleDock)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testCheatTeleGate(self):
        disabledPre = self.ef.make(1, operandID=Operand.cheatTeleGate)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testAoeDecloak(self):
        disabledPre = self.ef.make(1, operandID=Operand.aoeDecloak)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testEcmBurst(self):
        disabledPre = self.ef.make(1, operandID=Operand.ecmBurst)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testAoeDmg(self):
        disabledPre = self.ef.make(1, operandID=Operand.aoeDmg)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testMissileLaunch(self):
        disabledPre = self.ef.make(1, operandID=Operand.missileLaunch)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testDefenderLaunch(self):
        disabledPre = self.ef.make(1, operandID=Operand.defenderLaunch)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testFofLaunch(self):
        disabledPre = self.ef.make(1, operandID=Operand.fofLaunch)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testMine(self):
        disabledPre = self.ef.make(1, operandID=Operand.mine)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testPowerBooster(self):
        disabledPre = self.ef.make(1, operandID=Operand.powerBooster)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testShipScan(self):
        disabledPre = self.ef.make(1, operandID=Operand.shipScan)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testSurveyScan(self):
        disabledPre = self.ef.make(1, operandID=Operand.surveyScan)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testTgtHostile(self):
        disabledPre = self.ef.make(1, operandID=Operand.tgtHostile)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testTgtSilent(self):
        disabledPre = self.ef.make(1, operandID=Operand.tgtSilent)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testToolTgtSkills(self):
        disabledPre = self.ef.make(1, operandID=Operand.toolTgtSkills)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testUserError(self):
        disabledPre = self.ef.make(1, operandID=Operand.userError)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)

    def testVrfTgtGrp(self):
        disabledPre = self.ef.make(1, operandID=Operand.vrfTgtGrp)
        modifiers, status = self.runBuilder(disabledPre['expressionID'], self.stub['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 0)
