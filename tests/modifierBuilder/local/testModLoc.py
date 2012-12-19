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


from eos.const import State, Location, EffectBuildStatus, Context, FilterType, Operator
from eos.fit.attributeCalculator.modifier.modifierBuilder import ModifierBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase


class TestModLoc(EosTestCase):
    """Test parsing of trees describing modification filtered by location"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgt = self.ch.expression(expressionId=1, operandId=24, value="Ship")
        eTgtAttr = self.ch.expression(expressionId=2, operandId=22, expressionAttributeId=1211)
        eOptr = self.ch.expression(expressionId=3, operandId=21, value="PostPercent")
        eSrcAttr = self.ch.expression(expressionId=4, operandId=22, expressionAttributeId=1503)
        eTgtSpec = self.ch.expression(expressionId=5, operandId=12, arg1Id=eTgt.id, arg2Id=eTgtAttr.id)
        eOptrTgt = self.ch.expression(expressionId=6, operandId=31, arg1Id=eOptr.id, arg2Id=eTgtSpec.id)
        self.eAddMod = self.ch.expression(expressionId=7, operandId=8, arg1Id=eOptrTgt.id, arg2Id=eSrcAttr.id)
        self.eRmMod = self.ch.expression(expressionId=8, operandId=60, arg1Id=eOptrTgt.id, arg2Id=eSrcAttr.id)

    def testGenericBuildSuccess(self):
        effect = self.ch.effect(categoryId=0, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.context, Context.local)
        self.assertEqual(modifier.sourceAttributeId, 1503)
        self.assertEqual(modifier.operator, Operator.postPercent)
        self.assertEqual(modifier.targetAttributeId, 1211)
        self.assertEqual(modifier.location, Location.ship)
        self.assertEqual(modifier.filterType, FilterType.all_)
        self.assertIsNone(modifier.filterValue)

    def testEffCategoryPassive(self):
        effect = self.ch.effect(categoryId=0, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.context, Context.local)

    def testEffCategoryActive(self):
        effect = self.ch.effect(categoryId=1, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.active)
        self.assertEqual(modifier.context, Context.local)

    def testEffCategoryTarget(self):
        effect = self.ch.effect(categoryId=2, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.active)
        self.assertEqual(modifier.context, Context.projected)

    def testEffCategoryArea(self):
        effect = self.ch.effect(categoryId=3, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)

    def testEffCategoryOnline(self):
        effect = self.ch.effect(categoryId=4, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.online)
        self.assertEqual(modifier.context, Context.local)

    def testEffCategoryOverload(self):
        effect = self.ch.effect(categoryId=5, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.overload)
        self.assertEqual(modifier.context, Context.local)

    def testEffCategoryDungeon(self):
        effect = self.ch.effect(categoryId=6, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)

    def testEffCategorySystem(self):
        effect = self.ch.effect(categoryId=7, preExpressionId=self.eAddMod.id, postExpressionId=self.eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.context, Context.local)
