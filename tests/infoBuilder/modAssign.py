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
from eos.fit.aux.location import Location
from eos.fit.aux.state import State
from eos.fit.calc.info.builder.infoBuilder import InfoBuilder, InfoBuildStatus
from eos.fit.calc.info.info import InfoContext, InfoRunTime, InfoOperator, InfoSourceType


class TestModAssignPreAttr(TestCase):
    """Test parsing of trees describing assignments by attribute applied in the beginning of the cycle"""

    def setUp(self):
        # Manually composed example, CCP doesn't use such combination
        eTgt = Expression(24, value="Char")
        eTgtAttr = Expression(22, expressionAttributeId=166)
        eSrcAttr = Expression(22, expressionAttributeId=177)
        eTgtSpec = Expression(12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreAssign = Expression(65, arg1=eTgtSpec, arg2=eSrcAttr)
        self.ePostStub = Expression(27, value="1")

    def testGenericBuildSuccess(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 0)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = InfoRunTime.pre
        self.assertEqual(info.runTime, expType, msg="info type must be instant pre-modifier (ID {})".format(expType))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
        expLocation = Location.character
        self.assertEqual(info.location, expLocation, msg="info target location must be char (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = InfoOperator.assignment
        self.assertEqual(info.operator, expOperation, msg="info operator must be Assign (ID {})".format(expOperation))
        expTgtAttr = 166
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = InfoSourceType.attribute
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be attribute (ID {})".format(expSrcType))
        expSrcVal = 177
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")

    def testEffCategoryPassive(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 0)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be passive (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryActive(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 1)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryTarget(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 2)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = InfoContext.projected
        self.assertEqual(info.context, expContext, msg="info context must be projected (ID {})".format(expContext))

    def testEffCategoryArea(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 3)
        expStatus = InfoBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategoryOnline(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 4)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.online
        self.assertEqual(info.state, expState, msg="info state must be online (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryOverload(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 5)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.overload
        self.assertEqual(info.state, expState, msg="info state must be overload (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryDungeon(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 6)
        expStatus = InfoBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategorySystem(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 7)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be offline (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))


class TestModAssignPreVal(TestCase):
    """Test parsing of trees describing assignments by value applied in the beginning of the cycle"""

    def setUp(self):
        eTgt = Expression(24, value="Self")
        eTgtAttr = Expression(22, expressionAttributeId=2)
        eSrcVal = Expression(27, value="1")
        eTgtSpec = Expression(12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreAssign = Expression(65, arg1=eTgtSpec, arg2=eSrcVal)
        self.ePostStub = Expression(27, value="1")

    def testGenericBuildSuccess(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 0)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = InfoRunTime.pre
        self.assertEqual(info.runTime, expType, msg="info type must be instant pre-modifier (ID {})".format(expType))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
        expLocation = Location.self_
        self.assertEqual(info.location, expLocation, msg="info target location must be self (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = InfoOperator.assignment
        self.assertEqual(info.operator, expOperation, msg="info operator must be Assign (ID {})".format(expOperation))
        expTgtAttr = 2
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = InfoSourceType.value
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be value (ID {})".format(expSrcType))
        expSrcVal = 1
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")

    def testEffCategoryPassive(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 0)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be passive (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryActive(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 1)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryTarget(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 2)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = InfoContext.projected
        self.assertEqual(info.context, expContext, msg="info context must be projected (ID {})".format(expContext))

    def testEffCategoryArea(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 3)
        expStatus = InfoBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategoryOnline(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 4)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.online
        self.assertEqual(info.state, expState, msg="info state must be online (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryOverload(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 5)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.overload
        self.assertEqual(info.state, expState, msg="info state must be overload (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryDungeon(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 6)
        expStatus = InfoBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategorySystem(self):
        infos, status = InfoBuilder().build(self.ePreAssign, self.ePostStub, 7)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be offline (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))


class TestModAssignPostAttr(TestCase):
    """Test parsing of trees describing assignments by attribute applied in the end of the cycle"""

    def setUp(self):
        # Manually composed example, CCP doesn't use such combination
        eTgt = Expression(24, value="Char")
        eTgtAttr = Expression(22, expressionAttributeId=166)
        eSrcAttr = Expression(22, expressionAttributeId=177)
        eTgtSpec = Expression(12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreStub = Expression(27, value="1")
        self.ePostAssign = Expression(65, arg1=eTgtSpec, arg2=eSrcAttr)

    def testGenericBuildSuccess(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 0)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = InfoRunTime.post
        self.assertEqual(info.runTime, expType, msg="info type must be instant post-modifier (ID {})".format(expType))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
        expLocation = Location.character
        self.assertEqual(info.location, expLocation, msg="info target location must be char (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = InfoOperator.assignment
        self.assertEqual(info.operator, expOperation, msg="info operator must be Assign (ID {})".format(expOperation))
        expTgtAttr = 166
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = InfoSourceType.attribute
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be attribute (ID {})".format(expSrcType))
        expSrcVal = 177
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")

    def testEffCategoryPassive(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 0)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be passive (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryActive(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 1)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryTarget(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 2)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = InfoContext.projected
        self.assertEqual(info.context, expContext, msg="info context must be projected (ID {})".format(expContext))

    def testEffCategoryArea(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 3)
        expStatus = InfoBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategoryOnline(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 4)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.online
        self.assertEqual(info.state, expState, msg="info state must be online (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryOverload(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 5)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.overload
        self.assertEqual(info.state, expState, msg="info state must be overload (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryDungeon(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 6)
        expStatus = InfoBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategorySystem(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 7)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be offline (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))


class TestModAssignPostVal(TestCase):
    """Test parsing of trees describing assignments by value applied in the end of the cycle"""

    def setUp(self):
        eTgt = Expression(24, value="Self")
        eTgtAttr = Expression(22, expressionAttributeId=2)
        eSrcVal = Expression(27, value="0")
        eTgtSpec = Expression(12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreStub = Expression(27, value="1")
        self.ePostAssign = Expression(65, arg1=eTgtSpec, arg2=eSrcVal)

    def testGenericBuildSuccess(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 0)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = InfoRunTime.post
        self.assertEqual(info.runTime, expType, msg="info type must be instant post-modifier (ID {})".format(expType))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
        expLocation = Location.self_
        self.assertEqual(info.location, expLocation, msg="info target location must be self (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = InfoOperator.assignment
        self.assertEqual(info.operator, expOperation, msg="info operator must be Assign (ID {})".format(expOperation))
        expTgtAttr = 2
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = InfoSourceType.value
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be value (ID {})".format(expSrcType))
        expSrcVal = 0
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")

    def testEffCategoryPassive(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 0)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be passive (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryActive(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 1)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryTarget(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 2)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = InfoContext.projected
        self.assertEqual(info.context, expContext, msg="info context must be projected (ID {})".format(expContext))

    def testEffCategoryArea(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 3)
        expStatus = InfoBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategoryOnline(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 4)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.online
        self.assertEqual(info.state, expState, msg="info state must be online (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryOverload(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 5)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.overload
        self.assertEqual(info.state, expState, msg="info state must be overload (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryDungeon(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 6)
        expStatus = InfoBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategorySystem(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostAssign, 7)
        expStatus = InfoBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be offline (ID {})".format(expState))
        expContext = InfoContext.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
