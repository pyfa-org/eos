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


from eos.const.eos import EffectBuildStatus
from eos.const.eve import EffectCategory, Operand
from eos.tests.modifierBuilder.modBuilderTestCase import ModBuilderTestCase


class TestSplicing(ModBuilderTestCase):
    """Test parsing of trees describing joins of multiple operations applied onto items"""

    def testBuildSuccess(self):
        eTgtLoc = self.ef.make(1, operandID=Operand.defLoc, expressionValue='Target')
        eTgtSrq = self.ef.make(2, operandID=Operand.defType, expressionTypeID=3300)
        eTgtAttr1 = self.ef.make(3, operandID=Operand.defAttr, expressionAttributeID=54)
        eTgtAttr2 = self.ef.make(4, operandID=Operand.defAttr, expressionAttributeID=158)
        eTgtAttr3 = self.ef.make(5, operandID=Operand.defAttr, expressionAttributeID=160)
        eOptr = self.ef.make(6, operandID=Operand.defOptr, expressionValue='PostPercent')
        eSrcAttr1 = self.ef.make(7, operandID=Operand.defAttr, expressionAttributeID=351)
        eSrcAttr2 = self.ef.make(8, operandID=Operand.defAttr, expressionAttributeID=349)
        eSrcAttr3 = self.ef.make(9, operandID=Operand.defAttr, expressionAttributeID=767)
        eTgtItms = self.ef.make(10, operandID=Operand.locSrq, arg1=eTgtLoc['expressionID'], arg2=eTgtSrq['expressionID'])
        eTgtSpec1 = self.ef.make(11, operandID=Operand.itmAttr, arg1=eTgtItms['expressionID'], arg2=eTgtAttr1['expressionID'])
        eTgtSpec2 = self.ef.make(12, operandID=Operand.itmAttr, arg1=eTgtItms['expressionID'], arg2=eTgtAttr2['expressionID'])
        eTgtSpec3 = self.ef.make(13, operandID=Operand.itmAttr, arg1=eTgtItms['expressionID'], arg2=eTgtAttr3['expressionID'])
        eOptrTgt1 = self.ef.make(14, operandID=Operand.optrTgt, arg1=eOptr['expressionID'], arg2=eTgtSpec1['expressionID'])
        eOptrTgt2 = self.ef.make(15, operandID=Operand.optrTgt, arg1=eOptr['expressionID'], arg2=eTgtSpec2['expressionID'])
        eOptrTgt3 = self.ef.make(16, operandID=Operand.optrTgt, arg1=eOptr['expressionID'], arg2=eTgtSpec3['expressionID'])
        eAddMod1 = self.ef.make(17, operandID=Operand.addLocSrqMod, arg1=eOptrTgt1['expressionID'], arg2=eSrcAttr1['expressionID'])
        eAddMod2 = self.ef.make(18, operandID=Operand.addLocSrqMod, arg1=eOptrTgt2['expressionID'], arg2=eSrcAttr2['expressionID'])
        eAddMod3 = self.ef.make(19, operandID=Operand.addLocSrqMod, arg1=eOptrTgt3['expressionID'], arg2=eSrcAttr3['expressionID'])
        eRmMod1 = self.ef.make(20, operandID=Operand.rmLocSrqMod, arg1=eOptrTgt1['expressionID'], arg2=eSrcAttr1['expressionID'])
        eRmMod2 = self.ef.make(21, operandID=Operand.rmLocSrqMod, arg1=eOptrTgt2['expressionID'], arg2=eSrcAttr2['expressionID'])
        eRmMod3 = self.ef.make(22, operandID=Operand.rmLocSrqMod, arg1=eOptrTgt3['expressionID'], arg2=eSrcAttr3['expressionID'])
        eAddSplice1 = self.ef.make(23, operandID=Operand.splice, arg1=eAddMod1['expressionID'], arg2=eAddMod3['expressionID'])
        eAddSplice2 = self.ef.make(24, operandID=Operand.splice, arg1=eAddMod2['expressionID'], arg2=eAddSplice1['expressionID'])
        eRmSplice1 = self.ef.make(25, operandID=Operand.splice, arg1=eRmMod1['expressionID'], arg2=eRmMod3['expressionID'])
        eRmSplice2 = self.ef.make(26, operandID=Operand.splice, arg1=eRmMod2['expressionID'], arg2=eRmSplice1['expressionID'])
        modifiers, status = self.runBuilder(eAddSplice2['expressionID'], eRmSplice2['expressionID'], EffectCategory.passive)
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 3)
        self.assertEqual(len(self.log), 0)
