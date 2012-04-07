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


from eos.const import EffectBuildStatus
from eos.fit.attributeCalculator.modifier.modifierBuilder import ModifierBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase


class TestIncomplete(EosTestCase):
    """Test parsing of trees, which include actions, which are not converted into modifiers"""

    def setUp(self):
        EosTestCase.setUp(self)
        # Modifier, except for top-most expression, which
        # is added in test cases
        eTgt = self.dh.expression(expressionId=1, operandId=24, value="Ship")
        eTgtAttr = self.dh.expression(expressionId=2, operandId=22, expressionAttributeId=9)
        eOptr = self.dh.expression(expressionId=3, operandId=21, value="PostPercent")
        self.eSrcAttr = self.dh.expression(expressionId=4, operandId=22, expressionAttributeId=327)
        eTgtSpec = self.dh.expression(expressionId=5, operandId=12, arg1Id=eTgt.id, arg2Id=eTgtAttr.id)
        self.eOptrTgt = self.dh.expression(expressionId=6, operandId=31, arg1Id=eOptr.id, arg2Id=eTgtSpec.id)
        self.stub = self.dh.expression(expressionId=7, operandId=27, value="1")

    def testPre(self):
        eAddMod = self.dh.expression(expressionId=8, operandId=6, arg1Id=self.eOptrTgt.id, arg2Id=self.eSrcAttr.id)
        effect = self.dh.effect(categoryId=0, preExpressionId=eAddMod.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testPost(self):
        eRmMod = self.dh.expression(expressionId=8, operandId=58, arg1Id=self.eOptrTgt.id, arg2Id=self.eSrcAttr.id)
        effect = self.dh.effect(categoryId=0, preExpressionId=self.stub.id, postExpressionId=eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
