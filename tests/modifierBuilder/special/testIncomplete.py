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
from eos.eve.effect import Effect
from eos.eve.expression import Expression
from eos.fit.attributeCalculator.modifier.modifierBuilder import ModifierBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase
from eos.tests.modifierBuilder.environment import DataHandler


class TestIncomplete(EosTestCase):
    """Test parsing of trees, which include actions, which are not converted into modifiers"""

    def setUp(self):
        EosTestCase.setUp(self)
        self.dh = DataHandler()
        # Modifier, except for top-most expression, which
        # is added in test cases
        eTgt = Expression(dataHandler=self.dh, expressionId=1, operandId=24, value="Ship")
        eTgtAttr = Expression(dataHandler=self.dh, expressionId=2, operandId=22, expressionAttributeId=9)
        eOptr = Expression(dataHandler=self.dh, expressionId=3, operandId=21, value="PostPercent")
        self.eSrcAttr = Expression(dataHandler=self.dh, expressionId=4, operandId=22, expressionAttributeId=327)
        eTgtSpec = Expression(dataHandler=self.dh, expressionId=5, operandId=12, arg1Id=eTgt.id, arg2Id=eTgtAttr.id)
        self.eOptrTgt = Expression(dataHandler=self.dh, expressionId=6, operandId=31, arg1Id=eOptr.id, arg2Id=eTgtSpec.id)
        self.stub = Expression(dataHandler=self.dh, expressionId=7, operandId=27, value="1")
        self.dh.addExpressions((eTgt, eTgtAttr, eOptr, self.eSrcAttr, eTgtSpec, self.eOptrTgt, self.stub))

    def testPre(self):
        eAddMod = Expression(dataHandler=self.dh, expressionId=8, operandId=6, arg1Id=self.eOptrTgt.id, arg2Id=self.eSrcAttr.id)
        self.dh.addExpressions((eAddMod,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=eAddMod.id, postExpressionId=self.stub.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)

    def testPost(self):
        eRmMod = Expression(dataHandler=self.dh, expressionId=8, operandId=58, arg1Id=self.eOptrTgt.id, arg2Id=self.eSrcAttr.id)
        self.dh.addExpressions((eRmMod,))
        effect = Effect(dataHandler=self.dh, categoryId=0, preExpressionId=self.stub.id, postExpressionId=eRmMod.id)
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
