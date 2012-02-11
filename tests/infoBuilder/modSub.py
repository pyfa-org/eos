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


from eos.const import State, Location, EffectBuildStatus, Context, RunTime, Operator, SourceType
from eos.eve.expression import Expression
from eos.fit.attributeCalculator.info.infoBuilder import InfoBuilder
from eos.tests.eosTestCase import EosTestCase


class TestModSubPreAttr(EosTestCase):
    """Test parsing of trees describing decrement by attribute in the beginning of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgt = Expression(None, 24, value="Target")
        eTgtAttr = Expression(None, 22, expressionAttributeId=18)
        eSrcAttr = Expression(None, 22, expressionAttributeId=97)
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreSub = Expression(None, 18, arg1=eTgtSpec, arg2=eSrcAttr)
        self.ePostStub = Expression(None, 27, value="1")

    def testGenericBuildSuccess(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = RunTime.pre
        self.assertEqual(info.runTime, expType, msg="info type must be instant pre-modifier (ID {})".format(expType))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
        expLocation = Location.target
        self.assertEqual(info.location, expLocation, msg="info target location must be target (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = Operator.decrement
        self.assertEqual(info.operator, expOperation, msg="info operator must be Decreement (ID {})".format(expOperation))
        expTgtAttr = 18
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = SourceType.attribute
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be attribute (ID {})".format(expSrcType))
        expSrcVal = 97
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")

    def testEffCategoryPassive(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be passive (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryActive(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 1)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryTarget(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 2)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = Context.projected
        self.assertEqual(info.context, expContext, msg="info context must be projected (ID {})".format(expContext))

    def testEffCategoryArea(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 3)
        expStatus = EffectBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategoryOnline(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 4)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.online
        self.assertEqual(info.state, expState, msg="info state must be online (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryOverload(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 5)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.overload
        self.assertEqual(info.state, expState, msg="info state must be overload (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryDungeon(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 6)
        expStatus = EffectBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategorySystem(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 7)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be offline (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))


class TestModSubPreVal(EosTestCase):
    """Test parsing of trees describing decrement by value in the beginning of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgt = Expression(None, 24, value="Target")
        eTgtAttr = Expression(None, 22, expressionAttributeId=18)
        eSrcVal = Expression(None, 27, value="7")
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreSub = Expression(None, 18, arg1=eTgtSpec, arg2=eSrcVal)
        self.ePostStub = Expression(None, 27, value="1")

    def testGenericBuildSuccess(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = RunTime.pre
        self.assertEqual(info.runTime, expType, msg="info type must be instant pre-modifier (ID {})".format(expType))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
        expLocation = Location.target
        self.assertEqual(info.location, expLocation, msg="info target location must be target (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = Operator.decrement
        self.assertEqual(info.operator, expOperation, msg="info operator must be Decrement (ID {})".format(expOperation))
        expTgtAttr = 18
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = SourceType.value
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be value (ID {})".format(expSrcType))
        expSrcVal = 7
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")

    def testEffCategoryPassive(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be passive (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryActive(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 1)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryTarget(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 2)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = Context.projected
        self.assertEqual(info.context, expContext, msg="info context must be projected (ID {})".format(expContext))

    def testEffCategoryArea(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 3)
        expStatus = EffectBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategoryOnline(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 4)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.online
        self.assertEqual(info.state, expState, msg="info state must be online (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryOverload(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 5)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.overload
        self.assertEqual(info.state, expState, msg="info state must be overload (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryDungeon(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 6)
        expStatus = EffectBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategorySystem(self):
        infos, status = InfoBuilder().build(self.ePreSub, self.ePostStub, 7)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be offline (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))


class TestModSubPostAttr(EosTestCase):
    """Test parsing of trees describing decrement by attribute in the end of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgt = Expression(None, 24, value="Target")
        eTgtAttr = Expression(None, 22, expressionAttributeId=266)
        eSrcAttr = Expression(None, 22, expressionAttributeId=84)
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreStub = Expression(None, 27, value="1")
        self.ePostSub = Expression(None, 18, arg1=eTgtSpec, arg2=eSrcAttr)

    def testGenericBuildSuccess(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = RunTime.post
        self.assertEqual(info.runTime, expType, msg="info type must be instant post-modifier (ID {})".format(expType))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
        expLocation = Location.target
        self.assertEqual(info.location, expLocation, msg="info target location must be target (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = Operator.decrement
        self.assertEqual(info.operator, expOperation, msg="info operator must be Decreement (ID {})".format(expOperation))
        expTgtAttr = 266
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = SourceType.attribute
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be attribute (ID {})".format(expSrcType))
        expSrcVal = 84
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")

    def testEffCategoryPassive(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be passive (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryActive(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 1)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryTarget(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 2)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = Context.projected
        self.assertEqual(info.context, expContext, msg="info context must be projected (ID {})".format(expContext))

    def testEffCategoryArea(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 3)
        expStatus = EffectBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategoryOnline(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 4)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.online
        self.assertEqual(info.state, expState, msg="info state must be online (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryOverload(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 5)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.overload
        self.assertEqual(info.state, expState, msg="info state must be overload (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryDungeon(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 6)
        expStatus = EffectBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategorySystem(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 7)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be offline (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))


class TestModSubPostVal(EosTestCase):
    """Test parsing of trees describing decrement by value in the end of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgt = Expression(None, 24, value="Target")
        eTgtAttr = Expression(None, 22, expressionAttributeId=266)
        eSrcVal = Expression(None, 27, value="1")
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreStub = Expression(None, 27, value="1")
        self.ePostSub = Expression(None, 18, arg1=eTgtSpec, arg2=eSrcVal)

    def testGenericBuildSuccess(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expType = RunTime.post
        self.assertEqual(info.runTime, expType, msg="info type must be instant post-modifier (ID {})".format(expType))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
        expLocation = Location.target
        self.assertEqual(info.location, expLocation, msg="info target location must be target (ID {})".format(expLocation))
        self.assertIsNone(info.filterType, msg="info target filter type must be None")
        self.assertIsNone(info.filterValue, msg="info target filter value must be None")
        expOperation = Operator.decrement
        self.assertEqual(info.operator, expOperation, msg="info operator must be Decrement (ID {})".format(expOperation))
        expTgtAttr = 266
        self.assertEqual(info.targetAttributeId, expTgtAttr, msg="info target attribute ID must be {}".format(expTgtAttr))
        expSrcType = SourceType.value
        self.assertEqual(info.sourceType, expSrcType, msg="info source type must be value (ID {})".format(expSrcType))
        expSrcVal = 1
        self.assertEqual(info.sourceValue, expSrcVal, msg="info source value must be {}".format(expSrcVal))
        self.assertIsNone(info.conditions, msg="info conditions must be None")

    def testEffCategoryPassive(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 0)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be passive (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryActive(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 1)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryTarget(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 2)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.active
        self.assertEqual(info.state, expState, msg="info state must be active (ID {})".format(expState))
        expContext = Context.projected
        self.assertEqual(info.context, expContext, msg="info context must be projected (ID {})".format(expContext))

    def testEffCategoryArea(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 3)
        expStatus = EffectBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategoryOnline(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 4)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.online
        self.assertEqual(info.state, expState, msg="info state must be online (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryOverload(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 5)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.overload
        self.assertEqual(info.state, expState, msg="info state must be overload (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))

    def testEffCategoryDungeon(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 6)
        expStatus = EffectBuildStatus.error
        self.assertEqual(status, expStatus, msg="expressions must be erroneously parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 0, msg="no infos must be generated")

    def testEffCategorySystem(self):
        infos, status = InfoBuilder().build(self.ePreStub, self.ePostSub, 7)
        expStatus = EffectBuildStatus.okFull
        self.assertEqual(status, expStatus, msg="expressions must be successfully parsed (ID {})".format(expStatus))
        self.assertEqual(len(infos), 1, msg="one info must be generated")
        info = infos.pop()
        expState = State.offline
        self.assertEqual(info.state, expState, msg="info state must be offline (ID {})".format(expState))
        expContext = Context.local
        self.assertEqual(info.context, expContext, msg="info context must be local (ID {})".format(expContext))
