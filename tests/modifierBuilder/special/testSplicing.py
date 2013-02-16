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
        eTgtLoc = self.ef.make(1, operandID=24, expressionValue='Target')
        eTgtSrq = self.ef.make(2, operandID=29, expressionTypeID=3300)
        eTgtAttr1 = self.ef.make(3, operandID=22, expressionAttributeID=54)
        eTgtAttr2 = self.ef.make(4, operandID=22, expressionAttributeID=158)
        eTgtAttr3 = self.ef.make(5, operandID=22, expressionAttributeID=160)
        eOptr = self.ef.make(6, operandID=21, expressionValue='PostPercent')
        eSrcAttr1 = self.ef.make(7, operandID=22, expressionAttributeID=351)
        eSrcAttr2 = self.ef.make(8, operandID=22, expressionAttributeID=349)
        eSrcAttr3 = self.ef.make(9, operandID=22, expressionAttributeID=767)
        eTgtItms = self.ef.make(10, operandID=49, arg1=eTgtLoc['expressionID'], arg2=eTgtSrq['expressionID'])
        eTgtSpec1 = self.ef.make(11, operandID=12, arg1=eTgtItms['expressionID'], arg2=eTgtAttr1['expressionID'])
        eTgtSpec2 = self.ef.make(12, operandID=12, arg1=eTgtItms['expressionID'], arg2=eTgtAttr2['expressionID'])
        eTgtSpec3 = self.ef.make(13, operandID=12, arg1=eTgtItms['expressionID'], arg2=eTgtAttr3['expressionID'])
        eOptrTgt1 = self.ef.make(14, operandID=31, arg1=eOptr['expressionID'], arg2=eTgtSpec1['expressionID'])
        eOptrTgt2 = self.ef.make(15, operandID=31, arg1=eOptr['expressionID'], arg2=eTgtSpec2['expressionID'])
        eOptrTgt3 = self.ef.make(16, operandID=31, arg1=eOptr['expressionID'], arg2=eTgtSpec3['expressionID'])
        eAddMod1 = self.ef.make(17, operandID=9, arg1=eOptrTgt1['expressionID'], arg2=eSrcAttr1['expressionID'])
        eAddMod2 = self.ef.make(18, operandID=9, arg1=eOptrTgt2['expressionID'], arg2=eSrcAttr2['expressionID'])
        eAddMod3 = self.ef.make(19, operandID=9, arg1=eOptrTgt3['expressionID'], arg2=eSrcAttr3['expressionID'])
        eRmMod1 = self.ef.make(20, operandID=61, arg1=eOptrTgt1['expressionID'], arg2=eSrcAttr1['expressionID'])
        eRmMod2 = self.ef.make(21, operandID=61, arg1=eOptrTgt2['expressionID'], arg2=eSrcAttr2['expressionID'])
        eRmMod3 = self.ef.make(22, operandID=61, arg1=eOptrTgt3['expressionID'], arg2=eSrcAttr3['expressionID'])
        eAddSplice1 = self.ef.make(23, operandID=17, arg1=eAddMod1['expressionID'], arg2=eAddMod3['expressionID'])
        eAddSplice2 = self.ef.make(24, operandID=17, arg1=eAddMod2['expressionID'], arg2=eAddSplice1['expressionID'])
        eRmSplice1 = self.ef.make(25, operandID=17, arg1=eRmMod1['expressionID'], arg2=eRmMod3['expressionID'])
        eRmSplice2 = self.ef.make(26, operandID=17, arg1=eRmMod2['expressionID'], arg2=eRmSplice1['expressionID'])
        modifiers, status = self.runBuilder(eAddSplice2['expressionID'], eRmSplice2['expressionID'], 0)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 3)
        self.assertEqual(len(self.log), 0)
