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
        eTgt = self.ef.make(1, operandID=24, expressionValue='Ship')
        eTgtAttr = self.ef.make(2, operandID=22, expressionAttributeID=9)
        eOptr = self.ef.make(3, operandID=21, expressionValue='PostPercent')
        self.eSrcAttr = self.ef.make(4, operandID=22, expressionAttributeID=327)
        eTgtSpec = self.ef.make(5, operandID=12, arg1=eTgt['expressionID'], arg2=eTgtAttr['expressionID'])
        self.eOptrTgt = self.ef.make(6, operandID=31, arg1=eOptr['expressionID'], arg2=eTgtSpec['expressionID'])
        self.stub = self.ef.make(7, operandID=27, expressionValue='1')

    def testPre(self):
        eAddMod = self.ef.make(8, operandID=6, arg1=self.eOptrTgt['expressionID'], arg2=self.eSrcAttr['expressionID'])
        modifiers, status = self.runBuilder(eAddMod['expressionID'], self.stub['expressionID'], 0)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)

    def testPost(self):
        eRmMod = self.ef.make(8, operandID=58, arg1=self.eOptrTgt['expressionID'], arg2=self.eSrcAttr['expressionID'])
        modifiers, status = self.runBuilder(self.stub['expressionID'], eRmMod['expressionID'], 0)
        self.assertEqual(status, EffectBuildStatus.okPartial)
        self.assertEqual(len(modifiers), 0)
        self.assertEqual(len(self.log), 1)
