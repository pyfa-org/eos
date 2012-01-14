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

from eos import const
from eos.data import Expression
from eos.data.effect import InfoBuilder

class TestInactive(TestCase):
    """Test parsing of trees involving disabled operands"""

    def testAttack(self):
        disabledPre = Expression(1, 13)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testCargoScan(self):
        disabledPre = Expression(1, 14)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testCheatTeleDock(self):
        disabledPre = Expression(1, 15)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testCheatTeleGate(self):
        disabledPre = Expression(1, 16)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testAoeDecloak(self):
        disabledPre = Expression(1, 19)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEcmBurst(self):
        disabledPre = Expression(1, 30)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testAoeDmg(self):
        disabledPre = Expression(1, 32)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testMissileLaunch(self):
        disabledPre = Expression(1, 44)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testDefenderLaunch(self):
        disabledPre = Expression(1, 45)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testFofLaunch(self):
        disabledPre = Expression(1, 47)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testMine(self):
        disabledPre = Expression(1, 50)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testPowerBooster(self):
        disabledPre = Expression(1, 53)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testShipScan(self):
        disabledPre = Expression(1, 66)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testSurveyScan(self):
        disabledPre = Expression(1, 69)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testTgtHostile(self):
        disabledPre = Expression(1, 70)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testTgtSilent(self):
        disabledPre = Expression(1, 71)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testToolTgtSkills(self):
        disabledPre = Expression(1, 72)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testUserError(self):
        disabledPre = Expression(1, 73)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testVrfTgtGrp(self):
        disabledPre = Expression(1, 74)
        stubPost = Expression(2, 27, value="1")
        infos, status = InfoBuilder().build(disabledPre, stubPost)
        expStatus = const.effectInfoOkPartial
        self.assertEqual(status, expStatus, msg="expressions must be partially parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")
