#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
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
from eos.tests.modifierBuilder.modBuilderTestCase import ModBuilderTestCase


class TestIncomplete(ModBuilderTestCase):
    """Test parsing of trees, which include actions, which are not converted into modifiers"""

    def setUp(self):
        ModBuilderTestCase.setUp(self)
        # Modifier, except for top-most expression, which
        # is added in test cases
        eTgt = self.ef.make(1, operandId=24, expressionValue='Ship')
        eTgtAttr = self.ef.make(2, operandId=22, expressionAttributeId=9)
        eOptr = self.ef.make(3, operandId=21, expressionValue='PostPercent')
        self.eSrcAttr = self.ef.make(4, operandId=22, expressionAttributeId=327)
        eTgtSpec = self.ef.make(5, operandId=12, arg1Id=eTgt['expressionId'], arg2Id=eTgtAttr['expressionId'])
        self.eOptrTgt = self.ef.make(6, operandId=31, arg1Id=eOptr['expressionId'], arg2Id=eTgtSpec['expressionId'])
        self.stub = self.ef.make(7, operandId=27, expressionValue='1')

    def testPre(self):
        eAddMod = self.ef.make(8, operandId=6, arg1Id=self.eOptrTgt['expressionId'], arg2Id=self.eSrcAttr['expressionId'])
        modifiers, status = self.runBuilder(eAddMod['expressionId'], self.stub['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)

    def testPost(self):
        eRmMod = self.ef.make(8, operandId=58, arg1Id=self.eOptrTgt['expressionId'], arg2Id=self.eSrcAttr['expressionId'])
        modifiers, status = self.runBuilder(self.stub['expressionId'], eRmMod['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
