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
from eos.eve.effect import Effect
from eos.eve.expression import Expression
from eos.fit.attributeCalculator.info.infoBuilder import InfoBuilder
from eos.tests.infoBuilder.environment import Logger
from eos.tests.eosTestCase import EosTestCase


class TestModAddPreAttr(EosTestCase):
    """Test parsing of trees describing increment by attribute in the beginning of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgt = Expression(None, 24, value="Ship")
        eTgtAttr = Expression(None, 22, expressionAttributeId=264)
        eSrcAttr = Expression(None, 22, expressionAttributeId=68)
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreAdd = Expression(None, 42, arg1=eTgtSpec, arg2=eSrcAttr)
        self.ePostStub = Expression(None, 27, value="1")

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.runTime, RunTime.pre)
        self.assertEqual(info.context, Context.local)
        self.assertEqual(info.location, Location.ship)
        self.assertIsNone(info.filterType)
        self.assertIsNone(info.filterValue)
        self.assertEqual(info.operator, Operator.increment)
        self.assertEqual(info.targetAttributeId, 264)
        self.assertEqual(info.sourceType, SourceType.attribute)
        self.assertEqual(info.sourceValue, 68)
        self.assertIsNone(info.conditions)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.projected)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.online)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.overload)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)


class TestModAddPreVal(EosTestCase):
    """Test parsing of trees describing increment by value in the beginning of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgt = Expression(None, 24, value="Ship")
        eTgtAttr = Expression(None, 22, expressionAttributeId=264)
        eSrcVal = Expression(None, 27, value="200")
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreAdd = Expression(None, 42, arg1=eTgtSpec, arg2=eSrcVal)
        self.ePostStub = Expression(None, 27, value="1")

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.runTime, RunTime.pre)
        self.assertEqual(info.context, Context.local)
        self.assertEqual(info.location, Location.ship)
        self.assertIsNone(info.filterType)
        self.assertIsNone(info.filterValue)
        self.assertEqual(info.operator, Operator.increment)
        self.assertEqual(info.targetAttributeId, 264)
        self.assertEqual(info.sourceType, SourceType.value)
        self.assertEqual(info.sourceValue, 200)
        self.assertIsNone(info.conditions)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.projected)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.online)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.overload)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpression=self.ePreAdd, postExpression=self.ePostStub)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)


class TestModAddPostAttr(EosTestCase):
    """Test parsing of trees describing increment by attribute in the end of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgt = Expression(None, 24, value="Ship")
        eTgtAttr = Expression(None, 22, expressionAttributeId=264)
        eSrcAttr = Expression(None, 22, expressionAttributeId=68)
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreStub = Expression(None, 27, value="1")
        self.ePostAdd = Expression(None, 42, arg1=eTgtSpec, arg2=eSrcAttr)

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.runTime, RunTime.post)
        self.assertEqual(info.context, Context.local)
        self.assertEqual(info.location, Location.ship)
        self.assertIsNone(info.filterType)
        self.assertIsNone(info.filterValue)
        self.assertEqual(info.operator, Operator.increment)
        self.assertEqual(info.targetAttributeId, 264)
        self.assertEqual(info.sourceType, SourceType.attribute)
        self.assertEqual(info.sourceValue, 68)
        self.assertIsNone(info.conditions)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.projected)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.online)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.overload)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)


class TestModAddPostVal(EosTestCase):
    """Test parsing of trees describing increment by value in the end of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgt = Expression(None, 24, value="Ship")
        eTgtAttr = Expression(None, 22, expressionAttributeId=264)
        eSrcVal = Expression(None, 27, value="3")
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreStub = Expression(None, 27, value="1")
        self.ePostAdd = Expression(None, 42, arg1=eTgtSpec, arg2=eSrcVal)

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.runTime, RunTime.post)
        self.assertEqual(info.context, Context.local)
        self.assertEqual(info.location, Location.ship)
        self.assertIsNone(info.filterType)
        self.assertIsNone(info.filterValue)
        self.assertEqual(info.operator, Operator.increment)
        self.assertEqual(info.targetAttributeId, 264)
        self.assertEqual(info.sourceType, SourceType.value)
        self.assertEqual(info.sourceValue, 3)
        self.assertIsNone(info.conditions)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.projected)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.online)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.overload)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpression=self.ePreStub, postExpression=self.ePostAdd)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)
