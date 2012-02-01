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


from unittest import TestCase

from eos.const import EffectBuildStatus
from eos.eve.expression import Expression
from eos.fit.calc.info.builder.infoBuilder import InfoBuilder


class TestInactive(TestCase):
    """Test parsing of trees involving disabled operands"""

    def testAttack(self):
        disabledPre = Expression(None, 13)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testCargoScan(self):
        disabledPre = Expression(None, 14)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testCheatTeleDock(self):
        disabledPre = Expression(None, 15)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testCheatTeleGate(self):
        disabledPre = Expression(None, 16)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testAoeDecloak(self):
        disabledPre = Expression(None, 19)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEcmBurst(self):
        disabledPre = Expression(None, 30)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testAoeDmg(self):
        disabledPre = Expression(None, 32)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testMissileLaunch(self):
        disabledPre = Expression(None, 44)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testDefenderLaunch(self):
        disabledPre = Expression(None, 45)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testFofLaunch(self):
        disabledPre = Expression(None, 47)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testMine(self):
        disabledPre = Expression(None, 50)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testPowerBooster(self):
        disabledPre = Expression(None, 53)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testShipScan(self):
        disabledPre = Expression(None, 66)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testSurveyScan(self):
        disabledPre = Expression(None, 69)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testTgtHostile(self):
        disabledPre = Expression(None, 70)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testTgtSilent(self):
        disabledPre = Expression(None, 71)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testToolTgtSkills(self):
        disabledPre = Expression(None, 72)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testUserError(self):
        disabledPre = Expression(None, 73)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testVrfTgtGrp(self):
        disabledPre = Expression(None, 74)
        stubPost = Expression(None, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost, 0)
        expStatus = EffectBuildStatus.okPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")
