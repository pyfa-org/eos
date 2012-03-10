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
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase
from eos.tests.infoBuilder.environment import callize


class TestModAssignPreAttr(EosTestCase):
    """Test parsing of trees describing assignments by attribute applied in the beginning of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        # Manually composed example, CCP doesn't use such combination
        eTgt = Expression(None, 24, value="Char")
        eTgtAttr = Expression(None, 22, expressionAttributeId=166)
        eSrcAttr = Expression(None, 22, expressionAttributeId=177)
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreAssign = Expression(1, 65, arg1=eTgtSpec, arg2=eSrcAttr)
        self.ePostStub = Expression(2, 27, value="1")

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.runTime, RunTime.pre)
        self.assertEqual(info.context, Context.local)
        self.assertEqual(info.location, Location.character)
        self.assertIsNone(info.filterType)
        self.assertIsNone(info.filterValue)
        self.assertEqual(info.operator, Operator.assignment)
        self.assertEqual(info.targetAttributeId, 166)
        self.assertEqual(info.sourceType, SourceType.attribute)
        self.assertEqual(info.sourceValue, 177)
        self.assertIsNone(info.conditions)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.projected)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.online)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.overload)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)


class TestModAssignPreVal(EosTestCase):
    """Test parsing of trees describing assignments by value applied in the beginning of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgt = Expression(None, 24, value="Self")
        eTgtAttr = Expression(None, 22, expressionAttributeId=2)
        eSrcVal = Expression(None, 27, value="1")
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreAssign = Expression(1, 65, arg1=eTgtSpec, arg2=eSrcVal)
        self.ePostStub = Expression(2, 27, value="1")

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.runTime, RunTime.pre)
        self.assertEqual(info.context, Context.local)
        self.assertEqual(info.location, Location.self_)
        self.assertIsNone(info.filterType)
        self.assertIsNone(info.filterValue)
        self.assertEqual(info.operator, Operator.assignment)
        self.assertEqual(info.targetAttributeId, 2)
        self.assertEqual(info.sourceType, SourceType.value)
        self.assertEqual(info.sourceValue, 1)
        self.assertIsNone(info.conditions)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.projected)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.online)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.overload)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpressionCallData=callize(self.ePreAssign), postExpressionCallData=callize(self.ePostStub))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)


class TestModAssignPostAttr(EosTestCase):
    """Test parsing of trees describing assignments by attribute applied in the end of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        # Manually composed example, CCP doesn't use such combination
        eTgt = Expression(None, 24, value="Char")
        eTgtAttr = Expression(None, 22, expressionAttributeId=166)
        eSrcAttr = Expression(None, 22, expressionAttributeId=177)
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreStub = Expression(1, 27, value="1")
        self.ePostAssign = Expression(2, 65, arg1=eTgtSpec, arg2=eSrcAttr)

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.runTime, RunTime.post)
        self.assertEqual(info.context, Context.local)
        self.assertEqual(info.location, Location.character)
        self.assertIsNone(info.filterType)
        self.assertIsNone(info.filterValue)
        self.assertEqual(info.operator, Operator.assignment)
        self.assertEqual(info.targetAttributeId, 166)
        self.assertEqual(info.sourceType, SourceType.attribute)
        self.assertEqual(info.sourceValue, 177)
        self.assertIsNone(info.conditions)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.projected)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.online)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.overload)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)


class TestModAssignPostVal(EosTestCase):
    """Test parsing of trees describing assignments by value applied in the end of the cycle"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgt = Expression(None, 24, value="Self")
        eTgtAttr = Expression(None, 22, expressionAttributeId=2)
        eSrcVal = Expression(None, 27, value="0")
        eTgtSpec = Expression(None, 12, arg1=eTgt, arg2=eTgtAttr)
        self.ePreStub = Expression(1, 27, value="1")
        self.ePostAssign = Expression(2, 65, arg1=eTgtSpec, arg2=eSrcVal)

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.runTime, RunTime.post)
        self.assertEqual(info.context, Context.local)
        self.assertEqual(info.location, Location.self_)
        self.assertIsNone(info.filterType)
        self.assertIsNone(info.filterValue)
        self.assertEqual(info.operator, Operator.assignment)
        self.assertEqual(info.targetAttributeId, 2)
        self.assertEqual(info.sourceType, SourceType.value)
        self.assertEqual(info.sourceValue, 0)
        self.assertIsNone(info.conditions)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.projected)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.online)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.overload)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpressionCallData=callize(self.ePreStub), postExpressionCallData=callize(self.ePostAssign))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)
