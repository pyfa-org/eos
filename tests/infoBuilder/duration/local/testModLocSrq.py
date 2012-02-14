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


class TestModLocSrq(EosTestCase):
    """Test parsing of trees describing modification filtered by location and skill requirement"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgtLoc = Expression(None, 24, value="Ship")
        eTgtSrq = Expression(None, 29, expressionTypeId=3307)
        eTgtAttr = Expression(None, 22, expressionAttributeId=54)
        eOptr = Expression(None, 21, value="PostPercent")
        eSrcAttr = Expression(None, 22, expressionAttributeId=491)
        eTgtItms = Expression(None, 49, arg1=eTgtLoc, arg2=eTgtSrq)
        eTgtSpec = Expression(None, 12, arg1=eTgtItms, arg2=eTgtAttr)
        eOptrTgt = Expression(None, 31, arg1=eOptr, arg2=eTgtSpec)
        self.eAddMod = Expression(None, 9, arg1=eOptrTgt, arg2=eSrcAttr)
        self.eRmMod = Expression(None, 61, arg1=eOptrTgt, arg2=eSrcAttr)

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpression=self.eAddMod, postExpression=self.eRmMod)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos.pop()
        self.assertEqual(info.runTime, RunTime.duration)
        self.assertEqual(info.context, Context.local)
        self.assertEqual(info.location, Location.ship)
        self.assertEqual(info.filterType, FilterType.skill)
        self.assertEqual(info.filterValue, 3307)
        self.assertEqual(info.operator, Operator.postPercent)
        self.assertEqual(info.targetAttributeId, 54)
        self.assertEqual(info.sourceType, SourceType.attribute)
        self.assertEqual(info.sourceValue, 491)
        self.assertIsNone(info.conditions)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpression=self.eAddMod, postExpression=self.eRmMod)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos.pop()
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpression=self.eAddMod, postExpression=self.eRmMod)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos.pop()
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpression=self.eAddMod, postExpression=self.eRmMod)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos.pop()
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.projected)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpression=self.eAddMod, postExpression=self.eRmMod)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpression=self.eAddMod, postExpression=self.eRmMod)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos.pop()
        self.assertEqual(info.state, State.online)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpression=self.eAddMod, postExpression=self.eRmMod)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos.pop()
        self.assertEqual(info.state, State.overload)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpression=self.eAddMod, postExpression=self.eRmMod)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpression=self.eAddMod, postExpression=self.eRmMod)
        infos, status = InfoBuilder().build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos.pop()
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)
