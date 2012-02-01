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

from eos.const import State, Location, EffectBuildStatus, Context, RunTime, FilterType, Operator, SourceType
from eos.eve.expression import Expression
from eos.fit.calc.info.builder.infoBuilder import InfoBuilder


class TestModLocGrp(TestCase):
    """Test parsing of trees describing modification filtered by location and group"""

    def setUp(self):
        eTgtLoc = Expression(None, 24, value="Ship")
        eTgtGrp = Expression(None, 26, expressionGroupId=46)
        eTgtAttr = Expression(None, 22, expressionAttributeId=6)
        eOptr = Expression(None, 21, value="PostPercent")
        eSrcAttr = Expression(None, 22, expressionAttributeId=1576)
        eTgtItms = Expression(None, 48, arg1=eTgtLoc, arg2=eTgtGrp)
        eTgtSpec = Expression(None, 12, arg1=eTgtItms, arg2=eTgtAttr)
        eOptrTgt = Expression(None, 31, arg1=eOptr, arg2=eTgtSpec)
        self.eAddMod = Expression(None, 7, arg1=eOptrTgt, arg2=eSrcAttr)
        self.eRmMod = Expression(None, 59, arg1=eOptrTgt, arg2=eSrcAttr)

    def testGenericBuildSuccess(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = RunTime.duration
        self.assertEqual(info.runTime, expType, msg="info type must be duration (ID {})".format(expType))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
        expLocation = Location.ship
        self.assertEqual(info.location, expLocation, msg="info target location must be ship (ID {})".format(expLocation))
        expFilterType = FilterType.group
        self.assertEqual(info.filterType, expFilterType, msg="info target filter type must be group (ID {})".format(expFilterType))
        expFilterValue = 46
        self.assertEqual(info.filterValue, expFilterValue, msg="info target filter value must be {}".format(expFilterValue))
        expOperation = Operator.postPercent
        self.assertEqual(info.operator, expOperation, msg="info operator must be PostPercent (ID {})".format(expOperation))
        expTgtAttr = 6
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = SourceType.attribute
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be attribute (ID {})".format(expSrcType))
        expSrcVal = 1576
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")

    def testEffCategoryPassive(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be passive (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryActive(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 1)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryTarget(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 2)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = Context.projected
        self.assertEqual(info.context, expContext, msg="info context must be projected (ID {})".format(expContext))

    def testEffCategoryArea(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 3)
        expStatus = EffectBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategoryOnline(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 4)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.online
        self.assertEqual(info.state, expState, msg="info state must be online (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryOverload(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 5)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.overload
        self.assertEqual(info.state, expState, msg="info state must be overload (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryDungeon(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 6)
        expStatus = EffectBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategorySystem(self):
        infos, status = InfoBuilder().build(self.eAddMod, self.eRmMod, 7)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be offline (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
