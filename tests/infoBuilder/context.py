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

from eos.eve.expression import Expression
from eos.calc.info.builder.builder import InfoBuilder, InfoBuildStatus
from eos.calc.info.info import InfoContext

class TestContext(TestCase):
    """Test context conversion"""

    def setUp(self):
        # Some random modifier, which makes sense for builder
        eTgt = Expression(24, value="Ship")
        eTgtAttr = Expression(22, attributeId=15)
        eOptr = Expression(21, value="ModAdd")
        eSrcAttr = Expression(22, attributeId=30)
        eTgtSpec = Expression(12, arg1=eTgt, arg2=eTgtAttr)
        eOptrTgt = Expression(31, arg1=eOptr, arg2=eTgtSpec)
        self.eAddMod = Expression(6, arg1=eOptrTgt, arg2=eSrcAttr)
        self.eRmMod = Expression(58, arg1=eOptrTgt, arg2=eSrcAttr)

    def testPassive(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 0)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expContext = InfoContext.passive
        self.assertEqual(info.context, expContext, msg="info context must be passive (ID {})".format(expContext))

    def testActive(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 1)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expContext = InfoContext.active
        self.assertEqual(info.context, expContext, msg="info context must be active (ID {})".format(expContext))

    def testTarget(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 2)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expContext = InfoContext.projected
        self.assertEqual(info.context, expContext, msg="info context must be projected (ID {})".format(expContext))

    def testArea(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 3)
        expStatus = InfoBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testOnline(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 4)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expContext = InfoContext.online
        self.assertEqual(info.context, expContext, msg="info context must be online (ID {})".format(expContext))

    def testOverload(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 5)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expContext = InfoContext.overload
        self.assertEqual(info.context, expContext, msg="info context must be overload (ID {})".format(expContext))

    def testDungeon(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 6)
        expStatus = InfoBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testSystem(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 7)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expContext = InfoContext.projected
        self.assertEqual(info.context, expContext, msg="info context must be projected (ID {})".format(expContext))
