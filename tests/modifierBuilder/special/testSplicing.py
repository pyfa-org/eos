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


class TestSplicing(ModBuilderTestCase):
    """Test parsing of trees describing joins of multiple operations applied onto items"""

    def testBuildSuccess(self):
        eTgtLoc = self.ef.make(1, operandId=24, expressionValue='Target')
        eTgtSrq = self.ef.make(2, operandId=29, expressionTypeId=3300)
        eTgtAttr1 = self.ef.make(3, operandId=22, expressionAttributeId=54)
        eTgtAttr2 = self.ef.make(4, operandId=22, expressionAttributeId=158)
        eTgtAttr3 = self.ef.make(5, operandId=22, expressionAttributeId=160)
        eOptr = self.ef.make(6, operandId=21, expressionValue='PostPercent')
        eSrcAttr1 = self.ef.make(7, operandId=22, expressionAttributeId=351)
        eSrcAttr2 = self.ef.make(8, operandId=22, expressionAttributeId=349)
        eSrcAttr3 = self.ef.make(9, operandId=22, expressionAttributeId=767)
        eTgtItms = self.ef.make(10, operandId=49, arg1Id=eTgtLoc['expressionId'], arg2Id=eTgtSrq['expressionId'])
        eTgtSpec1 = self.ef.make(11, operandId=12, arg1Id=eTgtItms['expressionId'], arg2Id=eTgtAttr1['expressionId'])
        eTgtSpec2 = self.ef.make(12, operandId=12, arg1Id=eTgtItms['expressionId'], arg2Id=eTgtAttr2['expressionId'])
        eTgtSpec3 = self.ef.make(13, operandId=12, arg1Id=eTgtItms['expressionId'], arg2Id=eTgtAttr3['expressionId'])
        eOptrTgt1 = self.ef.make(14, operandId=31, arg1Id=eOptr['expressionId'], arg2Id=eTgtSpec1['expressionId'])
        eOptrTgt2 = self.ef.make(15, operandId=31, arg1Id=eOptr['expressionId'], arg2Id=eTgtSpec2['expressionId'])
        eOptrTgt3 = self.ef.make(16, operandId=31, arg1Id=eOptr['expressionId'], arg2Id=eTgtSpec3['expressionId'])
        eAddMod1 = self.ef.make(17, operandId=9, arg1Id=eOptrTgt1['expressionId'], arg2Id=eSrcAttr1['expressionId'])
        eAddMod2 = self.ef.make(18, operandId=9, arg1Id=eOptrTgt2['expressionId'], arg2Id=eSrcAttr2['expressionId'])
        eAddMod3 = self.ef.make(19, operandId=9, arg1Id=eOptrTgt3['expressionId'], arg2Id=eSrcAttr3['expressionId'])
        eRmMod1 = self.ef.make(20, operandId=61, arg1Id=eOptrTgt1['expressionId'], arg2Id=eSrcAttr1['expressionId'])
        eRmMod2 = self.ef.make(21, operandId=61, arg1Id=eOptrTgt2['expressionId'], arg2Id=eSrcAttr2['expressionId'])
        eRmMod3 = self.ef.make(22, operandId=61, arg1Id=eOptrTgt3['expressionId'], arg2Id=eSrcAttr3['expressionId'])
        eAddSplice1 = self.ef.make(23, operandId=17, arg1Id=eAddMod1['expressionId'], arg2Id=eAddMod3['expressionId'])
        eAddSplice2 = self.ef.make(24, operandId=17, arg1Id=eAddMod2['expressionId'], arg2Id=eAddSplice1['expressionId'])
        eRmSplice1 = self.ef.make(25, operandId=17, arg1Id=eRmMod1['expressionId'], arg2Id=eRmMod3['expressionId'])
        eRmSplice2 = self.ef.make(26, operandId=17, arg1Id=eRmMod2['expressionId'], arg2Id=eRmSplice1['expressionId'])
        modifiers, status = self.runBuilder(eAddSplice2['expressionId'], eRmSplice2['expressionId'], 0)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 3)
        self.assertEqual(len(self.log), 0)
