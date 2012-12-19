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


from eos.const import EffectBuildStatus, FilterType, InvType
from eos.fit.attributeCalculator.modifier.modifierBuilder import ModifierBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase


class TestSelfType(EosTestCase):
    """Test parsing of trees describing modification which contains reference to typeID of its carrier"""

    def testBuildSuccess(self):
        eTgtOwn = self.ch.expression(expressionId=1, operandId=24, value="Char")
        eSelf = self.ch.expression(expressionId=2, operandId=24, value="Self")
        eSelfType = self.ch.expression(expressionId=3, operandId=36, arg1Id=eSelf.id)
        eTgtAttr = self.ch.expression(expressionId=4, operandId=22, expressionAttributeId=64)
        eOptr = self.ch.expression(expressionId=5, operandId=21, value="PostPercent")
        eSrcAttr = self.ch.expression(expressionId=6, operandId=22, expressionAttributeId=292)
        eTgtItms = self.ch.expression(expressionId=7, operandId=49, arg1Id=eTgtOwn.id, arg2Id=eSelfType.id)
        eTgtSpec = self.ch.expression(expressionId=8, operandId=12, arg1Id=eTgtItms.id, arg2Id=eTgtAttr.id)
        eOptrTgt = self.ch.expression(expressionId=9, operandId=31, arg1Id=eOptr.id, arg2Id=eTgtSpec.id)
        eAddMod = self.ch.expression(expressionId=10, operandId=11, arg1Id=eOptrTgt.id, arg2Id=eSrcAttr.id)
        eRmMod = self.ch.expression(expressionId=11, operandId=62, arg1Id=eOptrTgt.id, arg2Id=eSrcAttr.id)
        effect = self.ch.effect(categoryId=0, preExpressionId=eAddMod.id, postExpressionId=eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.filterType, FilterType.skill)
        self.assertEqual(modifier.filterValue, InvType.self_)
