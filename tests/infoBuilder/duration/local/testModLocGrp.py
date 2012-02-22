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
from eos.tests.infoBuilder.environment import Eos
from eos.tests.eosTestCase import EosTestCase


class TestModLocGrp(EosTestCase):
    """Test parsing of trees describing modification filtered by location and group"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgtLoc = Expression(None, 24, value="Ship")
        eTgtGrp = Expression(None, 26, expressionGroupId=46)
        eTgtAttr = Expression(None, 22, expressionAttributeId=6)
        eOptr = Expression(None, 21, value="PostPercent")
        eSrcAttr = Expression(None, 22, expressionAttributeId=1576)
        eTgtItms = Expression(None, 48, arg1=eTgtLoc, arg2=eTgtGrp)
        eTgtSpec = Expression(None, 12, arg1=eTgtItms, arg2=eTgtAttr)
        eOptrTgt = Expression(None, 31, arg1=eOptr, arg2=eTgtSpec)
        self.eAddMod = Expression(1, 7, arg1=eOptrTgt, arg2=eSrcAttr)
        self.eRmMod = Expression(2, 59, arg1=eOptrTgt, arg2=eSrcAttr)

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        eos = Eos({self.eAddMod.id: self.eAddMod, self.eRmMod.id: self.eRmMod})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.runTime, RunTime.duration)
        self.assertEqual(info.context, Context.local)
        self.assertEqual(info.location, Location.ship)
        self.assertEqual(info.filterType, FilterType.group)
        self.assertEqual(info.filterValue, 46)
        self.assertEqual(info.operator, Operator.postPercent)
        self.assertEqual(info.targetAttributeId, 6)
        self.assertEqual(info.sourceType, SourceType.attribute)
        self.assertEqual(info.sourceValue, 1576)
        self.assertIsNone(info.conditions)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        eos = Eos({self.eAddMod.id: self.eAddMod, self.eRmMod.id: self.eRmMod})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        eos = Eos({self.eAddMod.id: self.eAddMod, self.eRmMod.id: self.eRmMod})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        eos = Eos({self.eAddMod.id: self.eAddMod, self.eRmMod.id: self.eRmMod})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.active)
        self.assertEqual(info.context, Context.projected)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        eos = Eos({self.eAddMod.id: self.eAddMod, self.eRmMod.id: self.eRmMod})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        eos = Eos({self.eAddMod.id: self.eAddMod, self.eRmMod.id: self.eRmMod})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.online)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        eos = Eos({self.eAddMod.id: self.eAddMod, self.eRmMod.id: self.eRmMod})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.overload)
        self.assertEqual(info.context, Context.local)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        eos = Eos({self.eAddMod.id: self.eAddMod, self.eRmMod.id: self.eRmMod})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(infos), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        eos = Eos({self.eAddMod.id: self.eAddMod, self.eRmMod.id: self.eRmMod})
        infos, status = InfoBuilder().build(effect, eos)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(infos), 1)
        info = infos[0]
        self.assertEqual(info.state, State.offline)
        self.assertEqual(info.context, Context.local)
