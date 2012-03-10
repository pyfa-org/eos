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


from eos.const import State, Location, EffectBuildStatus, Context, RunTime, FilterType, Operator, SourceType
from eos.eve.effect import Effect
from eos.eve.expression import Expression
from eos.fit.attributeCalculator.info.infoBuilder import InfoBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase
from eos.tests.infoBuilder.environment import callize


class TestModGangOwnSrq(EosTestCase):
    """Test parsing of trees describing gang-mates' in-space items modification filtered by skill requirement"""

    def setUp(self):
        EosTestCase.setUp(self)
        # Manually composed example, as CCP doesn't use this modification type in any effect
        eTgtSrq = Expression(None, 29, expressionTypeId=3326)
        eTgtAttr = Expression(None, 22, expressionAttributeId=654)
        eOptr = Expression(None, 21, value="PostMul")
        eSrcAttr = Expression(None, 22, expressionAttributeId=848)
        eTgtSpec = Expression(None, 64, arg1=eTgtSrq, arg2=eTgtAttr)
        eOptrTgt = Expression(None, 31, arg1=eOptr, arg2=eTgtSpec)
        self.eAddMod = Expression(1, 4, arg1=eOptrTgt, arg2=eSrcAttr)
        self.eRmMod = Expression(2, 56, arg1=eOptrTgt, arg2=eSrcAttr)

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpressionData=callize(self.eAddMod), postExpressionData=callize(self.eRmMod))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.runTime, RunTime.duration)
        self.assertEqual(info.context, Context.gang)
        self.assertEqual(info.location, Location.space)
        self.assertEqual(info.filterType, FilterType.skill)
        self.assertEqual(info.filterValue, 3326)
        self.assertEqual(info.operator, Operator.postMul)
        self.assertEqual(info.targetAttributeId, 654)
        self.assertEqual(info.sourceType, SourceType.attribute)
        self.assertEqual(info.sourceValue, 848)
        self.assertIsNone(info.conditions)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpressionData=callize(self.eAddMod), postExpressionData=callize(self.eRmMod))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.gang)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpressionData=callize(self.eAddMod), postExpressionData=callize(self.eRmMod))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.gang)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpressionData=callize(self.eAddMod), postExpressionData=callize(self.eRmMod))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpressionData=callize(self.eAddMod), postExpressionData=callize(self.eRmMod))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpressionData=callize(self.eAddMod), postExpressionData=callize(self.eRmMod))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.online)
        self.assertEqual(info.context, Context.gang)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpressionData=callize(self.eAddMod), postExpressionData=callize(self.eRmMod))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.overload)
        self.assertEqual(info.context, Context.gang)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpressionData=callize(self.eAddMod), postExpressionData=callize(self.eRmMod))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpressionData=callize(self.eAddMod), postExpressionData=callize(self.eRmMod))
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.gang)
