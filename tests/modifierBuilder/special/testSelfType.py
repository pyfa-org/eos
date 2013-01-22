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


from eos.const import EffectBuildStatus, FilterType, InvType
from eos.tests.modifierBuilder.modBuilderTestCase import ModBuilderTestCase


class TestSelfType(ModBuilderTestCase):
    """Test parsing of trees describing modification which contains reference to typeID of its carrier"""

    def testBuildSuccess(self):
        eTgtOwn = self.ef.make(1, operandId=24, expressionValue='Char')
        eSelf = self.ef.make(2, operandId=24, expressionValue='Self')
        eSelfType = self.ef.make(3, operandId=36, arg1Id=eSelf['expressionId'])
        eTgtAttr = self.ef.make(4, operandId=22, expressionAttributeId=64)
        eOptr = self.ef.make(5, operandId=21, expressionValue='PostPercent')
        eSrcAttr = self.ef.make(6, operandId=22, expressionAttributeId=292)
        eTgtItms = self.ef.make(7, operandId=49, arg1Id=eTgtOwn['expressionId'], arg2Id=eSelfType['expressionId'])
        eTgtSpec = self.ef.make(8, operandId=12, arg1Id=eTgtItms['expressionId'], arg2Id=eTgtAttr['expressionId'])
        eOptrTgt = self.ef.make(9, operandId=31, arg1Id=eOptr['expressionId'], arg2Id=eTgtSpec['expressionId'])
        eAddMod = self.ef.make(10, operandId=11, arg1Id=eOptrTgt['expressionId'], arg2Id=eSrcAttr['expressionId'])
        eRmMod = self.ef.make(11, operandId=62, arg1Id=eOptrTgt['expressionId'], arg2Id=eSrcAttr['expressionId'])
        modifiers, status = self.runBuilder(eAddMod['expressionId'], eRmMod['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.filterType, FilterType.skill)
        self.assertEqual(modifier.filterValue, InvType.self_)
        self.assertEqual(len(self.log), 0)
